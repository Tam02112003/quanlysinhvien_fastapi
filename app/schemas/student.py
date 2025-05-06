from pydantic import BaseModel
from datetime import date
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    email: str
    date_of_birth: date
    class_id: Optional[int]

class StudentOut(StudentCreate):
    id: int
