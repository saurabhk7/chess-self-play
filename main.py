from Coach import Coach
from othello.OthelloGame import OthelloGame as Game
from othello.keras.NNet import NNetWrapper as nn
from utils import *

args = dotdict({
    'numIters': 1, #original value: 1000
    'numEps': 2, #orginal value: 100
    'tempThreshold': 15,
    'updateThreshold': 0.6,
    'maxlenOfQueue': 200000,
    'numMCTSSims': 25,
    'arenaCompare': 40,
    'cpuct': 1,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('/dev/models/8x100x50','best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})

if __name__=="__main__":
    g = Game(6) #returns the game object (constructor)
    nnet = nn(g) #NNet class returns NNetWrapper for the game object (g)
    print('----------------------********************-----------------------*********************-----------------')
    if args.load_model:
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])

    print ('main.py==> ', 'args: ', args)
    c = Coach(g, nnet, args) #returns the Coach object with params(game_object, NeuralNet, argument values)
    if args.load_model:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()
