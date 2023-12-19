'''Discretizes the rummy game into MCTS-processible parts. Note Rummy is NOT a perfect information game.'''

from rummy import Game as Rummy
from game import State


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

