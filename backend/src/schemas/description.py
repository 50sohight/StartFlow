from pydantic import BaseModel
from .project import ProjectForDescription


class ML_request(BaseModel):
    documents:ProjectForDescription
    temperature: int
    top_k: int
    max_tokens: int