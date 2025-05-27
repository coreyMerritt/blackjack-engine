from pydantic import BaseModel


class DoubleDownRules(BaseModel):
  double_after_hit: bool
  double_after_split_except_aces: bool
  double_after_split_including_aces: bool
  double_on_ten_eleven_only: bool
  double_on_nine_ten_eleven_only: bool
  double_on_any_two_cards: bool
