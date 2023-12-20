from policy import RummyPolicy
from agent_utility import find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets
from base_mcts import base_mcts_policy
from rummy_game import GameState, AdvancedGameState
from deck import Deck
import copy
import random

class BaseMCTSPolicy(RummyPolicy):
  def __init__(self, time, game):
    self.time = time
    self.game = game

  def generate_unseen_card_distribution(self, hand, discard_pile_top_card, num_cards_in_hands, num_cards_stock_pile, melds):
    hand_info = copy.copy(hand)  # shallow copy of obj ref
    meld_info = [card for meld_set in melds for card in meld_set[0]]
    existing_cards = hand_info + meld_info  # don't overlap
    if discard_pile_top_card:
      existing_cards += [discard_pile_top_card]
    reconstructed_stock = Deck(self.game.ALL_RANKS, self.game.ALL_SUITS, 1)
    i = 0
    while i < len(reconstructed_stock._cards):  # remove the viewable, existing possibilities from the deck
      existed = False
      for j in range(len(existing_cards)):
        if reconstructed_stock._cards[i].same_suit(existing_cards[j]) and reconstructed_stock._cards[i].same_rank(existing_cards[j]):
          existing_cards.pop(j)
          existed = True
          break
      if existed:
        reconstructed_stock._cards.pop(i)
      else:
        i += 1
      if len(existing_cards) == 0:
        break
    # Select some cards to be the assumed stock cards
    assumed_stock_cards = random.sample(reconstructed_stock._cards, k=num_cards_stock_pile) 
    # print(len(reconstructed_stock._cards) - len(assumed_stock_cards))
    # print("stock " + str(assumed_stock_cards))
    # Create a list of the remaining cards after removing the selected ones
    remaining_cards = [card for card in reconstructed_stock._cards if card not in assumed_stock_cards]
    # print(len(remaining_cards))
    # print("remaining " + str(remaining_cards))
    reconstructed_stock._cards = assumed_stock_cards
    # Randomly remove sum(num_cards_in_hands)-num_cards_of_you from the remaining to assume other players' cards
    assumed_discard_cards = random.sample(remaining_cards, k = len(remaining_cards) - (sum(num_cards_in_hands)-len(hand)))
    if discard_pile_top_card:
      assumed_discard_cards.append(discard_pile_top_card)
    # print(len(assumed_discard_cards))
    # print("discard " + str(assumed_discard_cards))
    return reconstructed_stock, assumed_discard_cards

  def draw(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, meld_turn_count, melds):
    """Use MCTS to choose between drawing from discard pile and stock pile"""
    # this is for playout only.
    # simulate a bad player that DOESN'T TRACK CARDS. NOTE: potentially improvement: a belief table that does
    reconstructed_stock, assumed_discard_cards = self.generate_unseen_card_distribution(hand, discard_pile_top_card, num_cards_in_hands, num_cards_stock_pile, melds) 

    root_state = GameState(self.game, hand, reconstructed_stock, assumed_discard_cards, num_turnover, 
                           meld_turn_count[player_index], melds, self.playout_random_discard, None, 0)
    mcts = base_mcts_policy(self.time)  # a callable function
    choice = mcts(root_state)
    return choice
  
  def playout_random_discard(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, card_drawn_from_discard_pile, meld_turn_count, melds):
    # A weak discard policy just for playout
    all_poss_melds = find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets(hand, melds)
    available, remaining = random.choice(all_poss_melds)
    meld_choice = available
    discard_choice = [] if not remaining else [random.choice(remaining)]
    return discard_choice, meld_choice

  def discard(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, card_drawn_from_discard_pile, meld_turn_count, melds):
    # Use the heuristical discard; random discard for now. TODO: update later.
    """Randomly meld (if possible) and discard card"""
    return self.playout_random_discard(hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, card_drawn_from_discard_pile, meld_turn_count, melds)


class AdvanceMCTSPolicy(BaseMCTSPolicy):
  # Still using the advance draw for the actual draw_policy.

  def playout_random_draw(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, meld_turn_count, melds):
    # A weak draw policy just for playout
    return random.choice(["stock", "discard"])

  # Carry out MCTS on discard too
  def discard(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, card_drawn_from_discard_pile, meld_turn_count, melds):
    reconstructed_stock, assumed_discard_cards = self.generate_unseen_card_distribution(hand, discard_pile_top_card, num_cards_in_hands, num_cards_stock_pile, melds) 

    draw_strategy = self.playout_random_draw  # use self.draw for recursion.
    root_state = AdvancedGameState(self.game, hand, reconstructed_stock, assumed_discard_cards, num_turnover, 
                           meld_turn_count[player_index], melds, None, draw_strategy, 0)  # NOTE: replace to self.draw for recursion.
    mcts = base_mcts_policy(self.time)  # a callable function
    choice = mcts(root_state)
    return choice