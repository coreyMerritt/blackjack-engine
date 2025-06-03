from pydantic import BaseModel


class HandResultsPercentagesFormatted(BaseModel):
  won: str = ""
  lost: str = ""
  drawn: str = ""
