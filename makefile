TestRummy:
	echo "#!/bin/bash" > TestRummy
	echo "echo 'SimpleGreedyPolicyBASE vs. BaseMCTSPolicy (5 iterations)'" >> TestRummy
	echo "python3 test_agents.py --agent1 1 --agent2 3 --count 5" >> TestRummy
	echo "" >> TestRummy
	echo "echo 'HeuristicPolicyBASE vs. BaseMCTSPolicy (5 iterations)'" >> TestRummy
	echo "python3 test_agents.py --agent1 2 --agent2 3 --count 5" >> TestRummy
	echo "" >> TestRummy
	echo "echo 'SimpleGreedyPolicyBASE vs. AdvanceMCTSPolicy (5 iterations)'" >> TestRummy
	echo "python3 test_agents.py --agent1 1 --agent2 4 --count 5" >> TestRummy
	echo "" >> TestRummy
	echo "echo 'HeuristicPolicyBASE vs. AdvanceMCTSPolicy (5 iterations)'" >> TestRummy
	echo "python3 test_agents.py --agent1 2 --agent2 4 --count 5" >> TestRummy
	chmod u+x TestRummy

clean:
	rm -f TestRummy