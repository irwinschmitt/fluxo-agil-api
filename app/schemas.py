from pydantic import BaseModel
from enum import Enum


class DepartmentBase(BaseModel):
    sigaa_id: int
    acronym: str
    title: str


class DepartmentCreate(DepartmentBase):
    pass


class Department(DepartmentBase):
    id: int

    class Config:
        orm_mode = True
