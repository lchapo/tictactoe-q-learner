"""Run many simulations of the game

"""

from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import tensorflow as tf 

from environment import Player, Board, Game

# initial test of random player vs random player
def play_games(n_games=1000, visualize_win_ratio=True, p1=Player("X"), p2=Player("O")):
	games = [Game(p1=p1, p2=p2) for i in range(n_games)]
	metrics = []
	for game in games:
		metrics.append(game.play_game())

	#TODO: change env to give w/l/t rather than doing it here
	mapping = {"X":"win","O":"loss","tie":"tie"}
	metrics = [mapping[i] for i in metrics]
	print Counter(metrics)

	if visualize_win_ratio:
		_visualize_win_ratio(metrics)

	return metrics

def _visualize_win_ratio(score_metrics):
	# shows w/t/l ratio over time

	# divide metrics into 10 parts for plotting purposes
	num_chunks = 10
	chunk = len(score_metrics) / num_chunks

	d = [dict(Counter(score_metrics[:chunk*(i+1)])) for i in range(num_chunks)]
	data = pd.DataFrame(d,index=[chunk*(i+1) for i in range(num_chunks)])
	# index represents games played

	# We need to transform the data from raw data to percentage (fraction)
	data_perc = data.divide(data.sum(axis=1), axis=0)
	 
	# Make the plot
	plt.stackplot(
	    data.index,
	    data_perc["loss"] if "loss" in data_perc else np.zeros(data_perc.shape[0]),
	    data_perc["tie"] if "tie" in data_perc else np.zeros(data_perc.shape[0]),
	    data_perc["win"] if "win" in data_perc else np.zeros(data_perc.shape[0]),
	    labels=['loss','tie','win'],
	    colors=['coral','silver','turquoise']
	)
	plt.legend(frameon=True,labelspacing=-2,bbox_to_anchor=(1, 1),borderpad=2.5)
	plt.margins(0,0)
	plt.xlabel("games played")
	plt.ylabel("outcome ratios for AI player")
	#plt.xscale("log")
	plt.title('Performance Over Time')
	plt.show()
	return None
