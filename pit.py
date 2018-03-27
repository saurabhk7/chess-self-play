import Arena
from MCTS import MCTS
from chess.ChessGame import ChessGame, display
from chess.ChessPlayers import *
# from othello.pytorch.NNet import NNetWrapper as NNet
from chess.tensorflow.NNet import NNetWrapper as NNet

import numpy as np
from utils import *

"""
use this script to play any two agents against each other, or play manually with
any agent.
"""

print ('For human moves input coordinates as "x1 y1 x2 y2" where "(x1 y1 x2 y2)" is in suggested moves ')

g = ChessGame(6)

# all players
rp = RandomPlayer(g).play
#gp = GreedyOthelloPlayer(g).play
hp = HumanOthelloPlayer(g).play

# nnet players
n1 = NNet(g)
# n1.load_checkpoint('./pretrained_models/othello/keras/','6x6_checkpoint_145.pth.tar')
# args1 = dotdict({'numMCTSSims': 50, 'cpuct':1.0})
# mcts1 = MCTS(g, n1, args1)
# n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))


#n2 = NNet(g)
#n2.load_checkpoint('/dev/8x50x25/','best.pth.tar')
#args2 = dotdict({'numMCTSSims': 25, 'cpuct':1.0})
#mcts2 = MCTS(g, n2, args2)
#n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))

arena = Arena.Arena(hp, hp, g, display=display)
print(arena.playGames(2, verbose=True))
