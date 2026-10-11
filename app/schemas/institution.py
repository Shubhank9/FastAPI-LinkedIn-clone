from pydantic import BaseModel, ConfigDict


class InstitutionResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True
    )
