from pydantic import BaseModel


class DoubleDownRestrictions(BaseModel):
  first_two_cards_only: bool
  allow_after_split: bool
  nine_ten_eleven_only: bool
