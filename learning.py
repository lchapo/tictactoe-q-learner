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

# use this model to run a simulation and see if it works
simulator.play_games(p1 = Player("X", strategy=model))
