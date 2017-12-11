# simulates tic-tac-toe game, extensible to n size (2 dimensions)
import itertools
import numpy as np
import pandas as pd
import random

class Environment(object):
	
	def __init__(self, size=3, o_positions = None, x_positions=None):
	# size: length/width of the board
		# create empty board
		self.board = np.empty(shape=(size,size),dtype="string")
		self.board.fill("_")
		
		# define what's playable on an empty board
		# an action is an integer specified as (row,column)
		# for example (0,2) or (1,1)
		self.valid_actions = list(itertools.product(range(size),range(size)))
		self.winner = None

	def check_for_winner(self):
		# TODO: update with actual rules
		if np.count_nonzero(self.board == "X") == 3:
			self.winner = "Player X"
		if np.count_nonzero(self.board == "O") == 3:
			self.winner == "Player O"

	def update_board(self,action,player_sign):
		print "action is %s" %str(action)
		print "valid actions include %s" %self.valid_actions
		assert action in self.valid_actions, "Move is not on the board!"
		assert self.board[action[0]][action[1]] == "_", "Move already taken!"
		self.board[action[0]][action[1]] = player_sign

	def print_board(self):
		print self.board

class Player(object):

	def __init__(self, sign):
		self.sign = sign # X or O, traditionally

	def request_action(self):
		action = input("Enter move as a tuple: ")
		return action

def simulate_human_game():
	player_x = Player("X")
	player_o = Player("O")
	players = ["X","O"]
	board = Environment()
	while board.winner == None:
		turn = random.choice(players)
		print "Player %s's turn:" %turn
		if turn=="X":
			board.update_board(player_x.request_action(),turn)
		else:
			board.update_board(player_o.request_action(),turn)
		board.print_board()
		board.check_for_winner()
	print "%s has won!" %self.winner

simulate_human_game()
