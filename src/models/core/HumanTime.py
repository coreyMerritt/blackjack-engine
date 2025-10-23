from pydantic import BaseModel


class HumanTime(BaseModel):
  hands_per_hour: int
  hours_per_day: int
  days_per_week: int
