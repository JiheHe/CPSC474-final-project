# NOTE: this setup is capable of dealing with single-player, since we all have to do is make the state-actor == 0 always.
import time
import math
import random

class Node:
  '''A node in the MCTS tree, along with information it stores'''

  def __init__(self, state, parent=None):
    self.total_reward = 0
    self.visit_count = 0
    self.parent = parent
    self.children = []  # everything is by reference in python automatically
    self.state = state
    self.actions_cache = state.get_actions()

def base_mcts_policy(allowed_time):
  '''
  Input:
    allowed_time - time budget for the MCTS computation for this round of game, in seconds
  Output:
    A function that takes a position and returns the move suggested by running MCTS for that amount of time starting with that position
  '''

  # Global variables in the scope of a round of game. (Nothing yet)

  # Current enhancements: None

  def mcts(state):
    '''
    Input:
      state - an instance of the abstract State class from the game module, a non-terminal state.
    Output:
      The suggested move
    '''
    # Ready up for the time constraint for this MCTS step  
    start_time = time.time()

    # Turn state into a root node, a tree with only 1 node at the root.
    root = Node(state=state)

    # While current_time (in miliseconds) hasn't reached the allowed time:   *Note - can be a bit over
    while (time.time() - start_time) < allowed_time:
      # Note: based on my experiment, we can have terminal leaves. And it makes no difference.

      # traverse: choose path from root s to leaf s’, 
      # w/ expand: if s’ expandable then add children, s’← arbitrary child
      leaf = traverse(root)

      # simulate: play from s’ to terminal position t
      terminal_reward = simulate(leaf)

      # update: propagate reward, increment count on path s’ to root 
      update(leaf, terminal_reward)

    # return action leading to child of root s with best statistics
    return best_action(root)

  return mcts

N = 2  # the UCT constant. TODO: NOT TUNED YET!!!

def compute_UCT(child_node, parent_node):
  '''
  Computes the UCT formula output
  Current version: UCB (UCT0)
  Idea 1) during traversal, min for opponent, max for yourself. And backprop in perspective of you directly.
  Idea 2) during traversal, max everything, but during backprop + for you, - for opponent.
  Idea 3) This (from TA). We flip for the opponent. (Honesty idk why this works better than total flip. Ty TA).
  '''
  # IMPORTANT TAKEAWAY: compute UCT from the perspective of PARENT!!!!
  if child_node.visit_count == 0:
    result = (float('inf') if parent_node.state.actor() == 0 else float('-inf'))
  else:
    exploit = child_node.total_reward / child_node.visit_count  # both parties will exploit
    explore = math.sqrt(N * math.log(parent_node.visit_count) / child_node.visit_count)
    # P0 maximizes, P1 minimizes.
    result = exploit + (explore if parent_node.state.actor() == 0 else -1*explore)

  return result

def traverse(root):  # traverse + expand would be more accurate.
  '''
  Input: the root of the tree, a Node object
  Output: a leaf of the current tree, a Node object

  We want to traverse it like minimax. A0 goes to node with best UCB score. A1 goes to node with the WORST UCB score. 
  '''
  current = root
  while not current.state.is_terminal():
    # print("action cache len at visit: " + str(len(current.actions_cache)))
    if len(current.actions_cache) == len(current.children):  # if fully expanded:
      # Find the UCT leaf
      UCT_values = [compute_UCT(child_node, current) for child_node in current.children]
      optimal_UCT_value = max(UCT_values) if current.state.actor() == 0 else min(UCT_values)  # decision-making
      best_children = [current.children[i] for i in range(len(UCT_values)) if UCT_values[i] == optimal_UCT_value]  # only if we have numpy...
      # Update and keep going with a random best child
      current = random.choice(best_children)  
    else:  # else not fully expanded
      # EXPAND the node by 1 child and return it, sequentially, since we assume that actions are always returned in the same order
      unvisited_successor_state = current.state.successor(current.actions_cache[len(current.children)])
      successor_node = Node(state=unvisited_successor_state, parent=current)
      current.children.append(successor_node)
      return successor_node
    
  # Return the terminal leaf
  return current

def simulate(leaf):
  '''
  Input: a leaf of the current tree, a Node object
  Output: a numerical scalar, the payoff for player 0 at a terminal state
  '''
  if not leaf.state.is_terminal():
    current_state = leaf.state.successor(random.choice(leaf.actions_cache))
    # Play until we reach a terminal state
    while not current_state.is_terminal():
      # Using uniformly random playout for now.
      random_action = random.choice(current_state.get_actions())  # pick a random action
      current_state = current_state.successor(random_action)  # move onto the next state
  else:
    current_state = leaf.state
  
  # Return the payoff 
  return current_state.payoff()

def update(leaf, terminal_reward):
  '''
  Input: 
    leaf - a leaf of the current tree, a Node object
    terminal_reward - a numerical scalar, the payoff for player 0 at a terminal state returned from playout
  '''
  current = leaf
  # Traverse until we finishes with Root (root has no parent)
  while current:  # None is false
    # Update the statistics
    current.visit_count += 1
    current.total_reward += terminal_reward  # accumulate w.r.t P0 UNBIASED.

    # Backprop up
    current = current.parent

def best_action(root):
  '''
  Input: the root of the tree, a Node object
  Output: a State.action object, indicating the best action to take from the root.
  '''
  # Get the visit counts of children
  # visit_counts = [child_node.visit_count for child_node in root.children]
  if not root.children:  # Check if there are no children; non of the children expanded, potentially due to budget constraint.
    # Fallback: Return a random move or a predefined default move
    return random.choice(root.actions_cache) if root.actions_cache else None
  # print("Root action cache: " + str(root.actions_cache))
  # print("Root children" + str(root.children))
  # print("Root status: " + str(root.state.is_terminal()))
  # Trying best Mean Reward (it's doing about the same as visit count?)
  mean_rewards = [child_node.total_reward / child_node.visit_count for child_node in root.children]
  # Player 0 makes the first move. Player 1 makes the second move. Reward is always in P0's perspective
  # You want to act like how the opponent would play at their node.
  optimal_move = root.actions_cache[max(range(len(mean_rewards)), key=lambda i: mean_rewards[i])] if root.state.actor() == 0 else \
                 root.actions_cache[min(range(len(mean_rewards)), key=lambda i: mean_rewards[i])]

  return optimal_move