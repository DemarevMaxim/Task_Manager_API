from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"
class TaskShortResponse(BaseModel):
    id: int
    title: str
    status: str
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    tasks: list[TaskShortResponse]
    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    category_id: int
class CategoryResponse(BaseModel):
    id: int
    name: str
    
    tasks: list[TaskShortResponse] | None = []    
    class Config:
        from_attributes = True
class TaskResponse(BaseModel):
    id: int
    title: str
    status: str
    owner: UserResponse
    category: Optional [CategoryResponse] = None

    class Config:
        from_attributes = True
class CategoryCreate(BaseModel):
    name: str
class TaskUpdate(BaseModel):
    title: str | None = None
    category_id: int | None = None

