import pickle
import bm25s
from .helper import (MinimalSource, UnansweredQuestion,
                     MinimalSearchResults, retrieval_type)
from typing import Any
from pydantic import model_validator, Field, BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os


def list_normalize(lst: list[int | float]) -> list[float]:
    """
    Normalizes a list of numerical values linearly to a scale of [0, 10].
    """
    if not lst:
        return []

    data_min = min(lst)
    data_max = max(lst)

    if data_max == data_min:
        return [0.0 for _ in lst]

    return [((x - data_min) / (data_max - data_min)) * 10.0 for x in lst]


def get_top_chunk(k: int, bm25_ids: list[int | float] = None,
                  bm25_scores: list[int | float] = None,
                  faiss_ids: list[int | float] = None,
                  faiss_scores: list[int | float] = None
                  ) -> dict[int, float]:
    chunk_scores = dict()
    # print(f"the faiss socres is :\n{faiss_scores} -> on ids\n {faiss_ids}")
    # print(f"the bm25 socres is :\n{bm25_scores} -> on ids\n {bm25_ids}")
    if len(bm25_ids) > 0:
        for id in bm25_ids:
            chunk_scores[id] = 0
        if len(faiss_ids) > 0:
            bm25_scores = list_normalize(bm25_scores)
    if len(faiss_ids) > 0:
        for id in faiss_ids:
            chunk_scores[id] = 0
        if len(bm25_ids) > 0:
            faiss_scores = list_normalize(faiss_scores)
    for id in chunk_scores.keys():
        score = 0
        if id in bm25_ids:
            bm_idx = bm25_ids.index(id)
            score += bm25_scores[bm_idx] * 1
        if id in faiss_ids:
            faiss_idx = faiss_ids.index(id)
            score += faiss_scores[faiss_idx] * 0.75
        chunk_scores[id] = score
    sorted_chunks = sorted(chunk_scores.items(),
                           key=lambda item: item[1], reverse=True)[:k]
    return dict(sorted_chunks)


class retriever(BaseModel):
    """
    This function handel the retrueving process.

    bm25model (Any): model using to find the bm25 between chunks and query.
    chunks_lookup (dict[int, MinimalSource]): chunks lookup used to access
                                              the chunks
    """

    bm25model: Any = Field(default=None)
    chunks_lookup: dict[int, MinimalSource] = Field(default_factory=dict)
    faiss_model: Any = Field(default=None)
    t: retrieval_type = retrieval_type.Bm25
    embedding_model: Any = Field(default=None)

    @model_validator(mode='after')
    def _run_post_init(self,
                       ) -> "retriever":
        if self.t == retrieval_type.Bm25:
            if not (self.bm25model and self.chunks_lookup):
                if not (os.path.isfile("data/processed/chunks_lookup.pkl") and
                        os.path.isfile("data/processed/retriever.pkl")):
                    from .utils.cli import do_index_handler
                    do_index_handler()
                self.load()
        else:
            if not (self.bm25model and self.chunks_lookup and
                    self.faiss_model):
                if not (os.path.isfile("data/processed/chunks_lookup.pkl") and
                        os.path.isfile("data/processed/retriever.pkl") and
                        os.path.isfile(
                            "data/processed/embedding_index.faiss")):
                    from .utils.cli import do_index_handler
                    do_index_handler(faiss_index=True)
                self.load(self.t)

        return self

    def load(self, t: retrieval_type = retrieval_type.Bm25) -> None:
        """
        This func load the required args from thier files
        """
        with open("data/processed/retriever.pkl", "rb") as f:
            self.bm25model = pickle.load(f)["bm25_model"]
        with open("data/processed/chunks_lookup.pkl", "rb") as f:
            self.chunks_lookup = pickle.load(f)
        if t != retrieval_type.Bm25:
            self.faiss_model = faiss.read_index(
                r"data/processed/embedding_index.faiss")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2',
                                                       device='cpu')

    def query(self,
              query_txt: str,
              q_id: str | None = None,
              k: int = 2,
              t: retrieval_type | str | None = None
              ) -> MinimalSearchResults:
        """
        Takes the user query and finds the closest chunks using BM25, FAISS,
        or both.
        """

        target_t = t if t is not None else self.t

        if hasattr(target_t, "value"):
            t_str = str(target_t.value).lower()
        else:
            t_str = str(target_t).lower()

        use_bm25 = t_str in ("bm25", "both")
        use_faiss = t_str in ("faiss", "both")
        if not q_id:
            q = UnansweredQuestion(
                question=query_txt
            )
        else:
            q = UnansweredQuestion(
                        question_id=q_id,
                        question=query_txt
            )
        bm25_ids = []
        bm25_scores = []
        faiss_ids = []
        faiss_scores = []
        if use_bm25:
            ids, scores = self.bm25model.retrieve(
                bm25s.tokenize(q.question), k=(k ** 2) * 2)
            for i, ids in enumerate(ids[0]):
                bm25_ids.append(ids)
                bm25_scores.append(scores[0][i])
        if use_faiss:
            raw_emb = self.embedding_model.encode(q.question)
            q_emb = np.array([raw_emb], dtype=np.float32)
            faiss.normalize_L2(q_emb)
            scores_mat, ids_mat = self.faiss_model.search(q_emb, (k ** 2) * 2)
            faiss_scores = [float(s) for s in scores_mat[0] if s != -1]
            faiss_ids = [int(i) for i in ids_mat[0] if i != -1]
        # print(bm25_ids, bm25_scores, faiss_ids, faiss_scores)
        top_chunks = get_top_chunk(k, bm25_ids, bm25_scores, faiss_ids,
                                   faiss_scores)
        res_minimal_source = []
        res_scores = []
        for chunk_id, score in top_chunks.items():
            orig_chunk = self.chunks_lookup[chunk_id]
            clean_chunk = orig_chunk.model_copy(update={"embedding": None})
            res_minimal_source.append(clean_chunk)
            res_scores.append(float(score))
        return MinimalSearchResults(
            question_id=q.question_id,
            question=q.question,
            retrieved_sources=res_minimal_source,
            scores=res_scores
        )
