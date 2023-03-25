from typing import Literal

from pydantic import BaseModel


class Component(BaseModel):
    sigaa_id: str
    title: str
    type: Literal["COURSE", "ACTIVITY"]
    department_id: int
