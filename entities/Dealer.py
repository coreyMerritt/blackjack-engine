from entities.Player import Player
from entities.Shoe import Shoe
from entities.Card import Card, Face, Suit
from models.core.player_info.PlayerInfo import PlayerInfo
from models.core.rules.DealerRules import DealerRules
from models.enums.PlayerDecision import PlayerDecision


class Dealer(Player):
  __hits_soft_seventeen: bool
  __blackjack_pays_multiplier: float
  __shoe: Shoe

  def __init__(self, rules: DealerRules):
    super().__init__(PlayerInfo(bankroll=4000000000.0))
    self.__hits_soft_seventeen = rules.dealer_hits_soft_seventeen
    self.__blackjack_pays_multiplier = rules.blackjack_pays_multiplier
    self.__shoe = Shoe(rules.deck_count, rules.shoe_reset_percentage)
    self.load_shoe()
    self.shuffle_shoe()

  def get_blackjack_pays_multiplier(self) -> float:
    return self.__blackjack_pays_multiplier

  def get_shoe(self) -> Shoe:
    return self.__shoe

  def get_full_shoe_size(self) -> int:
    return self.__shoe.get_full_size()

  def get_shoe_card_count(self) -> int:
    return self.__shoe.get_card_count()

  def get_shoe_reset_percentage(self) -> int:
    return self.__shoe.get_reset_percentage()

  def get_decks_remaining(self) -> int:
    return self.__shoe.get_decks_remaining()

  def get_facecard(self) -> Card:
    return self.get_hands()[0].get_card(1)

  def draw(self) -> Card:
    return self.__shoe.draw()

  def get_decision(self) -> PlayerDecision:
    if self.get_hand_value(0) == 17:
      if self.get_hands()[0].is_soft():
        if self.__hits_soft_seventeen:
          return PlayerDecision.HIT
        return PlayerDecision.STAND
    if self.get_hand_value(0) >= 17:
      return PlayerDecision.STAND
    else:
      return PlayerDecision.HIT

  def calculate_if_busted(self) -> bool:
    hand = self.get_hand(0)
    if hand.get_value() > 21:
      if not hand.is_soft():
        return True
    return False

  def shuffle_shoe(self) -> None:
    self.__shoe.shuffle()

  def load_shoe(self) -> None:
    shoe_deck_count = self.__shoe.get_deck_count()
    shoe_full_size = self.__shoe.get_full_size()
    self.__shoe.set_cards([])
    for _ in range(shoe_deck_count):
      for suit in Suit:
        for face in Face:
          card = Card(suit, face)
          self.__shoe.add_card(card)
    assert self.__shoe.get_card_count() == shoe_full_size

  def to_dict(self) -> dict:
    return {
      "shoe": self.__shoe.to_dict(),
      "hand": [c.to_dict() for hand in self.get_hands() for c in hand.get_cards()]
    }
