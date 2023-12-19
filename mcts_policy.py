from policy import RummyPolicy
from agent_utility import find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets
from mcts import mcts_draw_policy
from rummy_game import GameState
import random

class MCTSPolicy(RummyPolicy):
  def __init__(self, time, game):
    self.time = time
    self.game = game

  def draw(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, meld_turn_count, melds):
    state = GameState(self.game, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, meld_turn_count, melds)
    mcts = mcts_draw_policy(self.time)  # a callable function
    choice = mcts(state)
    return choice

  def discard(self, hand, player_index, scores, num_cards_in_hands, card_drawn_from_discard_pile, meld_turn_count, melds):
    # Use the heuristical discard
    pass