from pydantic import BaseModel, EmailStr


class BaseResponse(BaseModel):
    # may define additional fields or config shared across responses
    class Config:
        orm_mode = True


class AccessTokenResponse(BaseResponse):
    token_type: str
    access_token: str
    expires_at: int
    issued_at: int
    refresh_token: str
    refresh_token_expires_at: int
    refresh_token_issued_at: int


class UserResponse(BaseResponse):
    id: str
    email: EmailStr


class DepartmentResponse(BaseResponse):
    id: str
    sigaa_id: int
    acronym: str
    title: str


class ProgramResponse(BaseResponse):
    id: str
    sigaa_id: int
    title: str
    degree: str | None
    shift: str | None
    department_id: str


class CurriculumResponse(BaseResponse):
    id: int
    sigaa_id: str
    active: bool
    start_year: int
    start_period: int
    min_periods: int
    max_periods: int
    min_period_workload: int
    max_period_workload: int
    min_workload: int
    mandatory_components_workload: int
    min_elective_components_workload: int
    max_elective_components_workload: int
    min_complementary_components_workload: int
    max_complementary_components_workload: int

    program_id: int
