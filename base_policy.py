from policy import RummyPolicy
from agent_utility import find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets
import random
from deck import Card

class RandomPolicy(RummyPolicy):     
    """Random policy that arbitrarily chooses a move out of all possible moves"""

    def draw(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, meld_turn_count, melds):
        """Randomly chooses between drawing from discard pile and stock pile"""

        return random.choice(["discard", "stock"]) 

    def discard(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, card_drawn_from_discard_pile, meld_turn_count, melds):
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
    
class SimpleGreedyPolicyBASE(RummyPolicy):
    """
    Simple greedy policy that:
    1. Draws from discard pile if it allows itself to meld
    2. Melds if possible
    3. Avoids discarding cards that are part of a run or set draw (two consecutive, same-suit cards that could form a run or two of a kind)
    """

    def draw(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, meld_turn_count, melds):
        """Greedily draws from a pile (draws from discard pile if it allows itself to meld)"""

        if len(find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets(hand, melds)) < len(find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets(hand+[discard_pile_top_card], melds)):
            return "discard"
        
        return random.choice(["discard", "stock"]) 

    def discard(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, card_drawn_from_discard_pile, meld_turn_count, melds):
        """Greedily melds and discards card (melds if possible and avoids discarding cards that are part of a run or set draw)"""

        all_poss_melds = find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets(hand, melds)
        available, remaining = random.choice(all_poss_melds)

        meld_choice = available
        if not remaining:
            discard_choice = []
        else:
            no_draw_remaining = []
            for comp_card in remaining:
                curr_rank = comp_card.rank()
                curr_suit = comp_card.suit()

                for check_card in remaining:
                    is_part_of_draw = False

                    if (check_card.rank() == curr_rank and check_card.suit() != curr_suit) or (check_card.rank()-1 == curr_rank and check_card.suit() == curr_suit) or (check_card.rank()+1 == curr_rank and check_card.suit() == curr_suit):
                        is_part_of_draw = True
                    
                    if not is_part_of_draw:
                        no_draw_remaining.append(check_card)

            if len(no_draw_remaining) > 0:
                remaining = no_draw_remaining
        
            discard_choice = [random.choice(remaining)]

        return discard_choice, meld_choice
    

class HeuristicPolicyBASE(RummyPolicy):
    """
    Strong heuristic agent with several strategic implementations including:
    1. Greedy components of SimpleGreedyPolicy
    2. Numerous rules with optimized cutoffs via testing or calculations / logic
    3. Accurate discard list tracking throughout gameplay
    4. EV calculation to optimize draw choice using hand, meld, and discard list information
    5. Non-determinism to maintain unpredictability and to avoid infinite loops
    6. Card ranking system for both draw and discard
    """

    def __init__(self):
        self.clear_cache()
        self._num_stock_cards_after_turn = -1
        self._total_rank_left = 340
        self._total_cards_left = 52

    def clear_cache(self):
        self._discard_list = []
        self._num_stock_cards_after_turn = -1

    def draw(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, meld_turn_count, melds):
        """Heuristically chooses between drawing from discard pile and stock pile"""

        # If you took last stock pile card and opponent chooses stock, clear cache
        if self._num_stock_cards_after_turn == 0 and num_cards_stock_pile != 0:
            self.clear_cache()
        
        # If opponent took card from discard pile (stock pile size is unchanged), pop it from the list
        elif self._num_stock_cards_after_turn == num_cards_stock_pile:
            self._discard_list.pop()

        # Append the card that opponent discarded
        self._discard_list.append(discard_pile_top_card)

        if len(find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets(hand, melds)) < len(find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets(hand+[discard_pile_top_card], melds)):
            self._discard_list.pop()
            return "discard"
        
        # Non-determinism to avoid infinite loop (which is allowed by rules)
        if random.random() < 0.1:
            random_choice = random.choice(["discard", "stock"])
            if random_choice == "stock" and num_cards_stock_pile == 0:
                self.clear_cache()
            if random_choice == "discard":
                self._discard_list.pop()

            return random_choice
        
        # Each suit has cards summing to 85 (1+2+...+10+10+10+10), for a total rank sum of 340
        self._total_rank_left = 340
        self._total_cards_left = 52

        for hand_card in hand:
            self._total_cards_left -= 1
            real_rank = hand_card.rank()
            if real_rank > 10:
                real_rank = 10
            
            self._total_rank_left -= real_rank
        
        for i in range(len(melds)):
            for meld_card in melds[i][0]:
                self._total_cards_left -= 1
                real_rank = meld_card.rank()
                if real_rank > 10:
                    real_rank = 10
            
                self._total_rank_left -= real_rank

        for discard_card in self._discard_list:
            self._total_cards_left -= 1
            real_rank = discard_card.rank()
            if real_rank > 10:
                real_rank = 10
            
            self._total_rank_left -= real_rank
        
        if self._total_cards_left > 0:
            rank_cutoff = self._total_rank_left/self._total_cards_left
        else:
            rank_cutoff = 6

        if discard_pile_top_card.rank() <= rank_cutoff:
            self._discard_list.pop()
            return "discard"
        else:
            if num_cards_stock_pile == 0:
                self.clear_cache()
            return "stock"

    def discard(self, hand, player_index, scores, num_cards_in_hands, discard_pile_top_card, num_cards_stock_pile, num_turnover, card_drawn_from_discard_pile, meld_turn_count, melds):
        """Heuristically melds (if possible) and discards card"""

        all_poss_melds = find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets(hand, melds)
        available, remaining = random.choice(all_poss_melds)
        
        meld_choice = available
        if not remaining:
            discard_choice = []
        else:
            bestCardIndex = -1
            bestCardRank = 999
            
            # If opponent has more than 3 cards in hand, don't discard cards that
            # contribute to a run or set draw, no matter the rank value
            if num_cards_in_hands[1-player_index] > 3 and len(hand) > 1.7*num_cards_in_hands[1-player_index]:
                no_draw_remaining = []
                for comp_card in remaining:
                    curr_rank = comp_card.rank()
                    curr_suit = comp_card.suit()

                    for check_card in remaining:
                        is_part_of_draw = False

                        if (check_card.rank() == curr_rank and check_card.suit() != curr_suit) or (check_card.rank()-1 == curr_rank and check_card.suit() == curr_suit) or (check_card.rank()+1 == curr_rank and check_card.suit() == curr_suit):
                            is_part_of_draw = True
                        
                        if not is_part_of_draw:
                            no_draw_remaining.append(check_card)

                if len(no_draw_remaining) > 0:
                    remaining = no_draw_remaining

            # Cards for discarding are ranked best to worst (higher rank value is better)
            for i in range(len(remaining)):
                currRank = -1
                currRank = 14 - remaining[i].rank()
                
                if currRank != -1 and currRank < bestCardRank:
                    bestCardIndex = i
                    bestCardRank = currRank

            if bestCardIndex != -1:
                discard_choice = [remaining[bestCardIndex]]

        self._num_stock_cards_after_turn = num_cards_stock_pile
        if discard_choice:
            self._discard_list.append(discard_choice[0])

        return discard_choice, meld_choice