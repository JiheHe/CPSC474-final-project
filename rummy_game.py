'''Discretizes the rummy game into MCTS-processible parts. Note Rummy is NOT a perfect information game.'''

from rummy import Game as Rummy
from game import State
from deck import Deck
import copy
import random

class GameState(State):
  '''A state in the Rummy Game, granularity to be defined-
    We have 4 levels of granularity we can choose to model our MCTS, similarly commented in the rummy.py file:
    1. Finest Granularity, move of one player in a turn. 
    2. Medium Granularity, moves of all players in a circle of turns. 
    3. Coarse Granularity, playing out a whole round of the game (multiple circles of turns).
    4. Coarest Granularity, playing out the whole game once (multiple rounds).

    We know opponent's strategy.
    [assuming optimal you and player?]
    [optimal you only, feeding in player stratgy?]
    TODO: make a decision, and implement this.
  '''

  def __init__(self, game, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, meld_turn_count, melds):
    # These information are related to the current turn of the player, inherited from Policy
    self.game = game  # perfection information instance currently, not fair; need some masking to simulate the unknowing state.

    # this is for playout only.
    # simulate a bad player that DOESN'T TRACK CARDS. NOTE: potentially improvement: a belief table that does
    hand_info = copy.copy(hand)  # shallow copy of obj ref
    meld_info = [card for meld_set in melds for card in meld_set[0]]
    existing_cards = hand_info + meld_info  # don't overlap
    self.reconstructed_stock = Deck(self.game.ALL_RANKS, self.game.ALL_SUITS, 1)
    i = 0
    while i < len(self.reconstructed_stock._cards):  # remove the viewable, existing possibilities from the deck
      existed = False
      for j in range(len(existing_cards)):
        if self.reconstructed_stock._cards[i].same_suit(existing_cards[j]) and self.reconstructed_stock._cards[i].same_rank(existing_cards[j]):
          existing_cards.pop(j)
          existed = True
          break
      if existed:
        self.reconstructed_stock._cards.pop(i)
      else:
        i += 1
      if len(existing_cards) == 0:
        break
    self.reconstructed_stock._cards = random.choices(self.reconstructed_stock._cards, k=num_cards_stock_pile) # select



    self.hand = hand
    self.player_index = player_index
    self.scores = scores
    self.num_cards_in_hands = num_cards_in_hands
    self.discard_pile_top_card = discard_pile_top_card
    self.num_cards_stock_pile = num_cards_stock_pile
    self.num_turnover = num_turnover
    self.meld_turn_count = meld_turn_count
    self.melds = melds

  def is_terminal(self, hands, num_turnover, stock):
    """ Determines if this state is terminal.  Return value is true is so and false otherwise.

        self -- a state depending on externel information
    """
    return self.game.round_ends(hands) or self.game.tie(num_turnover[0], stock.size())

  def payoff(self):
    """ Returns the payoff for player 0 at this terminal state.

        self -- a terminal state
    """
    pass

  def actor(self):
    """ Determines which player is the actor in this nonterminal state.

        self -- a nonterminal state
    """
    pass

  def get_actions(self):
    """ Returns a list of possible actions in this nonterminal state.
        The representation of each state is left to the implementation.

        self -- a nonterminal state
    """
    pass

  def is_legal(self, action):
    """ Determines if the given action is legal in this state.

        self -- a state
        action -- an action
    """
    return False
  
  def successor(self, action):
    """ Returns the state that results from the given action in this nonterminal state.

        self -- a nonterminal state
        action -- one of the actions in the list returned by get_actions for this state
    """
    pass

