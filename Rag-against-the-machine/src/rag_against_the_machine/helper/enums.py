from enum import Enum


class chunk_types(Enum):
    """
    Enums define the tpye of allowd chunking
    plicies
    """

    Code = "code"
    Doc = "doc"


class allowed_file_type(Enum):
    """
    Enums define the tpye of allowd file type to chunk
    """

    TXT = ".txt"
    CODE = ".py"
    MD = ".md"
    BASH = ".sh"


class llm_engin(Enum):
    """
    Enums define the available engine to use llm through
    """
    llama = "llama"
    transformers = "transformers"
