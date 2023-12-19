import argparse
from rummy import Game as RummyGame
from my_policy import RandomPolicy
from mcts_policy import MCTSPolicy
import sys

class SimulationError(Exception):
  pass

def init_agent(type, time, game):
  if type == 0:
    return RandomPolicy()
  elif type == 1:
    pass
  elif type == 2:
    return MCTSPolicy(time, game)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Test agents for Rummy")
  parser.add_argument('--agent1', type=int, action="store", default=0, help='Agent type (0=random, 1=heuristic, 2=MCTS)')
  parser.add_argument('--agent2', type=int, action="store", default=0, help='Agent type (0=random, 1=heuristic, 2=MCTS)')
  parser.add_argument('--count', type=int, action="store", default=1, help='number of games to play (default=1)')
  parser.add_argument('--time', type=float, action="store", default=0.1, help='time for MCTS per move')
  args = parser.parse_args()

  if args.count < 1:
    raise SimulationError("count must be positive")
  if args.time <= 0:
    raise SimulationError("time must be positive")
  if args.agent1 < 0 or args.agent1 > 2:
    raise SimulationError("agent1 must be 0, 1, or 2")
  if args.agent2 < 0 or args.agent2 > 2:
    raise SimulationError("agent2 must be 0, 1, or 2")

  game = RummyGame()

  agent1 = init_agent(args.agent1, args.time, game)
  agent2 = init_agent(args.agent2, args.time, game)
  
  result = game.evaluate_policies([agent1, agent2], args.count)
  print(result)
  sys.exit(0)
  
