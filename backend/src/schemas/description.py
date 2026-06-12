from pydantic import BaseModel

from .project import ProjectForDescription


class ML_request(BaseModel):
    documents: ProjectForDescription
    temperature: float
    top_k: int
    max_tokens: int
