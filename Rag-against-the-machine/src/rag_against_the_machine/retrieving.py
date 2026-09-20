import pickle
import bm25s
from .controler import index
from .helper import MinimalSource, UnansweredQuestion, MinimalSearchResults
from typing import Any
from pydantic import model_validator, Field, BaseModel
import os


class retriever(BaseModel):
    """
    This function handel the retrueving process.

    bm25model (Any): model using to find the bm25 between chunks and query.
    chunks_lookup (dict[int, MinimalSource]): chunks lookup used to access
                                              the chunks
    """

    bm25model: Any = Field(default=None)
    chunks_lookup: dict[int, MinimalSource] = Field(default_factory=dict)

    @model_validator(mode='after')
    def _run_post_init(self) -> "retriever":
        if not (self.bm25model and self.chunks_lookup):
            if not (os.path.isfile("data/processed/chunks_lookup.pkl") and
                    os.path.isfile("data/processed/retriever.pkl")):
                index()
            self.load()

        return self

    def load(self) -> None:
        """
        This func load the required args from thier files
        """
        with open("data/processed/retriever.pkl", "rb") as f:
            self.bm25model = pickle.load(f)["bm25_model"]
        with open("data/processed/chunks_lookup.pkl", "rb") as f:
            self.chunks_lookup = pickle.load(f)

    def query(self, query_txt: str, q_id: str | None = None,
              k: int = 2) -> MinimalSearchResults:
        """
        This fun take the user query and find the closer chunks to it.

        Args:
            query_txt (str): user question.
            q_id (str | None = None): ID of question.

        Returns:
            MinimalSearchResults: object with MinimalSearchResults schema
        """
        if not q_id:
            q = UnansweredQuestion(
                question=query_txt
            )
        else:
            q = UnansweredQuestion(
                        question_id=q_id,
                        question=query_txt
            )
        ids, scores = self.bm25model.retrieve(
            bm25s.tokenize(q.question), k=k)
        min_source = []
        sc = []
        for i, ids in enumerate(ids[0]):
            min_source.append(self.chunks_lookup[int(ids)])
            sc.append(scores[0][i])
        results = MinimalSearchResults(
                    question_id=q.question_id,
                    question=q.question,
                    retrieved_sources=min_source,
                    scores=sc
                )
        return results
