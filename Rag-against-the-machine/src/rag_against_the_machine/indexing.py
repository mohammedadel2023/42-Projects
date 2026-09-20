from pydantic import BaseModel, model_validator, Field
from langchain_core.documents import Document
from .utils import traversal, chunker
from .helper import chunk_types, MinimalSource
from typing import Optional, Any
import pickle
import bm25s
import os


class indexer(BaseModel):
    """
    This class index all codebase and store it
    making it ready to querying.

    Args:
        root (sre): path for codebase.
        chunk_size (int): the size of the chunk.
        traversal_obj: object of traverser class.
        tree (dict[str, list[str]]): stroe extracted files
        code_tree (list[str]): store all code files
        txt_tree (list[str]): store all doc files.
        indexes (dict[str, list[list[Document] | None]]):
        store fiels based on thier chunking technique.
        chunk_lookup (dict[int, MinimalSource]): used to return the
                                                 chunk based ot it id
    """

    root: str = "data/raw"
    chunk_size: int = Field(default=2000, le=2000)
    traversal_obj: Optional[Any] = Field(default=None, exclude=True)
    tree: dict[str, list[str]] = Field(default_factory=dict)
    code_tree: list[str] = Field(default_factory=list)
    txt_tree: list[str] = Field(default_factory=list)
    indexes: dict[str, list[list[Document] | None]] = Field(
        default_factory=dict)
    chunk_lookup: dict[int, MinimalSource] = Field(default_factory=dict)

    @model_validator(mode='after')
    def _run_post_init(self) -> "indexer":
        traversal_obj = traversal(root=self.root)
        traversal_obj.do()
        self.tree = traversal_obj.filter_and_build()
        self.code_tree = self.tree.get("code", [])
        self.txt_tree = self.tree.get("txt", [])

        return self

    def start(self, t: chunk_types) -> None:
        """
        This func start the indexing logic

        Args:
            t (chunk_types): the type of chunking you want to apply
        """
        if t == chunk_types.Code:
            chunker_obj = chunker(files_type=chunk_types.Code,
                                  sources=self.code_tree,
                                  max_chunk_size=self.chunk_size)
            self.indexes["CODE"] = chunker_obj.do_chunk()
        else:
            chunker_obj = chunker(files_type=chunk_types.Doc,
                                  sources=self.txt_tree,
                                  max_chunk_size=self.chunk_size)
            self.indexes["DOC"] = chunker_obj.do_chunk()

    def build_chunk_lookup(self) -> bool:
        """
        This func build a chunk_lookup to store it using pickle.

        Returns:
            bool: if succeed.
        """
        try:
            if self.chunk_lookup:
                return True
            st_ids = 0
            for t in ["CODE", "DOC"]:
                for file in self.indexes[t]:
                    if isinstance(file, list):
                        for chunk in file:
                            st_index = chunk.metadata["start_index"]
                            min_source = MinimalSource(
                                file_path=chunk.metadata["source"],
                                first_character_index=st_index,
                                last_character_index=(len(chunk.page_content) +
                                                      st_index - 1),
                                content=chunk.page_content)
                            self.chunk_lookup[st_ids] = min_source
                            st_ids += 1
                    else:
                        if isinstance(file, Document):
                            print(f"the file is :{file}, id is :{st_ids}")
                            self.chunk_lookup[st_ids] = file
                            st_ids += 1
            return True
        except Exception as e:
            print("fail to build a lookup dict")
            print(f"error mes: {e}")
            return False

    def do_save(self) -> bool:
        """
        This func save the chunk_lookup file.

        Retunrs:
            bool: if succeed.
        """
        self.build_chunk_lookup()
        try:
            if not os.path.isdir("data/processed"):
                os.mkdir("data/processed")
            with open("data/processed/chunks_lookup.pkl", "wb") as f:
                pickle.dump(self.chunk_lookup, f)
            self.build_bm25_model()
            return True
        except Exception as e:
            print(e)
            return False

    def build_bm25_model(self) -> bool:
        """
        This func build a bm25 model and store it.

        Returns:
            bool: if succeed.
        """
        try:
            corpus = [chunk.content for chunk
                      in self.chunk_lookup.values()]
            retriever = bm25s.BM25()
            retriever.index(bm25s.tokenize(corpus))
            with open("data/processed/retriever.pkl", "wb") as f:
                pickle.dump(
                    {"bm25_model": retriever},
                    f)
            return True
        except Exception as e:
            print(f"error: {e}")
            return False
