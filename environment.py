"""Framework for a tic-tac-toe game

File is organized into 2 classes:
1) Game() governs the physical state of game board (e.g. how the size
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
	
	Arguments:
		strategy: one of a set number of strategies that the player will use
			to take an action (decide on a move in the game)
		learning_rate: rate from 0-1 that affects how malleable the Q learner
			is in the current game. Lower rates will weight the Q-learner's
			existing weights more heavily than the feedback from the current 
			game, while higher rates will move Q rates more significantly.
		epsilon: starting exploration factor. This determines the likelihood
			that a Q-leaner will make a random move instead of using its 
			Q-strategy (higher epsilon -> more likelihood of making random move)
		learning: boolean that determines whether or not the player should 
			update its Q strategy over time. Set to False when testing (this will
			also set epsilon to 0)
		load_Q: boolean that determines if the player should start with an 
			existing Q strategy
		q_file: filepath for loading Q strategy from a pickled file
		sign: "X" or "O" representing player's positions on the board

	This class represents a player and its chosen strategy, which will 
	dictate how it plays tictactoe. This is also where the learning happens
	as the player takes training inputs and updates its strategy over time
	to improve its chance of winning.
	"""

	def __init__(self, strategy="random", learning_rate=.5, epsilon=.9, learning=False, load_Q=False, q_file = "saved_q.p", sign=None):
		self.strategy = strategy
		self._Q = self._load_Q(q_file) if load_Q else {}
		self._learning = learning
		self._learning_rate = learning_rate
		self._epsilon = 0 if not learning else epsilon
		self.sign = sign
		self.q_file = q_file

	def _load_Q(self, q_file):
		# load Q from a pickled file
		with open(q_file, "rb") as f:
			self._Q = pickle.load(f)
			return self._Q

	def _write_Q(self, q_file):
		# pickle Q, write file and save for future use
		with open(q_file, "wb") as f:
			pickle.dump(self._Q, f)

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
			# use Q file to determine optimal policy, with some chance epsilon of taking a random action
			
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
	    
		elif self.strategy == "adversarial":
			# load dictionary with specific moves to make for adversarial examples
			state = tuple(board.flatten())
			if state in self._Q:
				action = self._Q[state]
			else:
				action = random.choice(valid_actions)
		return action

	def update_q(self, game_outcome, decisions):
    	# after a game is played, this will back propogate the results
    	# to update the Q-learner, with a discount for early moves

    	# determine reward
		reward = {"won":1,"tied":0,"lost":-1}[game_outcome]
    	# we should have a list of several (state,action) decisions taken during game
    	# find those and update Q values based on reward

		for state, action in decisions:
			old_q = self._Q[state][action]
			new_q = (1-self._learning_rate) * old_q + self._learning_rate * reward
			self._Q[state][action] = new_q

class Game(object):
	""" Controls the physical board and game mechanics
	
	Arguments:
		p1: player 1 ("X")
		p2: player 2 ("O")
		size: int representing length and width of game board
		verbose: prints game positions to the terminal as the game happens,
			which is very useful for debugging but slows down training.

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
		self._verbose = verbose
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
		# sets winner and outcome (win, loss, tie, or None) from P1's POV
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
		"""Run a single tic tac toe game, P1 vs. P2

		Returns:
			outcome: won, lost, or tied (from P1's perspective)
			x_decisions: player 1's (state,action) decisions during the game
			o_decisions: player 2's (state,action) decisions during the game
		"""
		self._reset_board()

		# log player X's (state,action) decisions
		x_decisions = []

		# log player O's (state,action) decisions
		o_decisions = []

		# randomly determine who goes first
		turn = self.p1 if random.random() <=.5 else self.p2
		if self._verbose:
			print "New game. %s will go first" %turn.sign
		while self.outcome == None:
			action = turn.choose_action(self.board,self.valid_actions)
			if turn.sign == "X":
				x_decisions.append((self.flat_board,action))
			elif turn.sign == "O":
				o_decisions.append((self.flat_board,action))
			self._update_board(turn, action)
			self._check_for_winner()
			# change turns
			turn = self.p1 if turn == self.p2 else self.p2
		if self._verbose:
			if self.outcome=="tied":
				print "Game ended in a tie"
			else:
				print "Player %s won!" %self.winner
		return self.outcome, x_decisions ,o_decisions

