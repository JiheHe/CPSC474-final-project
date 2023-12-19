from policy import RummyPolicy
from agent_utility import find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets
import random

class RandomPolicy(RummyPolicy):        
    def draw(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, meld_turn_count, melds):
        """Randomly chooses between drawing from discard pile and stock pile"""
        
        if not discard_pile_top_card:
            return "stock"
        
        return random.choice(["discard", "stock"]) 

    def discard(self, hand, player_index, scores, num_cards_in_hands, card_drawn_from_discard_pile, meld_turn_count, melds):
        """Randomly meld (if possible) and discard card"""
        all_poss_melds = find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets(hand, melds)
        meld_choice = []
        discard_choice = []

        if all_poss_melds:
            meld_choice = random.choice(all_possible_melds)
            cards_left = list(set(hand) - set(meld_choice[0][0]))
            discard_choice.append(random.choice(cards_left))
        else:
            discard_choice.append(random.choice(hand))
        
        return discard_choice, meld_choice