'''Discretizes the rummy game into MCTS-processible parts. Note Rummy is NOT a perfect information game.'''

from game import State
import copy
from agent_utility import find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets

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
    ...etc

    FINAL DECISION:
    For MCTS, simulate a one-player playout i.e. yourself using the observable knowledge from the current state
    of the game.
    The playout lasts till the end of a ROUND only.
    This is for drawing policy only at the moment.
  '''

  def __init__(self, game, hand, stock_cards, discard_cards, num_turnover, meld_turn_count, melds, discard_policy, draw_policy, num_turn_so_far):
    # These information are related to the current turn of the player, inherited from Policy
    self.game = game  # perfection information instance currently, not fair; need some masking to simulate the unknowing state. Otherwise just a function caller.
    # Other state properties
    self.reconstructed_stock = stock_cards
    self.reconstructed_discard = discard_cards
    self.hand = hand  # DEEPCOPY later at playout; don't want to disturb the original references
    self.num_turnover = num_turnover
    self.meld_turn_count_self = meld_turn_count # not possible given current melding constraints for simplification...
    self.melds = melds  # DEEPCOPY later at playout; don't want to disturb the original references
    self.discard_policy = discard_policy  # first order function.
    self.draw_policy = draw_policy
    self.num_turn_so_far = num_turn_so_far

  def is_terminal(self):
    """ Determines if this state is terminal.  Return value is true is so and false otherwise.

        self -- a state depending on externel information
    """
    return self.game.round_ends([self.hand]) or self.game.tie(self.num_turnover, self.reconstructed_stock.size())

  def payoff(self):
    """ Returns the payoff for player 0 at this terminal state.

        self -- a terminal state
    """
    # NOTE: design a payoff. Since it's a single player
    # Shorter the turns the better (if you win)
    # If tie, then bad reward.
    if self.game.tie(self.num_turnover, self.reconstructed_stock.size()):
      return -1
    else:
      # print(self.num_turn_so_far)  # Based on statistics, ranges from 10 to 150 turn. 
      return (1 - self.num_turn_so_far / 150)  # normalize; inverse reward, less the better.
    
  def actor(self):
    """ Determines which player is the actor in this nonterminal state.

        self -- a nonterminal state
    """
    return 0  # you are always the actor; 1 player playout.

  def get_actions(self):
    """ Returns a list of possible actions in this nonterminal state.
        The representation of each state is left to the implementation.

        self -- a nonterminal state
    """
    return ["stock", "discard"]  # MCTS for drawing for now.

  def is_legal(self, action):
    """ Determines if the given action is legal in this state.

        self -- a state
        action -- an action
    """
    pass   # never used; useless.
  
  def successor(self, action):
    """ Returns the state that results from the given action in this nonterminal state.

        self -- a nonterminal state
        action -- one of the actions in the list returned by get_actions for this state
    """
    temp_policy = Monkey(None, self.discard_policy, [action])  # monkey patching...
    # They differ by state
    succ_stock = copy.deepcopy(self.reconstructed_stock)  # obj by ref, no need to wrap; has a reassignment at card flip
    succ_discard = copy.deepcopy(self.reconstructed_discard)  # clear is used instead.
    succ_hand = [copy.deepcopy(self.hand)]  # need to wrap here, since there's a replacement going on in the game code.
    succ_num_turnover = [self.num_turnover]
    succ_meld_turn_count_self = [self.meld_turn_count_self]
    succ_melds = copy.deepcopy(self.melds)
    # print("before DPMOVE: " + str(succ_hand))
    # Reminder: this function is reference-modifying.
    self.game.player_move(p=0, 
                          policies=[temp_policy], 
                          stock=succ_stock, 
                          discard=succ_discard, 
                          num_turnover=succ_num_turnover, 
                          hands=succ_hand, 
                          scores=[], 
                          meld_turn_count=succ_meld_turn_count_self, 
                          melds=succ_melds,
                          MCTS_draw_policy=True
                          )
    # print("after DPMOVE: " + str(succ_hand))
    # Set up the return state (new copy pretty much)
    succ = GameState(self.game, succ_hand[0], succ_stock, succ_discard, succ_num_turnover[0], succ_meld_turn_count_self[0], 
                     succ_melds, self.discard_policy, self.draw_policy, self.num_turn_so_far + 1)
    return succ

class Monkey(list):
  def __init__(self, draw_policy, discard_policy, *args, **kwargs):
    super(Monkey, self).__init__(*args, **kwargs)
    if draw_policy: self.draw = draw_policy
    if discard_policy: self.discard = discard_policy  # first order function

  def draw(self):
    pass

  def discard(self):
    pass

class AdvancedGameState(GameState):
  # Overwrite
  def get_actions(self):
    """ Returns a list of possible actions in this nonterminal state.
        The representation of each state is left to the implementation.

        self -- a nonterminal state
    """
    # print("Hand at get_actions is " + str(self.hand))
    all_poss_melds = find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets(self.hand, self.melds)
    choices = []
    for available, remaining in all_poss_melds:
      if not remaining:
        choices.append(([], available))
      else:
        for card in remaining:
          choices.append(([card], available))
    
    # print(choices)
    return choices  # MCTS for discarding only (random draw)
  
  # Overwrite
  def successor(self, action):
    """ Returns the state that results from the given action in this nonterminal state.

        self -- a nonterminal state
        action -- one of the actions in the list returned by get_actions for this state
    """
    temp_policy = Monkey(self.draw_policy, None, [action])  # monkey patching...
    # They differ by state
    succ_stock = copy.deepcopy(self.reconstructed_stock)  # obj by ref, no need to wrap; has a reassignment at card flip
    succ_discard = copy.deepcopy(self.reconstructed_discard)  # clear is used instead.
    succ_hand = [copy.deepcopy(self.hand)]  # need to wrap here, since there's a replacement going on in the game code.
    succ_num_turnover = [self.num_turnover]
    succ_meld_turn_count_self = [self.meld_turn_count_self]
    succ_melds = copy.deepcopy(self.melds)
    # print("before DPMOVE: " + str(succ_hand))
    # Reminder: this function is reference-modifying.
    self.game.player_move(p=0, 
                          policies=[temp_policy], 
                          stock=succ_stock, 
                          discard=succ_discard, 
                          num_turnover=succ_num_turnover, 
                          hands=succ_hand, 
                          scores=[], 
                          meld_turn_count=succ_meld_turn_count_self, 
                          melds=succ_melds,
                          MCTS_discard_policy=True,
                          half_start=True
                          )
    # print("after DPMOVE: " + str(succ_hand))
    if not self.game.round_ends(succ_hand) and not self.game.tie(succ_num_turnover, succ_stock.size()):  # possible that the game can end after discard. Remember we are starting from second half!
      # Prepare draw result for the next half_start, if the round doesn't end here.
      self.game.player_move(p=0, 
                            policies=[temp_policy], 
                            stock=succ_stock, 
                            discard=succ_discard, 
                            num_turnover=succ_num_turnover, 
                            hands=succ_hand, 
                            scores=[], 
                            meld_turn_count=succ_meld_turn_count_self, 
                            melds=succ_melds,
                            MCTS_draw_policy=False,
                            draw_only=True
                          )
    # Set up the return state (new copy pretty much)
    succ = AdvancedGameState(self.game, succ_hand[0], succ_stock, succ_discard, succ_num_turnover[0], succ_meld_turn_count_self[0], 
                     succ_melds, self.discard_policy, self.draw_policy, self.num_turn_so_far + 1)  # +1 could have an offset, but all offset so evens out
    return succ