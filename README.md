Outline for 2 player Rummy
https://bicyclecards.com/how-to-play/rummy-rum
Ranking: K (highest) to A (lowest)

This page explains how the game works and the set of rules/modifications we are following.
For a detailed report and logistics, please check 'log.'

Setup:
  One deck of cards, standard
  Each player is dealt 10 cards from the deck one at a time face-down without replacements
  The remaining cards are placed face down on the table, forming the stock.
  The top card of the stock is turned face up and placed next to the stock to start the discard pile。

Play:
  *Each player tries to form matched sets consisting of groups of three or four of a kind, or sequences of three or more cards of the same suit.
  Dealer alternates, and non-dealer starts the round.
  Each round, 
    First, the player in-turn either draws the top card of the stock or takes the top card of the discard pile to add to his hand
    Then, optionally (and):
      the player may lay down as many meld (matched set) face up on the table as they have without consuming the turn.
      the player may add one or more cards from their hand to any matched set already shown on the table.
    Next, the player discards one card, face up, onto the discard pile.
      *If the player has drawn from the discard pile, he may not discard the same card on that turn (DEPRECATED).
  When a player gets rid of all of their cards, they win the game.
    *If the player can get rid of all cards in the "optional" phase, then the round ends and no further discard or play is needed.
  If the last card of the stock has been drawn and no player has gone out, the next player in turn may either take the top of the discard pile, or may turn the discard pile over to form a new stock (without shuffling it) and draw the top card. Play then proceeds as before.
  
End Round:
  Each player pays to the winner the pip value of the cards remaining in their hand, whether the cards form matched sets or not. Face cards count 10 each, aces 1 each, and every other card its pip value.
    *Here we say the winner gains that many points
  A player goes "rummy" when they get rid of all cards in their hand at once, without previously having put down or laid off any cards (i.e. no optional). In this event, every other player pays double - twice what opponents would otherwise owe.

Quick modification:
For every GAME, the player that reaches 100 points first wins, or the player with the most points if multiple players are beyond 100.
If the stock deck gets burned through 2 times, then the game ends in a tie where everyone gains 5 points.
  *More specifically, the turnover is the specific action of discard pile -> new stock. If this happens 2 times already and on the
  current player's turn, the stock is gone, then the game ends in a tie immediately. 
If there are multiple winners in a round (i.e. share the same max points), then each winning player recevies a win eqaul to the
average over the number of winners, i.e. for example k winner, each winner gets 1/k wins. Everything still sums to 1 mathematically in the
end in terms of percentage, which is desired for the metrics.

# NOTE:
This game is a zero-sum game.
The game generally converges. But tie condition is implemented so the playout doesn't go on a long time by chance.
The rules above are essentially the rules of the original game. For the ease of computation, we implemented four agent-only restrictions to 
avoid abundunt enumerations. They are NOT enforced in the original game's code but soft-imposed as all our agents use them. They are:
  MELD_EVERYTHING_IN_HAND_MELDABLE
  PREFER_NEW_MELDS_OVER_EXISTING_MELDS
  LONGEST_LENGTH_NEW_MELD_PREFERRED
  PREFER_SEQUENCE_OVER_N_OF_KIND_FOR_EXISTING
More details are in the comments of agent_utility.py near the middle of the page.
