from pydantic import BaseModel


class SurrenderRules(BaseModel):
  early_surrender_allowed: bool
  late_surrender_allowed: bool
