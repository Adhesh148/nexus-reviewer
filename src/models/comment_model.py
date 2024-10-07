from pydantic import BaseModel, Field
from typing import Optional
from github.File import File

class CommentModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    body: str = Field(None, description="Body of review comment")
    subject_type: str = Field(None, description="Type of comment. Either line or file")
    line: Optional[int] = Field(None, description="The last line number in the patch where the comment applies")
    file: File = Field(None, description="File corresponding to the comment")