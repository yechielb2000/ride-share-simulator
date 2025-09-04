from pydantic import BaseModel


class ClockConfig(BaseModel):
    advance_delta_seconds: int = 1
