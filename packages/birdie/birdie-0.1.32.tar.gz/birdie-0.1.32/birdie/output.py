from pydantic import BaseModel, Field
from typing import List, Any, Optional


class ResultBase(BaseModel):
    name: str = Field(...)


class ResultText(ResultBase):
    type: str = "text"
    content: str = Field(...)


class ResultPDF(ResultBase):
    type: str = "pdf"
    content: str = Field(...)


class ResultImage(ResultBase):
    type: str = "image"
    content: str = Field(...)


class ResultHTML(ResultBase):
    type: str = "html"
    content: str = Field(...)


class ResultModel(BaseModel):
    content: str = Field(...)
    state: Optional[dict] = Field(None)
    parts: Optional[Any] = Field(None)
    step: int = Field(...)
    result: Optional[List[ResultText | ResultPDF | ResultHTML | ResultImage]] = Field([])  # noqa: E501
    final_result: bool = Field(False)
