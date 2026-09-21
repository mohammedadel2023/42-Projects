from pydantic import BaseModel, Field
from typing import List, Optional, Union, Annotated
import uuid


class MinimalSource(BaseModel):
    """pydantic schema for minimal type of source"""
    file_path: str
    first_character_index: int
    last_character_index: int
    content: Optional[str] = None


class UnansweredQuestion(BaseModel):
    """pydantic schema for unanswered question"""
    question_id: str = Field(default_factory=lambda:
                             str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """pydantic schema for answered question"""
    sources: List[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """pydantic schema for rag dataset which include a list of questions"""
    rag_questions: List[Annotated[
                        Union[AnsweredQuestion, UnansweredQuestion],
                        Field(union_mode="left_to_right"),
                        ]]


class MinimalSearchResults(BaseModel):
    """
    pydantic schema include the result of search
    (a question with related sources with thier scores)
    """
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]
    scores: List[float]


class MinimalAnswer(MinimalSearchResults):
    """
    pydantic schema include the result of answer
    (a question with related sources with thier
     scores and the answer based on them)
    """
    answer: str


class StudentSearchResults(BaseModel):
    """
    pydantic schema include the result of search_datasets
    """
    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """
    pydantic schema include the result of answer_datasets
    """
    search_results: List[MinimalAnswer]
    k: int


class Truth_source(BaseModel):
    """
    pydantic schema represent the source file in the truth source
    """
    file_path: str
    first_character_index: int
    last_character_index: int


class Truth_question(BaseModel):
    """
    pydantic schema represent the question in the truth source
    """
    question_id: str
    question: str
    answer: str
    sources: List[Truth_source]
    difficulty: str
    is_valid: bool


class Truth(BaseModel):
    """The truth source list of truth questions"""
    rag_questions: List[Truth_question]
