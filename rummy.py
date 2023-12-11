'''Implements the rummy card game outlined in README'''

from deck import Deck


class Game:
  '''
    The Game class for the Rummy Game
    NOTE: While the AI framework supports 2-player Rummy, this Game implementation can support
    as many players as it wants, given that only 1 deck of card can be used. Feel free to adjust
    the parameters in __init__ to adapt to multi-player functionality.
    NOTE: The logic treats cards by OBJECT REFERENCES. So when writing the policies we are not 
    passing in deepcopies of the player's hand. So PLEASE DON'T SCREW UP the card references
    in the hand and MAKE SURE TO RETURN THE CARD OBJECT REFERENCES FROM THE HAND as opposed to
    making new cards!!!!!!!!!!!
    NOTE: Need to implement .draw and .discard for the policy object to work.
  '''

  def __init__(self):
    self.WINNING_SCORE = 100  # TUNABLE. Winning score required for the game winner.
    self.NUM_PLAYERS = 2  # TUNABLE. Number of players/policies in the game.
    self.NUM_CARDS_INIT = 10  # TUNABLE. Number of cards to deal to each player at the start of each round.
    self.ALL_RANKS = range(1, 14)  # constant
    self.ALL_SUITS = ['S', 'H', 'D', 'C']  # constant
    self.PLAYERS = range(self.NUM_PLAYERS)  # constant

  def deal(self, count):
    deck = Deck(self.ALL_RANKS, self.ALL_SUITS, 1)  # a standard deck of cards. DON'T CHANGE THIS.
    deck.shuffle()
    dealt = deck.deal(count)
    return deck, dealt
  
  def round_ends(self, hands):
    return 0 in [len(hand) for hand in hands]  # round ends when a player is out of cards
  
  def _remove_from_hand(self, hand, cards_to_remove):
    # Copied over and slightly modified from deck's logic
    """ Removes the given cards from the current hand.  If there is a card
        to remove that isn't present in this hand, then it throws an error.  
        If there are multiple occurrences of a given card
        in the list to remove, then it throws an error too.

        hand AND cards_to_remove -- a list of Card objects
    """
    # Should be a fine operation since all cards are objects processed by reference.
    counts = dict()
    for card in hand:
        if card not in counts:
            counts[card] = 0
        counts[card] += 1
        if counts[card] > 1:
          raise Exception(f"Something went wrong. Card {card} appeared more than once in hand!")

    for card in cards_to_remove:
        if card not in counts:
          raise Exception(f"Error: Trying to remove {card} from {hand} when it's not in hand.")
        counts[card] -= 1
        if counts[card] < 0:
          raise Exception(f"Something went wrong. Card {card} appeared more than once in cards_to_remove!")

    return [card for card in counts.keys() if counts[card] == 1]  # the remaining cards in hand.  # new list is less efficient than .remove since by reference.

  def play(self, policies, log):
    '''
      Input:
        policies - a list of Policy objects ex. [p0_policy, p1_policy]
        log - ...
      Output:
        int, int - index of the game winning player/policy and the score it obtained
    '''
    if len(policies) != self.NUM_PLAYERS:
      raise Exception(f"Error: have {self.NUM_PLAYERS} players, but {len(policies)} policies!")
    scores = [0 for p in self.PLAYERS]
    # dealer = 0  # doesn't really matter who's dealer in this game. The game manager deals.

    # loop until one player has points to win
    while max(scores) < self.WINNING_SCORE:
      # One round of Rummy
      log("Score: " + str(scores))

      # Setup
      # deal cards
      stock, dealt = self.deal(self.NUM_PLAYERS * self.NUM_CARDS_INIT + 1)  # deal num_players * num of cards per player plus the discard; stock is the remaining deck
      hands = [dealt[self.NUM_CARDS_INIT * p : self.NUM_CARDS_INIT * (p + 1)] for p in self.PLAYERS]  # [p0_hand, p1_hand]
      meld_turn_count = [0 for p in self.PLAYERS]  # tracks the number of turns where melding is used for each player.
      discard = [dealt[-1]]  # the discard pile starts with a card from stock, hence the +1 earlier
      melds = []  # the list of all melds (matched set) on the table. Tuple ([cards], type) "n_of_a_kind, same_suit_seq"
      # Note: here, "top of the pile" refers to "end of the list"
      rummy_factor = 1  # for the special rummy case.

      # Play
      while not self.round_ends(hands):
        for p in self.PLAYERS:
          # Draw
          # Draw Policy either returns "stock" for drawing the top card from stock or "discard" for taking the top card from discard pile.
          draw_policy = policies[p].draw(hands[p],  # your hand
                                  p,  # p is "your player index"
                                  scores[:],  # all players' scores
                                  discard[-1],  # top visible card of the discard pile
                                  stock.size(),  # num cards left of the stock pile
                                  meld_turn_count,  # number of turns where melding is used for each player
                                  melds)  # all melds on the table
          card_drawn_from_discard_pile = None
          if draw_policy == "stock":  # draw the top card from stock pile
            if stock.size() == 0:  # stock pile is empty
              stock._cards = list(reversed(discard))  # turn over the discard pile and use it as the new stock pile
              discard = []  # discard pile is gone now. But no worry! This player will have to discard anyway.
            hands[p] += stock.deal(1)  # draw 1 card from the top
          elif draw_policy == "discard":  # take the top card from discard pile
            top_card = discard.pop()
            hands[p].append(top_card)
            card_drawn_from_discard_pile = top_card
          else:
            raise Exception(f"Invalid Draw Policy Response: {draw_policy}. Must be 'stock' or 'discard.'")

          # Discard & Optional (can also win here)
          # Discard Policy returns a [Card] to discard and [([Cards],decision)([Cards],decision)...] to meld away. Can be empty lists!
          discard_policy, meld_policy = policies[p].discard(hands[p],  # your hand, NOT deepcopied atm cuz by reference.
                                                  p,  # p is "your player index"
                                                  scores[:],  # all players' scores
                                                  card_drawn_from_discard_pile,  # if applicable. Can't discard the same card drawn from discard pile in this turn.
                                                  meld_turn_count,  # number of turns where melding is used for each player
                                                  melds)  # all melds on the table)

          # Track for rummy_factor.        
          if len(meld_policy) > 0:
            meld_turn_count[p] += 1  # deciding to meld on this turn. 
          
          # Execute meld. Decision is either "new" for new meld onto the table, or INT index indicating which meld it's adding to.
          for matched_set, decision in meld_policy:
            if decision == "new":  # adding a new meld onto the table
              # Check new meld validity
              if len(matched_set) < 3: 
                raise Exception(f"Invalid new meld {matched_set}, too few cards.")
              matched_set.sort()  # ascending order.
              n_of_a_kind = all(matched_set[0].same_rank(card) for card in matched_set)
              same_suit_seq = all( (matched_set[i+1] - matched_set[i] == 1 and matched_set[i+1].same_suit(matched_set[i])) for i in range(len(matched_set))-1)
              if not n_of_a_kind and not same_suit_seq:
                raise Exception(f"Invalid new meld {matched_set}, need to be n_of_a_kind or same_suit_sequence.")  # match set is sorted now.
              # Put the new meld on the table
              hands[p] = self._remove_from_hand(hands[p], matched_set)  # remove from hand
              melds.append((matched_set, "n_of_a_kind" if n_of_a_kind else "same_suit_seq"))
            
            elif isinstance(decision, int) and (0 <= decision < len(melds)):  # adding onto an existing meld on the table
              meld_matched_set, set_type = melds[decision]  # decision is the meld index.  # meld_matched_set is already sorted.
              if set_type == "n_of_a_kind":  # trying to add a 4th card
                # Check add meld validity
                if not len(matched_set) == 1:
                  raise Exception(f"Cannot add to three of a kind {meld_matched_set} with {matched_set}")
                if len(meld_matched_set) == 4:
                  raise Exception(f"Cannot add to four of a kind {meld_matched_set} with {matched_set}, already full")
                if not all((not matched_set[0].same_suit(card)) and matched_set[0].same_rank(card) for card in meld_matched_set):
                  raise Exception(f"Cannot add to three of a kind {meld_matched_set} with {matched_set}, invalid add.")
                # Add into the meld
                hands[p] = self._remove_from_hand(hands[p], matched_set)  # remove from hand
                melds[decision][0] += matched_set
              elif set_type == "same_suit_seq":  # trying to append a sequence
                # Check add meld validity
                if len(matched_set) == 0:
                  raise Exception(f"Cannot use an empty set of cards for melding.")
                matched_set.sort()  # ascending order.   # Also remember meld_matched_set is sorted when placed onto the table.
                if meld_matched_set[0] - matched_set[-1] == 1 and meld_matched_set[0].same_suit(matched_set[-1]):  # append to meld_set front
                  # Add into the meld
                  hands[p] = self._remove_from_hand(hands[p], matched_set)  # remove from hand
                  melds[decision][0] = matched_set + melds[decision][0]
                elif matched_set[0] - meld_matched_set[-1] == 1 and meld_matched_set[-1].same_suit(matched_set[0]):  # append to meld_set end
                  # Add into the meld
                  hands[p] = self._remove_from_hand(hands[p], matched_set)  # remove from hand
                  melds[decision][0] = melds[decision][0] + matched_set
                else:
                  raise Exception(f"Cannot add to same_suit_seq {meld_matched_set} with {matched_set}, invalid add")

            else:
              raise Exception(f"Invalid meld decision: {decision}. Must be 'new' or int (existing meld index).")
            
          # Check if anyone has won after melding.
          if self.round_ends(hands):
            break

          # Execute Discard.
          if not len(discard_policy) == 1:
            raise Exception(f"Can only discard one card at a time, not {discard_policy}")
          if card_drawn_from_discard_pile and discard_policy[0] == card_drawn_from_discard_pile:
            raise Exception(f"Cannot discard the card {discard_policy[0]} drawn from the discard pile on the same turn.")
          hands[p] = self._remove_from_hand(hands[p], discard_policy)
          discard.append(discard_policy[0])  # put faceup onto the discard pile

      # End Round
      round_winner = [i for i in range(len(hands)) if len(hands[i]) == 0][0]  # should only have 1 winner
      # winner get rid of all cards all at once, without any previous putdown or laid off (i.e. no optional)
      if meld_turn_count[round_winner] == 1:
        rummy_factor = 2  # everyone pays double!
      # Rest of the players pay up the pip value of remaining cards to the winner.
      for p in self.PLAYERS:
        pip_sum = 0
        for card in hands[p]:  # winner would have no cards.
          pip_sum += card.rank() if card.rank() <= 10 else 10  # Ace = 1, face cards = 10, rest rank value.
        scores[round_winner] += pip_sum * rummy_factor  # Pay the same as before, or pay double

      # Starting player alternates (or move to the next) next round
      self.PLAYERS = self.PLAYERS[1:] + self.PLAYERS[:1]  # NOTE: hopefully doesn't lead to bugs.

    # Game ends, return the stats
    max_score = max(scores)  # Find the maximum value in the list
    game_winner = scores.index(max_score)  # Find the index of the maximum value
    log(f"Game winner: player {game_winner} with score {max_score}")
    return game_winner, max_score
  
  def evaluate_policies(self, policies, count):
    '''
      A simple policy evaluator that returns the average % of winning for each policy
      Input:
        policies - a list of Policy objects ex. [p0_policy, p1_policy]
        count - the number of trials/games to run the evaluation
      Output:
        [float] - a list of average winning ratio for each policy, based on the given index
    '''
    wins = [0 for p in self.NUM_PLAYERS]
    for g in range(count):
      game_winner, max_score = self.play(policies, lambda mess: None)  # no log function for now.
      wins[game_winner] += 1
    return [win / count for win in wins]
