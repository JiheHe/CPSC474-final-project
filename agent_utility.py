import copy

def find_all_MUST_MELD_ALL_AVAILABLE_meldable_sets(hand, melds):
  '''
  Input:
    hand: List[Card] - the current hand of this player; note these Cards are by reference.
    melds: List[Tuple(List[Card], String)] - all melds on the table, each in the manner of (all cards in the meld, meld's type).
                                                meld's type is either "n_of_a_kind" or "same_suit_seq"
  Output:
    List[Tuple(List[Tuple(List[Card], String or int)], List[Card])] - a list of tuples such that the first element list is a set of melding 
                                                options we can do given our current hand, cleared of overlaps. Each meld is a list 
                                                of cards and a string type. The second element is a list of remaining cards from the
                                                first choice in the current hand.
                                                # NOTE: enforced by " MELD_EVERYTHING_IN_HAND_MELDABLE
                                                                      PREFER_NEW_MELDS_OVER_EXISTING_MELDS
                                                                      LONGEST_LENGTH_NEW_MELD_PREFERRED
                                                                      PREFER_SEQUENCE_OVER_N_OF_KIND_FOR_EXISTING " rules.
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
      if i < len(hand1_c) and consecutive[0].same_rank(hand1_c[i]):  # 4 of a kind
        consecutive.append(hand1_c.pop(i))  # i+4
      hand1_toak.append((consecutive, "new"))
    else:
      i += 1
  pass  

  # split hand into hand2_sss and hand2_c
  shcd = [[] for i in range(4)]  # order: s, h, d, c; partition by same suit first
  i = 0
  while i < len(hand2_c):
    card = hand2_c.pop(i)
    if card.suit() == 'S': shcd[0].append(card) 
    elif card.suit() == 'H': shcd[1].append(card)
    elif card.suit() == 'C': shcd[2].append(card)
    elif card.suit() == 'D': shcd[3].append(card)
  hand2_sss = []  # then do the splitting
  for suit in shcd:
    i = 0
    while i <= len(suit)-3:
      consecutive = []
      if suit[i+1].rank() - suit[i].rank() == 1 and suit[i+2].rank() - suit[i+1].rank() == 1:  # 3 straight
        consecutive.append(suit.pop(i))
        consecutive.append(suit.pop(i))
        consecutive.append(suit.pop(i))
        while i < len(suit) and suit[i].rank() - consecutive[-1].rank() == 1:  # k straight
          consecutive.append(suit.pop(i))
        hand2_sss.append((consecutive, "new"))
      else:
        i += 1
  hand2_c = shcd[0] + shcd[1] + shcd[2] + shcd[3]  # stitch together the rest.

  # Priority check
  choice_available_under_constraints = []
  if not len(hand1_toak) == 0:
    available, remaining = find_cards_addable_to_existing_melds(hand1_c, melds)
    choice_available_under_constraints.append((hand1_toak + available, remaining))
  if not len(hand2_sss) == 0:
    available, remaining = find_cards_addable_to_existing_melds(hand2_c, melds)
    choice_available_under_constraints.append((hand2_sss + available, remaining))
  if len(choice_available_under_constraints) == 0:  # no NEW_MELD available, fault to existing
    available, remaining = find_cards_addable_to_existing_melds(hand, melds)
    # print("Avaialble: " + str(available) + "Remaining: " + str(remaining))
    choice_available_under_constraints.append((available, remaining))
  
  return choice_available_under_constraints  # return it.

def find_cards_addable_to_existing_melds(hand, melds):
  available_cards = []
  remaining_cards = []
  # print("hand is here: " + str(hand))
  for card in hand:
    available = False
    for i in range(len(melds)):  # meld is sorted.
      meld = melds[i]
      meld_cards = meld[0]
      if meld[1] == "same_suit_seq":  # PREFERRED
        if meld_cards[0].same_suit(card) and (meld_cards[0].rank() - card.rank() == 1 or card.rank() - meld_cards[-1].rank() == 1):
          available_cards.append(([card], i))
          available = True
          break
      elif meld[1] == "n_of_a_kind":
        if meld_cards[0].same_rank(card):
          available_cards.append(([card], i))
          available = True
          break
    if not available:
      remaining_cards.append(card)
  # print("Reminaing after: " + str(remaining_cards))
  return available_cards, remaining_cards  # a list of tuple

'''
  Attempted to generated ALL combinations of melding choices: that is, you can choose any k out of n consecutives,
  on top of various combinations as well as meld choices to existing meld sets on the table etc.
  Literally a tree problem.... Took a long time to no avail. Mentally breaking down.
  So, going to enforce a new rule (just for our agents only): YOU MUST ALWAYS MELD EVERYTHING MELDABLE WHENEVER ITS YOUR TURN.
  So now the function can generate less choices; but still chocies in what you are melding.
  Note: this isn't enforced in the rummy.py game implementation. It's just an agent thing. We choose it this way 
  so the game code is original and can be used to its full potential in the future.
  Second note: going to prefer NEW_MELDS over EXISTING_MELDS when ENFORCING EVERYTHING MELDABLE. This means, if a card can
  be used for both.... WAIT
  NOTE: since we are receiving one card at a time, say every NEW_MELDS break into two sets that could overlap: a NEW_MELDS,
  and an EXISTING_MELDS. But these two sets DON'T have overlapping cards since we are gaining at most 1 new card at a time,
  a previous melds would've been played previously already. Ex. 123345 is not possible under the MELD_EVERYTHING_IF_POSSIBLE
  policy. So we just need to pick one set of NEW_MELD to do from either the 3 of a kind set, or same suit seq set. However,
  note this is possible at the very first turn of the first player since the player gets 10 cards at once. For the simplicity
  of the game, we'll still stick with our assumption since it's a more suboptimal heuristic but doesn't break the game. It could
  be treated as a rule so to speak. This is provable via induction.....
  NOTE: actually there are still more enumerations. We've established so far that the 3 of a kind set and same seq set don't
  overlap. We are also going to add a rule "LONGEST_LENGTH_NEW_MELD_PREFERRED" so we can guarantee that within each set, the 
  subsets don't overlap, else they would've been chained up into one under this rule. Lastly, we'll add a rule stating 
  "PREFER_SEQUENCE_OVER_N_OF_KIND_FOR_EXISTING," so there's less enumeration for choosing between whether to attach a card to a
  n_of_a_kind or same_set_seq. We want to end a round asap, and making new melds & extending same_set_seq so the seq stays open
  grant more chance for the game to end, so adding these rules are appropriate. Now the pipeline is much simpler. 

  So in conclusion, our non-conflicting, patching rules are:
  MELD_EVERYTHING_IN_HAND_MELDABLE
  PREFER_NEW_MELDS_OVER_EXISTING_MELDS
  LONGEST_LENGTH_NEW_MELD_PREFERRED
  PREFER_SEQUENCE_OVER_N_OF_KIND_FOR_EXISTING
'''

# def find_all_meldable_sets(self, hand, melds):
#   '''
#   Input:
#     hand: List[Card] - the current hand of this player; note these Cards are by reference.
#     melds: List[Tuple(List[Card], String)] - all melds on the table, each in the manner of (all cards in the meld, meld's type).
#                                                 meld's type is either "n_of_a_kind" or "same_suit_seq"
#   Output:
#     List[List[Tuple(List[Card], String)]] - a list of lists such that each list is a set of melding options we can do given our
#                                                 current hand, cleared of overlaps. Each meld is a list of cards and a string type.
#   '''  
#   hand.sort()  # sort hand if not already sorted.
#   # NOTE: a shallow copy where each entry is the same reference to the same card, but different lists
#   hand1_c = copy.copy(hand)  # three of a kind leftovers
#   hand2_c = copy.copy(hand)  # same_suit_seq leftovers

#   # split hand into hand1_toak and hand1_c
#   i = 0
#   hand1_toak = []
#   while i <= len(hand1_c)-3:
#     consecutive = []
#     if hand1_c[i].same_rank(hand1_c[i+1]) and hand1_c[i+1].same_rank(hand1_c[i+2]):  # 3 of a kind
#       consecutive.append(hand1_c.pop(i))  # i+1
#       consecutive.append(hand1_c.pop(i))  # i+2
#       consecutive.append(hand1_c.pop(i))  # i+3
#       if i < len(hand) and consecutive[0].same_rank(hand[i]):  # 4 of a kind
#         consecutive.append(hand1_c.pop(i))  # i+4
#       # Now we generate all combinations
#       if len(consecutive) == 3:
#         hand1_toak.append((consecutive, copy.copy(hand1_c)))  # 3 choose 3 is 1. 1 set of option. 
#       else:  # == 4
#         c = consecutive
#         hand1_toak.append(([c[0], c[1], c[2]], copy.copy(hand1_c) + c[3]))  # 4 choose 3 is 4.
#         hand1_toak.append(([c[1], c[2], c[3]], copy.copy(hand1_c) + c[0]))
#         hand1_toak.append(([c[0], c[1], c[3]], copy.copy(hand1_c) + c[2]))
#         hand1_toak.append(([c[0], c[2], c[3]], copy.copy(hand1_c) + c[1]))
#         hand1_toak.append((c, copy.copy(hand1_c)))  # or 4 at once.
#     else:
#       i += 1
  
#   # split hand into hand2_sss and hand2_c
#   shcd = [[] for i in range(4)]  # order: s, h, d, c; partition by same suit first
#   i = 0
#   while i < len(hand2_c):
#     card = hand2_c.pop(i)
#     if card.suit('S'): shcd[0].append(card) 
#     elif card.suit('H'): shcd[1].append(card)
#     elif card.suit('C'): shcd[2].append(card)
#     elif card.suit('D'): shcd[3].append(card)
#   hand2_sss = []  # then do the splitting
#   for suit in shcd:
#     i = 0
#     while i <= len(suit)-3:
#       consecutive = []
#       if suit[i+1].rank() - suit[i].rank() == 1 and suit[i+2].rank() - suit[i+1].rank() == 1:  # 3 straight
#         consecutive.append(suit.pop(i))
#         consecutive.append(suit.pop(i))
#         consecutive.append(suit.pop(i))
#         while i < len(hand) and suit[i].rank() - consecutive[-1].rank() == 1:  # k straight
#           consecutive.append(suit.pop(i))
#         # Now we generate all combinations
#         for seq_len in range(3, len(consecutive)):
#           for j in range(len(consecutive) - seq_len + 1):
#             # hand2_sss.append(, copy.copy(hand2_c)))
#       else:
#         i += 1
#   hand2_c = shcd[0] + shcd[1] + shcd[2] + shcd[3]  # stitch together the rest.
  