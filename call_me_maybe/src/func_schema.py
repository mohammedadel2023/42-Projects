from typing import Dict, Literal
from pydantic import BaseModel


class ParameterType(BaseModel):
    """
    pydantic class to provide a schema for the
    parameter section inside the func definition
    json file
    """

    type: Literal["number", "string", "boolean", "integer"]


class FunctionSchema(BaseModel):
    """
    pydantic class to provide a schema for the
    function difinition json file.
    """
    name: str
    description: str
    parameters: Dict[str, ParameterType]
    returns: ParameterType


class PromptSchema(BaseModel):
    """
    pydantic class to provide a schema for the
    user prompts json file.
    """

    prompt: str
