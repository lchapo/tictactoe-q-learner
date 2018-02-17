from collections import Counter
import cPickle as pickle
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from env import Player, Game

def train_learner(
	n_games=1000,
	p1 = Player(strategy="basic_q", learning=True),
	p2 = Player(strategy="random", learning=False),
	save_Q = False,
):
	
	games = [Game(p1=p1,p2=p2) for i in range(n_games)]
	metrics = []
	index = 0
	starting_epsilon = p1._epsilon

	for game in games:
		index += 1

		# run game and get results + P1's states and actions
		outcome, decisions = game.play_game()
		
		# log results
		metrics.append(outcome)

		# update q learner after each game
		if p1._learning:
			p1.update_q(outcome, decisions)

			# reduce exploration factor after each game
			p1._epsilon = starting_epsilon - starting_epsilon * (1.*index/n_games)**2

	print Counter(metrics)

	# save pickled Q learning file
	if save_Q:
		pickle.dump(p1._Q, open( "save.p", "wb" ))
	return metrics

def visualize_win_ratio(metrics, title="Performance Over Time"):
	# shows w/t/l ratio over time

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
	metrics = train_learner(save_Q = True)
	visualize_win_ratio(metrics,"Performance Over Time (training)")

def test_rando_against_rando():
	# primarily intended for testing and catching bugs
	# we instantiate 2 different players but they should be equally (un)skilled
	# so we expect even results
	metrics = train_learner(
		p1 = Player(strategy="basic_q", learning=False, load_Q = False),
		p2 = Player(strategy="random")
	)
	visualize_win_ratio(metrics,"Performance Over Time (testing)")

def test_learner_against_rando():
	metrics = train_learner(
		p1 = Player(strategy="basic_q", learning=False, load_Q = True),
		p2 = Player(strategy="random")
	)
	visualize_win_ratio(metrics,"Performance Over Time (testing)")

def test_learner_against_self():
	# another one meant for bug catches: results should be even
	metrics = train_learner(
		p1 = Player(strategy="basic_q", learning=False, load_Q=True,),
		p2 = Player(strategy="basic_q", learning=False, load_Q = True),
	)
	visualize_win_ratio(metrics,"Performance Over Time (testing)")

def test_learner_against_human():
	p1 = Player(strategy="basic_q",load_Q=True)
	p2 = Player(strategy="human")
	game = Game(p1=p1,p2=p2,verbose=True)
	game.play_game()

def train_learner_against_self(n_sessions=5):
	# trains a learner against itself over n_games
	# then trains against a new version of itself, etc. for n_sessions
	for n in range(n_sessions):
		train_learner(
			n_games = 10000,
			p1 = Player(strategy="basic_q", learning=True, load_Q=True),
			p2 = Player(strategy="basic_q", learning=False, load_Q = True),
		 	save_Q = True,
		)
		print "%d training sessions completed out of %d" %(n+1,n_sessions)

#train_from_scratch()
#test_rando_against_rando()
#test_learner_against_rando()
#test_learner_against_self()
#test_learner_against_human()
#train_learner_against_self()
