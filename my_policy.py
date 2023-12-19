from policy import RummyPolicy
from agent_utility import find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets
import random

class RandomPolicy(RummyPolicy):        
    def draw(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, meld_turn_count, melds):
        """Randomly chooses between drawing from discard pile and stock pile"""
        return random.choice(["discard", "stock"]) 

    def discard(self, hand, player_index, scores, num_cards_in_hands, card_drawn_from_discard_pile, meld_turn_count, melds):
        """Randomly meld (if possible) and discard card"""
        all_poss_melds = find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets(hand, melds)
        available, remaining = random.choice(all_poss_melds)
        
        meld_choice = available
        if not remaining:
            discard_choice = []
        else:
            discard_choice = [random.choice(remaining)]
        # elif not card_drawn_from_discard_pile:
        #     discard_choice = [random.choice(remaining)]
        # else:
        #     # if card_drawn_from_discard_pile in remaining:  # NOTE: deprecated rule.
        #     #     remaining.remove(card_drawn_from_discard_pile)  # cannot discard same card on same turn
        #     discard_choice = [random.choice(remaining)]
        return discard_choice, meld_choice