from langchain_community.document_loaders import PythonLoader, TextLoader
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_core.documents.base import Document
from pydantic import BaseModel, Field
from ..helper import chunk_types
from tqdm import tqdm
import os


class chunker(BaseModel):
    """
    This class will be responsible to chunk all srouce file
    (.py, .md, .txt)

    Args:
        files_type (chunk_types): The type of file to chunk.
        max_chunk_size  (int): The max number of char's in each chunk.
        new_after_n_chars (int): Chunks with more than this number will
                                stop extending using other partitions elements.
        overlap (int): only when using text-splitting (when the elements of
                     partitions is greater than the chunk size)
        source (list[str]): a list of file paths
    """
    files_type: chunk_types
    max_chunk_size: int = Field(default=2000, le=2000)
    overlap: int = 200
    sources: list[str]

    def do_chunk(self) -> list[list[Document] | None]:
        """
        this function start chunking the file in the source

        Returns:
            list[list[Document] | None]: each el in the outer list represent
                                         the output of chunking one file
        """
        docs_list = []
        if self.files_type == chunk_types.Doc:
            for file in tqdm(self.sources,
                             desc="start indexing the DOC files"):
                docs = self.chunk_txt(file_path=file)
                docs_list.append(docs)
        else:
            for file in tqdm(self.sources,
                             desc="start indexing the CODE files"):
                docs = self.chunk_code(file_path=file)
                docs_list.append(docs)
        return docs_list

    def chunk_txt(self, file_path: str) -> list[Document] | None:
        """
        This func include the technique to chunk a txt, md files

        Returns:
            list[Document] | None: list of Document include the chunk data
        """
        try:
            _, ext = os.path.splitext(file_path)
            if ext == ".md":
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language.MARKDOWN,
                    chunk_size=self.max_chunk_size,
                    chunk_overlap=self.overlap,
                    add_start_index=True
                )
            elif ext == ".txt":
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.max_chunk_size,
                    chunk_overlap=self.overlap,
                    add_start_index=True
                )
            else:
                return None

            loader = TextLoader(file_path)
            doc = loader.load()
            file_chunks = splitter.split_documents(doc)
            return file_chunks
        except Exception:
            return None

    def chunk_code(self, file_path: str) -> list[Document] | None:
        """
            This func include the technique to chunk a .py, .sh files

        Returns:
            list[Document] | None: list of Document include the chunk data
        """
        try:
            loader = PythonLoader(file_path=file_path)
            doc = loader.load()
            python_splitter = RecursiveCharacterTextSplitter.from_language(
                language=Language.PYTHON,
                chunk_size=self.max_chunk_size,
                add_start_index=True
            )
            docs = python_splitter.split_documents(doc)
            return docs
        except Exception as e:
            print(f"error: {e}")
            return None
