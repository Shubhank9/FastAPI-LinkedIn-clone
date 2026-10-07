from pydantic import BaseModel, ConfigDict, Field


class SkillCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )


class SkillResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True
    )


class UserSkillCreate(BaseModel):
    skill_id: int