from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class CodeReviewModel(BaseModel):
    uid: uuid.UUID
    user_id : uuid.UUID = Field(foreign_key = "users.uid")
    title: str
    code_snippet: str
    review: str
    created_at: datetime
    updated_at: datetime 
    
class CodeReviewSubmitModel(BaseModel):
    title: str
    code_snippet: str
    language: str
