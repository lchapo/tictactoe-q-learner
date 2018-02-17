"""framework for a tic-tac-toe game

file is organized into 2 classes:
1) Board() governs the physical state of game board (e.g. how the size
	of the game board and current player positions) and the mechanics of
	gameplay.
2) Player() represents a human or AI player. For AI players, this class
	is where the learning happens and where a strategic decision is made.
"""

import cPickle as pickle
import itertools
import numpy as np
import pandas as pd
import random

class Player(object):
	""" Represents a player (human or AI)
	
	This class represents a player and its chosen strategy, which will 
	dictate how it plays tictactoe. This is also where the learning happens
	as the player takes training inputs and updates its strategy over time
	to improve its chance of winning.
	"""

	def __init__(self, strategy="random", learning_rate=.5, epsilon=.9, learning=False, load_Q=False, sign=None):
		self.strategy = strategy
		if load_Q:
			self._Q = pickle.load(open( "save.p", "rb" ))
		else:
			self._Q = {} # this will hold state:action:reward
		self._learning = learning
		self._learning_rate = learning_rate
		self._epsilon = 0 if not learning else epsilon
		self.sign = sign

	def choose_action(self, board, valid_actions):
		""" Takes in the current board state and returns an action
		
		This could be manual input in the case of a human player, or it could
		be an AI input which is based on the player's strategy.
		
		Inputs are the physical board state (X, O, and blank positions) as
		well as the set of valid actions allowed by the game's mechanics.

		Returns an action in tuple form representing the row and column where
		the player decides to play (starting with 0). 
		"""
		if self.strategy=="random":
			action = random.choice(valid_actions)
		elif self.strategy=="human":
			action = input("Enter move as row,col: ")
		elif self.strategy=="basic_q":
			# uses Q learning to determine optimal policy, with some chance epsilon of taking a random action
			
			# compress board into 1D tuple
			state = tuple(board.flatten())

			# if sign is O (in the case of self play), flip board input since it's only been trained as the "X" player
			if self.sign == "O":
				# first swap Xs and Os
				board = np.char.replace(board, ["X"], ["L"])
				board = np.char.replace(board, ["O"], ["X"])
				board = np.char.replace(board, ["L"], ["O"])

				# now get the swapped state
				state = tuple(board.flatten())

			if state in self._Q and np.random.uniform(0,1) > self._epsilon:
				action = max(self._Q[state], key = self._Q[state].get)
			else:
				action = random.choice(valid_actions)
				if self._learning:
					if state not in self._Q:
						self._Q[state] = {}
					# give 0 initial value to this state:action pair
					self._Q[state][action] = 0
	    
		return action

	def update_q(self, game_outcome, decisions):
    	# after a game is played, this will back propogate the results
    	# to update the Q-learner, with a discount for early moves

    	# determine reward
		reward = {"won":1,"tied":0,"lost":-1}[game_outcome]

    	# we should have a list of several {state:action} decisions taken during game
    	# find those and update Q values based on reward

    	# TODO: update, incuding discounts. Check Q calculation.
		for state, action in decisions:
			old_q = self._Q[state][action]
			new_q = (1-self._learning_rate) * old_q + self._learning_rate * reward
			self._Q[state][action] = new_q

class Game(object):
	""" Controls the physical board and game mechanics
	
	Class is instantiated with two players and a blank board. The function
	play_game() controls the game mechanics and updates the board as the
	players take actions, returning a win or loss for P1.

	For simplicity, P1 is always X and the game is oriented around P1's POV
	""" 

	def __init__(self, p1=Player(), p2=Player(), size=3, verbose=False):
	# size: length/width of the board
		# create empty board
		self.size = size
		self.p1 = p1 
		self.p2 = p2
		self.p1.sign = "X"
		self.p2.sign = "O"
		self._verbose = verbose # prints info to console
		self._reset_board()

	def _reset_board(self):
		self.board = np.empty(shape=(self.size,self.size),dtype="string")
		self.board.fill("_")
		self.flat_board = self._flatten_board()
		self.winner = None
		self.outcome = None

		# define what's playable on an empty board
		self.valid_actions = list(itertools.product(range(self.size),range(self.size)))

	def _update_board(self,player,action):
		if self._verbose:
			print "%s chooses %s" %(player.sign,str(action))
		if action in self.valid_actions:
			self.board[action[0]][action[1]] = player.sign
			self.valid_actions.remove(action)
		else:
			if self._verbose:
				print "Invalid action. Lose a turn"
		if self._verbose:
			print self.board
		# also update flat version of the board
		self.flat_board = self._flatten_board()

	def _flatten_board(self):
		# returns 1D version of the board
		return tuple(self.board.flatten())

	def _check_for_winner(self):
		# get counts of X's and O's by column, row, and diagonals
		# sets winner and outcome (win, loss, tie, or None)
		for sign in ["X","O"]:
			counts = [np.count_nonzero(self.board[:,i] == sign) for i in range(self.size)]
			counts += [np.count_nonzero(self.board[i,:] == sign) for i in range(self.size)]
			counts += [np.count_nonzero(np.diag(self.board) == sign)]
			counts += [np.count_nonzero(np.diag(np.fliplr(self.board)) == sign)]
			if self.size in counts:
				self.winner = sign
		if self.winner == "X":
			self.outcome = "won"
		elif self.winner == "O":
			self.outcome = "lost"
		elif len(self.valid_actions) == 0:
			self.outcome = "tied"

	def play_game(self):
		# run full tictactoe game
		self._reset_board()

		# log player X's (state,action) decisions
		x_decisions = []

		# randomly determine who goes first
		turn = self.p1 if random.random() <=.5 else self.p2
		if self._verbose:
			print "New game. %s will go first" %turn.sign
		while self.outcome == None:
			action = turn.choose_action(self.board,self.valid_actions)
			if turn.sign == "X":
				x_decisions.append((self.flat_board,action))
			self._update_board(turn, action)
			self._check_for_winner()
			# change turns
			turn = self.p1 if turn == self.p2 else self.p2
		if self._verbose:
			if self.outcome=="tied":
				print "Game ended in a tie"
			else:
				print "Player %s won!" %self.winner
		return self.outcome, x_decisions

