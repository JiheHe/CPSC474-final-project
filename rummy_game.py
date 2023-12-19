'''Discretizes the rummy game into MCTS-processible parts. Note Rummy is NOT a perfect information game.'''

from rummy import Game as Rummy
from game import State
import copy


class State(State):
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

  def __init__(self, game):
    self.game = game  # game: an ongoing instance of Rummy Game, already initialized.

  def is_terminal(self):
    """ Determines if this state is terminal.  Return value is true is so and false otherwise.

        self -- a state
    """
    pass

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


  def find_all_meldable_sets(self, hand, melds):
    '''
    Input:
      hand: List[Card] - the current hand of this player; note these Cards are by reference.
      melds: List[Tuple(List[Card], String)] - all melds on the table, each in the manner of (all cards in the meld, meld's type).
                                                  meld's type is either "n_of_a_kind" or "same_suit_seq"
    Output:
      List[List[Tuple(List[Card], String)]] - a list of lists such that each list is a set of melding options we can do given our
                                                  current hand, cleared of overlaps. Each meld is a list of cards and a string type.
    '''  
    hand.sort()  # sort hand if not already sorted.
    # NOTE: a shallow copy where each entry is the same reference to the same card, but different lists
    hand1_c = copy.copy(hand)  # three of a kind leftovers
    hand2_c = copy.copy(hand)  # same_suit_seq leftovers

    # split hand into hand1_toak and hand1_c
    i = 0
    hand1_toak = []
    while i <= len(hand1_c)-3:
      consecutive = []
      if hand1_c[i].same_rank(hand1_c[i+1]) and hand1_c[i+1].same_rank(hand1_c[i+2]):  # 3 of a kind
        consecutive.append(hand1_c.pop(i))  # i+1
        consecutive.append(hand1_c.pop(i))  # i+2
        consecutive.append(hand1_c.pop(i))  # i+3
        if i < len(hand) and consecutive[0].same_rank(hand[i]):  # 4 of a kind
          consecutive.append(hand1_c.pop(i))  # i+4
        # Now we generate all combinations
        if len(consecutive) == 3:
          hand1_toak.append((consecutive, copy.copy(hand1_c)))  # 3 choose 3 is 1. 1 set of option. 
        else:  # == 4
          c = consecutive
          hand1_toak.append(([c[0], c[1], c[2]], copy.copy(hand1_c) + c[3]))  # 4 choose 3 is 4.
          hand1_toak.append(([c[1], c[2], c[3]], copy.copy(hand1_c) + c[0]))
          hand1_toak.append(([c[0], c[1], c[3]], copy.copy(hand1_c) + c[2]))
          hand1_toak.append(([c[0], c[2], c[3]], copy.copy(hand1_c) + c[1]))
          hand1_toak.append((c, copy.copy(hand1_c)))  # or 4 at once.
      else:
        i += 1
    
    # split hand into hand2_sss and hand2_c
    shcd = [[] for i in range(4)]  # order: s, h, d, c; partition by same suit first
    i = 0
    while i < len(hand2_c):
      card = hand2_c.pop(i)
      if card.suit('S'): shcd[0].append(card) 
      elif card.suit('H'): shcd[1].append(card)
      elif card.suit('C'): shcd[2].append(card)
      elif card.suit('D'): shcd[3].append(card)
    hand2_sss = []  # then do the splitting
    for suit in shcd:
      i = 0
      while i <= len(suit)-3:
        consecutive = []
        if suit[i+1].rank() - suit[i].rank() == 1 and suit[i+2].rank() - suit[i+1].rank() == 1:  # 3 straight
          consecutive.append(suit.pop(i))
          consecutive.append(suit.pop(i))
          consecutive.append(suit.pop(i))
          while i < len(hand) and suit[i].rank() - consecutive[-1].rank() == 1:  # k straight
            consecutive.append(suit.pop(i))
          # Now we generate all combinations
          for seq_len in range(3, len(consecutive)):
            for j in range(len(consecutive) - seq_len + 1):
              # hand2_sss.append(, copy.copy(hand2_c)))
        else:
          i += 1
    hand2_c = shcd[0] + shcd[1] + shcd[2] + shcd[3]  # stitch together the rest.
    
