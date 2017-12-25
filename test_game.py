"""play a single game of tictactoe

example use with command line: python test_game.py human_vs_cpu
"""

from environment import *
import argparse

# capture arguments from command line
parser = argparse.ArgumentParser(
    description="Select which game type to play"
    )

# the first argument should be the db table name and env variable prefix
parser.add_argument(
    "game_type", 
    help="db table AND env variable name (first argument)",
    type=str,
    nargs=1,
    choices=['human_vs_cpu','human_vs_human','cpu_vs_cpu'],
    )
args = parser.parse_args()
game_type = args.game_type[0]

def play_game():
	if game_type == 'human_vs_cpu':
		game = Game(p1 = Player("X","ai"), p2 = Player("O","human"))
	elif game_type == 'human_vs_human':
		game = Game(p1 = Player("X","human"), p2 = Player("O","human"))
	elif game_type == 'cpu_vs_cpu':
		game = Game(p1 = Player("X","ai"), p2 = Player("O","ai"))
	else:
		return None
	game.play_game()

play_game()
