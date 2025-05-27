from pydantic import BaseModel


# TODO: Implement real rules
class SurrenderRules(BaseModel):
  surrender_allowed: bool
