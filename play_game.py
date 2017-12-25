from environment import *

def human_vs_cpu():
	game = Game(p1 = Player("X","ai"), p2 = Player("O","human"))
	game.play_game()

human_vs_cpu()
