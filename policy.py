from abc import ABC, abstractmethod

class RummyPolicy(ABC):
  '''The abstract class for the policy needed for Rummy'''

  # NOTE: during concrete implementation, PLEASE treat the Card objects from "hand" arguments by-reference,
  # i.e. don't mess them up and please return the Card objects the same references as they as passed in,
  # instaed of potentially passing back new cards. The game logic requires by-reference logic to work.
  # Takes some effort to transform to suit/rank comparison instead of reference comparison at the moment.

  def clear_cache(self):
    '''Clears the cache in-between rounds, like state-dictionaries, etc.'''
    pass  # default is to do nothing. Can optionally overwrite.

  @abstractmethod
  def draw(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, meld_turn_count, melds):
    '''
      The draw policy for rummy.
      Input:
        hand: List[Card] - the current hand of this player; note these Cards are by reference.
        player_index: int - the player index to access the stat of the player in a multi-player list.
        scores: List[int] - the game scores of all existing players in the game.
        num_cards_in_hands: List[int] - the number of cards in the hand of each player, indexed by player_index
        discard_pile_top_card: Card - topmost visible card of the discard pile
        num_cards_stock_pile: int - number of cards left in the stock pile
        num_turnover: int - number of times the stock piles have been turned over so far. Game ends at final burnthough.
        meld_turn_count: List[int] - numbers of turns where melding is used for all existing player in the game.
        melds: List[Tuple(List[Card], String)] - all melds on the table, each in the manner of (all cards in the meld, meld's type).
                                                  meld's type is either "n_of_a_kind" or "same_suit_seq"
      Output:
        String - either "stock" or "discard", indicating the pile the player is drawing the card from for this turn.         
    '''
    pass

  @abstractmethod
  def discard(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, card_drawn_from_discard_pile, meld_turn_count, melds):
    '''
      The meld and discard policy for rummy.
      Input:
        hand: List[Card] - the current hand of this player; note these Cards are by reference.
        player_index: int - the player index to access the stat of the player in a multi-player list.
        scores: List[int] - the game scores of all existing players in the game.
        num_cards_in_hands: List[int] - the number of cards in the hand of each player, indexed by player_index
        discard_pile_top_card: Card or None - topmost visible card of the discard pile
        num_cards_stock_pile: int - number of cards left in the stock pile
        card_drawn_from_discard_pile: None or Card - the same Card grabbed from the top of the discard pile in same turn's draw, else None.
                                                     Enforces the rule that the player can't discard this card in the same turn.
        meld_turn_count: List[int] - numbers of turns where melding is used for all existing player in the game.
        melds: List[Tuple(List[Card], String)] - all melds on the table, each in the manner of (all cards in the meld, meld's type).
                                                  meld's type is either "n_of_a_kind" or "same_suit_seq"
      Output:
        List[Card], List[Tuple(List[Card], String or int])] - indicates the choices and purposes of cards for discard and meld
                                                                The first output should only contain ONE card, which is the card to discard from
                                                                the current hand of this player.
                                                                The second output is a list of meld choices. Each tuple's first component is
                                                                the list of cards to use for the second component's purpose, which is either
                                                                "new" referring to adding a new meld (matched set) to the table, or an integer
                                                                index in the range [0, num_melds) indicating to appending the corresponding set
                                                                of cards to the meld already on the table at that index.
    '''
    pass

