from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class SkillUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class SkillRead(ORMBase):
    id: int
    name: str
    created_at: datetime


class UserSkillUpsert(BaseModel):
    skill_id: int
    proficiency: int = Field(ge=0, le=100)


class UserSkillRead(ORMBase):
    skill: SkillRead
    proficiency: int
    created_at: datetime


class TeamMembershipCreate(BaseModel):
    user_id: int
    role: str = Field(min_length=1, max_length=60)


class TeamMembershipUpdate(BaseModel):
    role: str = Field(min_length=1, max_length=60)


class TeamMemberUserRead(ORMBase):
    id: int
    email: str
    full_name: str


class TeamMembershipRead(ORMBase):
    user: TeamMemberUserRead
    role: str
    joined_at: datetime


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    status: str = Field(default="todo", min_length=1, max_length=50)
    due_date: datetime | None = None
    team_id: int
    sort_order: int = 0


class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    status: str = Field(min_length=1, max_length=50)
    due_date: datetime | None = None
    sort_order: int = 0


class TaskRead(ORMBase):
    id: int
    title: str
    status: str
    created_at: datetime
    due_date: datetime | None
    team_id: int
    sort_order: int


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    project_id: int


class TeamUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class TeamRead(ORMBase):
    id: int
    name: str
    created_at: datetime
    project_id: int


class TeamDetail(TeamRead):
    memberships: list[TeamMembershipRead]
    tasks: list[TaskRead]


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    deadline: datetime | None = None


class ProjectUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    deadline: datetime | None = None


class ProjectRead(ORMBase):
    id: int
    title: str
    description: str
    created_at: datetime
    deadline: datetime | None
    owner_id: int


class ProjectDetail(ProjectRead):
    teams: list[TeamDetail]

