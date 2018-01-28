"""framework for a tic-tac-toe game

file is organized into 3 classes:
1) Board() governs the physical state of game board (e.g. how the size
	of the game board and current player positions).
2) Player() represents a human or AI player. This class contains
	attributes such as the sign (traditionally "X" or "O") as well as an
	interface for a player to make a move.
3) Game() governs the rules of gameplay and relies on a composition of a
	board and two (or more) players. This class is where basic gameplay
	rules are defined, such as who goes first, which actions are valid,
	and when the game ends.

"""

import itertools
import numpy as np
import pandas as pd
import random
mapping = {"_":0,"O":1,"X":2} # for mapping strings to numerics

class Board(object):
	# class relating to the game board and its physical state
	def __init__(self, size=3, o_positions = None, x_positions=None):
	# size: length/width of the board
		# create empty board
		self.size = size
		self._reset_board()
		self.players = ["X","O"] #TODO: replace with player class

	def _reset_board(self):
		self.board = np.empty(shape=(self.size,self.size),dtype="string")
		self.board.fill("_")
		self.winner = None
		self.numeric_board = self._get_numeric_board()

		# define what's playable on an empty board
		self.valid_actions = list(itertools.product(range(self.size),range(self.size)))

	def _get_numeric_board(self):
		# translate board position into numeric states
		return np.vectorize(mapping.__getitem__)(self.board)

	def update_board(self,action,player_sign):
		print "chosen move is %s" %str(action)
		if action in self.valid_actions:
			self.board[action[0]][action[1]] = player_sign
			self.valid_actions.remove(action)
			self.numeric_board = self._get_numeric_board()
		else:
			print "Invalid action. Lose a turn"

	# consider moving to Game()
	def check_for_winner(self):
		# get counts of X's and O's by column, row, and diagonals
		for sign in self.players:
			counts = [np.count_nonzero(self.board[:,i] == sign) for i in range(self.size)]
			counts += [np.count_nonzero(self.board[i,:] == sign) for i in range(self.size)]
			counts += [np.count_nonzero(np.diag(self.board) == sign)]
			counts += [np.count_nonzero(np.diag(np.fliplr(self.board)) == sign)]
			if self.size in counts:
				self.winner = sign

	def print_board(self):
		print self.board

class Player(object):

	def __init__(self, sign, player_type="cpu", strategy=None):
		self.sign = sign # X or O, traditionally
		self.type = player_type # human, AI
		self.strategy = strategy # optional strategy using tensorflow neural net

	def choose_action(self, valid_actions, numeric_board=None):
		if self.type == "human":
			action = self._human_input_action(valid_actions)
		elif self.strategy:
			action = self._ai_action(valid_actions, numeric_board)
		else:
			action = self._choose_random_action(valid_actions)
		return action

	def _choose_random_action(self, valid_actions):
		# picks a random action out of the set of valid moves
		return random.choice(valid_actions)

	def _human_input_action(self, valid_actions):
		# asks for a terminal input to specify the move
		return input("Enter move as row,col: ")

	def _ai_action(self, valid_actions, numeric_board):
		# takes in tensorflow model to decide the move
		# also requires the current game board positions
		# game board must be numeric, not Xs and Os
		
		# choose the move that maximizes expected Q
		best_move = np.argmax(self.strategy.predict(numeric_board)[0])
		action = (best_move/3,best_move%3)
		return action

class Game(object):
	def __init__(self, board = Board(), p1 = Player("X"), p2 = Player("O")):
		self.board = board
		self.players = [p1,p2]
		
	def _reset_game(self):
		# randomly choose who goes first and clear board
		self.turn = self.players[0] if random.random() <=.5 else self.players[1]
		self.board._reset_board()

	def play_game(self):
		self._reset_game()
		# controls the mechanics of the game, returns a win or loss
		print "New game. %s will go first" %self.turn.sign
		while self.board.winner == None:
			try:
				print "\nPlayer %s's turn:" %self.turn.sign
				self.board.update_board(
					self.turn.choose_action(self.board.valid_actions, self.board.numeric_board),
					self.turn.sign,
				)
				self.board.print_board()
				self.board.check_for_winner()

				# change turns
				self.turn = self.players[1] if self.turn.sign == "X" else self.players[0]
			except IndexError:
				self.board.winner = "tie"

		# TODO: Reframe from P1's perspective (win/tie/loss)
		print "%s has won!" %self.board.winner
		return self.board.winner
