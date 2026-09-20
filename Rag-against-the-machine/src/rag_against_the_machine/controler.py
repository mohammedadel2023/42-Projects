from .indexing import indexer
from .helper import chunk_types


def index(root: str = "data/raw") -> None:
    indexer_obj = indexer(root=root)
    indexer_obj.start(t=chunk_types.Doc)
    indexer_obj.start(t=chunk_types.Code)
    indexer_obj.do_save()
