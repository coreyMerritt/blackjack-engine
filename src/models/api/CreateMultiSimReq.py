from pydantic import BaseModel

from models.api.CreateSingleSimReq import CreateSingleSimReq
from models.core.MultiSimBounds import MultiSimBounds


class CreateMultiSimReq(BaseModel):
  multi: MultiSimBounds
  single: CreateSingleSimReq
