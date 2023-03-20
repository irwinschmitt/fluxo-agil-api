from pydantic import BaseModel, EmailStr


class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class UserUpdatePasswordRequest(BaseRequest):
    password: str


class UserCreateRequest(BaseRequest):
    email: EmailStr
    password: str


class DepartmentCreateRequest(BaseRequest):
    sigaa_id: int
    acronym: str
    title: str


class DepartmentUpdateRequest(BaseRequest):
    acronym: str | None
    title: str | None


class ProgramCreateRequest(BaseRequest):
    sigaa_id: int
    title: str
    degree: str | None = None
    shift: str | None = None
    department_id: int


class CurriculumCreateRequest(BaseRequest):
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
