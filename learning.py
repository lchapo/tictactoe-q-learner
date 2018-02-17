# implement q-learning with a neural net
import numpy as np
np.random.seed(1) # seed for reproducibility

from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import RMSprop
import tensorflow as tf 
from collections import Counter

# import other python files in directory
import simulator
from environment import Player, Board, Game

# define neural net architecture
# the input layer will be the tic tac toe board after the opponent moves
# the output layer will be a choice of where to play next

model = Sequential()
model.add(Dense(32, input_shape=(3,), activation='relu'))
model.add(Dropout(0.1))
model.add(Dense(9, activation='softmax'))
rms = RMSprop()
model.compile(loss='mse', optimizer=rms)

# now that we have the model defined, we need to run some trials and collect data on how well it performs
# use this model to run a simulation and see if it works
# score = simulator.play_games(p1 = Player("X", strategy=model, epsilon=.5))
# simulator.visualize_win_ratio(score)

# reward system
def reward(outcome):
	# gives a reward based on the outcomes of the game
	rewards = {"win":1,"tie":0,"loss":-1}
	return rewards[outcome]

def update_q(state, action, reward):
	# updates the value of the neural net weights based on the reward and how many moves from the end of the game the move was made

	# discount factor (gamma)
	discount_rate = .8

	update = reward + discount_rate * maxq(state,action)
	return None



# fit model based on first 1000 games
# state is the same as numeric_board



# copied from blackjack example
# TODO: update below code
class BasicLearner(Player):
    # here we will implement a brute force Q-learning algorithm
    # without the neural network

    def __init__(self):
        #Player.__init__(self)
        super(BasicLearner, self).__init__()
        self._learning = True
        self._learning_rate = .1
        self._discount = .1
        self._epsilon = .9
        self._Q = {} # this will hold state:action:reward
	
    def get_action(self, board, valid_actions):
        # board: 2D-array of Xs and Os

        state = tuple(board.flatten())
        if state in self._Q and np.random.uniform(0,1) < self._epsilon:
            action = max(self._Q[state], key = self._Q[state].get)
        else:
            action = random.choice(valid_actions)
            if state not in self._Q:
                self._Q[state] = {}
            # give 0 initial value to this state:action pair
            self._Q[state][action] = 0

        # save this state:action pair for updating Q later
        self._last_state = state
        self._last_action = action
    
        return action    

    def update(self,new_state,reward):
        # update Q file with moves

        if self._learning:
            # get previous state and action taken
            old = self._Q[self._last_state][self._last_action]
            
            # see if we already have a Q-value for the new state
            if new_state in self._Q:
                new = self._discount * self._Q[new_state][max(self._Q[new_state], key=self._Q[new_state].get)]
            else:
                new = 0

            # update Q value for previous move
            self._Q[self._last_state][self._last_action] = (1-self._learning_rate)*old + self._learning_rate*(reward+new)



# play a single game of the basic learner vs. a random opponent
game = Game(p1=BasicLearner(), p2=Player("O"))
game._reset_game()
while game.board.winner == None:
    try:
        print "\nPlayer %s's turn:" %game.turn.sign
        game.board.update_board(
            game.turn.choose_action(game.board.valid_actions, game.board.numeric_board),
            game.turn.sign,
        )
        game.board.print_board()
        game.board.check_for_winner()

        # change turns
        game.turn = game.players[1] if game.turn.sign == "X" else game.players[0]
    except IndexError:
        game.board.winner = "tie"

# TODO: Reframe from P1's perspective (win/tie/loss)
print "%s has won!" %game.board.winner
print game.board.winner



# play some games and see if we can get a Q output
#play_games(p1=BasicLearner())




# each state has an expected value
# each state and action puts us into a new state. we can use that to get the expected value
# we could use the properties of tictactoe to 

# run a simulation of this with values store in-memory

# run a single game and store the Q-values




















































# class DeepLearner(Player):
#     # here we wil implement a neural network to learn

#     def __init__(self):
#         #Player.__init__(self)
#         super(Learner, self).__init__()
#         self._learning = True
#         self._learning_rate = .1
#         self._discount = .1
#         self._epsilon = .9
    
#         # create Keras model
#         model = Sequential()
#         model.add(Dense(32, input_shape=(3,), activation='relu'))
#         model.add(Dropout(0.1))
#         model.add(Dense(9, activation='softmax'))
#         rms = RMSprop()
#         model.compile(loss='mse', optimizer=rms)
#         self._model = model

        # update neural network weights after each move
        # we don't have to wait until the game is over to give a reward
        # instead, we can give the reward according to the Q value of
        # being in the new state

