"""simulates tic-tac-toe game, extensible to n size (2 dimensions)

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

class Board(object):
	# class relating to the game board and its physical state

	def __init__(self, size=3, o_positions = None, x_positions=None):
	# size: length/width of the board
		# create empty board
		self.winner = None
		self.size = size
		self._reset_board()
		self.players = ["X","O"] #TODO: replace with player class

	def _reset_board(self):
		self.board = np.empty(shape=(self.size,self.size),dtype="string")
		self.board.fill("_")

		# define what's playable on an empty board
		self.valid_actions = list(itertools.product(range(self.size),range(self.size)))

	def update_board(self,action,player_sign):
		print "chosen move is %s" %str(action)
		if action in self.valid_actions:
			self.board[action[0]][action[1]] = player_sign
			self.valid_actions.remove(action)
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

	def __init__(self, sign, player_type="human"):
		self.sign = sign # X or O, traditionally
		self.type = player_type # human, AI

	def choose_action(self, valid_actions):
		if self.type == "human":
			action = (input("Enter move as row,col: "))
		else:
			action = self._choose_random_action(valid_actions)
		return action

	def _choose_random_action(self, valid_actions):
		return random.choice(valid_actions)

class Game(object):
	def __init__(self, board = Board(), p1 = Player("X"), p2 = Player("O")):
		self.board = board

		# TODO: fix random choice of who goes first
		self.players = [p1,p2]
		self.turn = p1 if random.random() <.5 else p2
		self._change_turn = itertools.cycle(self.players).next

	def play_game(self):
		while self.board.winner == None:
			self.turn = self._change_turn()
			print "\nPlayer %s's turn:" %self.turn.sign
			self.board.update_board(
				self.turn.choose_action(self.board.valid_actions),
				self.turn.sign,
			)
			self.board.print_board()
			self.board.check_for_winner()

		print "%s has won!" %self.board.winner
