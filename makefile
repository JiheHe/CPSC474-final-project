TestRummy:
	echo "#!/bin/bash" > TestRummy
	echo "echo 'Group members: Jihe Nick He, Evan Lee. We are using base MCTS, bilinear MCTS, simple-greedy, and heuristical agents to play Rummy, an imperfect-information, sequential-step games. Here are some sample runs of our evaluation calls. Please refer to LOG for more details, including our actual evaluation and the statistics. They take a long time, so here is just a taste with up to 5 iterations. Run the executable directly without args needed.'" >> TestRummy
	echo "echo ''" >> TestRummy
	echo "echo 'SimpleGreedyPolicyBASE vs. BaseMCTSPolicy (5 iterations)'" >> TestRummy
	echo "python3 test_agents.py --agent1 1 --agent2 3 --count 5" >> TestRummy
	echo "echo ''" >> TestRummy
	echo "echo 'HeuristicPolicyBASE vs. BaseMCTSPolicy (5 iterations)'" >> TestRummy
	echo "python3 test_agents.py --agent1 2 --agent2 3 --count 5" >> TestRummy
	echo "echo ''" >> TestRummy
	echo "echo 'SimpleGreedyPolicyBASE vs. AdvanceMCTSPolicy (5 iterations)'" >> TestRummy
	echo "python3 test_agents.py --agent1 1 --agent2 4 --count 5" >> TestRummy
	echo "echo ''" >> TestRummy
	echo "echo 'HeuristicPolicyBASE vs. AdvanceMCTSPolicy (5 iterations)'" >> TestRummy
	echo "python3 test_agents.py --agent1 2 --agent2 4 --count 5" >> TestRummy
	chmod u+x TestRummy

clean:
	rm -f TestRummy