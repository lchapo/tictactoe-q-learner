"""Functions to trains and/or test a Q-learner

Using Player() and Game() classes from environment, this file contains
helper functions to train and test the Q-learner.
"""

from collections import Counter
import cPickle as pickle
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from environment import Player, Game

def run_simulator(
	n_games=1000,
	p1 = Player(strategy="basic_q", learning=True),
	p2 = Player(strategy="random", learning=False),
	save_Q = False,
):
	"""Runs a number of tic tac toe games
	
	Arguments:
		n_games: number of tic tac toe games to be played
		p1: instance of the Player() class, should be used to specify the AI
			during training or testing
		p2: instance of the Player() class, should be used to specify the
			opponent
		save_Q: boolean, determines if p1's updated Q should be saved in a
			pickled file after training is complete

	Returns:
		metrics: dict of P1's wins, losses, and ties

	Use this function to run many games in a row. Depending on the 
	parameters for P1 and P2, this could be used for training or testing.
	This function also specifies the epsilon (exploration factor) decay
	over time as the learner moves from high exploration to low.
	"""
	games = [Game(p1=p1,p2=p2) for i in range(n_games)]
	metrics = []
	index = 0
	starting_epsilon = p1._epsilon

	for game in games:
		index += 1

		# run game and get results + P1's states and actions
		outcome, x_decisions, o_decisions = game.play_game()
		
		# log game results
		metrics.append(outcome)

		# update q learner after each game
		if p1._learning:
			p1.update_q(outcome, x_decisions)

			# reduce exploration factor after each game
			p1._epsilon = starting_epsilon - starting_epsilon * (1.*index/n_games)**2

	print Counter(metrics)

	# save pickled Q learning file
	if save_Q:
		pickle.dump(p1._Q, open( p1.q_file, "wb" ))
	return metrics

def visualize_win_ratio(metrics, title="Performance Over Time"):
	"""Shows win/loss/tie ratio over time
	
	Arguments:
		metrics: dictionary of wins, losses, and ties
		title: plot title

	Function plots the wins, losses, and ties it receives on a log scale
	"""

	# choose # intervals over time to plot
	num_chunks = 10

	logspace = np.logspace(1, math.log10(10000), num=num_chunks, dtype=int)

	# show data at 100 game minimum, otherwise it's too noisy
	logspace = [max(100+2*i,i) for i in logspace]
	d = [dict(Counter(metrics[:i])) for i in logspace]
	data = pd.DataFrame(d,index=logspace)
	# index represents games played

	# We need to transform the data from raw data to percentage (fraction)
	data_perc = data.divide(data.sum(axis=1), axis=0)
	 
	# Make the plot
	plt.stackplot(
	    data.index,
	    data_perc["lost"] if "lost" in data_perc else np.zeros(data_perc.shape[0]),
	    data_perc["tied"] if "tied" in data_perc else np.zeros(data_perc.shape[0]),
	    data_perc["won"] if "won" in data_perc else np.zeros(data_perc.shape[0]),
	    labels=['lost','tied','won'],
	    colors=['coral','silver','turquoise']
	)
	plt.legend(frameon=True,labelspacing=-2,bbox_to_anchor=(1, 1),borderpad=2.5)
	plt.margins(0,0)
	plt.xlabel("games played")
	plt.ylabel("outcome ratios for AI player")
	plt.xscale("log")
	plt.title(title)
	plt.show()
	return None

# shortcut functions to do various learning and testing

def train_from_scratch():
	# start untrained, play against a random strategy, and save results
	metrics = run_simulator(save_Q = True)
	visualize_win_ratio(metrics,"Performance Over Time (training)")

def train_learner_against_rando(n_games=20000):
	# load existing Q strategy and trains more against random strategy
	metrics = run_simulator(
		p1 = Player(strategy="basic_q", learning=True, load_Q = True),
		p2 = Player(strategy="random"),
		save_Q=True,
		n_games=n_games,
	)
	visualize_win_ratio(metrics,"Performance Over Time (testing)")

def train_learner_against_self(n_sessions=5, games_per_session=10000):
	"""Train a learner against itself
	
	Loads Q file for both P1 and P2. Learner (P1) starts with a high
	exploration factor that decays over time, while P2 uses no exploration
	factor. P1 updates its Q file over the course of *games_per_session*.

	After *games_per_session* have been played, P2 then updates its Q
	strategy to match P1's again, and the process continues iteratively for
	*n_sessions*
	""" 
	for n in range(n_sessions):
		run_simulator(
			n_games = games_per_session,
			p1 = Player(strategy="basic_q", learning=True, load_Q=True),
			p2 = Player(strategy="basic_q", learning=False, load_Q=True),
		 	save_Q = True,
		)
		print "%d training sessions completed out of %d" %(n+1,n_sessions)

def test_learner_against_rando(n_games=1000000):
	# see how learner performs against a player making random moves
	metrics = run_simulator(
		p1 = Player(strategy="basic_q", learning=False, load_Q = True),
		p2 = Player(strategy="random"),
		n_games=n_games,
	)
	visualize_win_ratio(metrics,"Performance Over Time (testing)")

def test_learner_against_self():
	# see how the leaner performs against itself; results should be even
	metrics = run_simulator(
		p1 = Player(strategy="basic_q", learning=False, load_Q=True,),
		p2 = Player(strategy="basic_q", learning=False, load_Q = True),
	)
	visualize_win_ratio(metrics,"Performance Over Time (testing)")

def test_learner_against_human():
	# tests Q-learner against human player ("O")
	p1 = Player(strategy="basic_q",load_Q=True)
	p2 = Player(strategy="human")
	game = Game(p1=p1,p2=p2,verbose=True)
	game.play_game()

def adversarial_training(
    p1 = Player(strategy="basic_q", learning=False, load_Q=True),
    p2 = Player(strategy="random", learning=False),
    p3 = Player(strategy="basic_q", learning=True, load_Q=True),
    p4 = Player(strategy="adversarial", learning=False),
):
	"""Finds strategies that beat the AI for targeted training

	Arguments:
		p1: trained Q-learner in "test mode" (no learning)
		p2: cpu player choosing random moves
		p3: trained Q-leaner that will continue to train
		p4: p3's opponent, uses saved strategy uncovered by p2 that beat p1

	Plays a trained AI against a random player until (if) the random player
	wins. If the random player does win, it will save that strategy in its
	own Q file. It will then play this adversarial scenario many times so
	that the AI can learn a better strategy.

	Training is very specific and deep (many repetitions), so this is not
	meant to be a general training strategy and is best used after the AI
	is already sufficiently robust. Each time this function runs will only
	cover one adversarial example, so it may need to be run many times.
	"""
    
    # phase 1: AI vs. random opponent
	max_games = 50000
	games = [Game(p1=p1,p2=p2) for i in range(max_games)]
    
	for game in games:

        # run game and get results + P1's states and actions
		outcome, x_decisions, o_decisions = game.play_game()

        # build a Q network for player O only where X lost
		if outcome == "lost":

        	# phase 2: adversarial training
			print "AI lost. Playing adversarial games..."
			Q_adversarial = {board:action for board,action in o_decisions}
			num_games = 10000
			a_games = [Game(
                p1=p3,
                p2=p4,
            ) for i in range(num_games)]

			starting_epsilon = p3._epsilon

			a_index = 0
			a_metrics = []
			for game in a_games:
				p4._Q = Q_adversarial
				a_index += 1
				outcome, x_decisions, o_decisions = game.play_game()
				a_metrics.append(outcome)
				p3.update_q(outcome, x_decisions)
				p3._epsilon = starting_epsilon - starting_epsilon * (1.*a_index/num_games)**2

			print "Adversarial game outcomes:\n"
			print Counter(a_metrics)
            
			print "Building better, stronger Q..."
			pickle.dump(p3._Q, open( p3.q_file, "wb" ))
            
            # end training
			return
	print "played %d games without losing!" %max_games

def human_vs_human():
	Game(p1=Player(strategy="human"),p2=Player(strategy="human"),verbose=True).play_game()
