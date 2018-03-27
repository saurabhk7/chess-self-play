from collections import deque
from Arena import Arena
from MCTS import MCTS
import numpy as np
from pytorch_classification.utils import Bar, AverageMeter
import time, os, sys
from pickle import Pickler, Unpickler
from random import shuffle
from chess.pythonchess import chess as chess


class Coach():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """
    def __init__(self, game, nnet, args):
        self.game = game #object of OthelloGame
        self.nnet = nnet
        self.pnet = self.nnet.__class__(self.game)  # the competitor network - parent network(to validate selfplay model after learning)
        self.args = args
        self.mcts = MCTS(self.game, self.nnet, self.args) #returns the MCTS object
        self.trainExamplesHistory = []    # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.skipFirstSelfPlay = False # can be overriden in loadTrainExamples()

    def executeEpisode(self): #one episode is one physical move on the board
        """
        This function executes one episode of self-play, starting with player 1.
        As the game is played, each turn is added as a training example to
        trainExamples. The game is played till the game ends. After the game
        ends, the outcome of the game is used to assign values to each example
        in trainExamples.

        It uses a temp=1 if episodeStep < tempThreshold, and thereafter
        uses temp=0.

        Returns:
            trainExamples: a list of examples of the form (canonicalBoard,pi,v)
                           pi is the MCTS informed policy vector, v is +1 if
                           the player eventually won the game, else -1.
        """
        print ('Coach.py ==>executeEpisode')
        trainExamples = []
        board = self.game.getInitBoard()
        print ('chessboard chess-pgn object: ', board)
        print('-----------************----------')
        self.curPlayer = 1
        episodeStep = 0

        while True:
            episodeStep += 1
            print ('Coach.py ==>executeEpisode ', 'board: ', board, 'self.curPlayer: ', self.curPlayer)
            canonicalBoard = self.game.getCanonicalForm(board,self.curPlayer) #gets the canonical board
            print ('Coach.py ==>executeEpisode ', 'canonicalBoard: ', canonicalBoard) #canonical = player*board matrix

            temp = int(episodeStep < self.args.tempThreshold) #tempThreshold: 15
            #temp is the temperature and controls the degree of exploration.
            #temp = 1 till num eps == 15 (threshold, simply the normalised counts) after that,
            #temp = 0 (picking the move with the maximum counts) (greedy)

            pi = self.mcts.getActionProb(canonicalBoard, temp=temp) #gets action probabilties
            pin = 0
            for p in pi:
                if p:
                    print("IND: ", pin, "PI: ", p)
                pin+=1
            sym = self.game.getSymmetries(canonicalBoard, pi)
            # print ('Coach.py ==>executeEpisode ', 'probability pi: ', pi, 'Symmetries sym: ', sym)

            # for b,p in sym:
            #     trainExamples.append([b, self.curPlayer, p, None])
            for b,p in sym:
                X = np.array([self.bb2array(b)])
                matrix2d = self.vector2matrix(X[0])

                trainExamples.append([matrix2d, self.curPlayer, p, None])
            action = np.random.choice(len(pi), p=pi) #Generates a random sample from a given 1-D array
            print ('Coach.py ==>executeEpisode ', 'action: ', action)

            #NOW MAKE THE ACTUAL PHYSICAL SUPER DUPER FINAL MOVE of MCTS by analysing MCTS

            board, self.curPlayer = self.game.getNextState(board, self.curPlayer, action)
            print("FINAL SELECTED MOVE NEW BOARD: ", board, "TURN: ", board.turn)
            r = self.game.getGameEnded(board, self.curPlayer)

            if r!=0:
                print("r: ", r)
                print ('Coach.py ==>executeEpisode ', 'returns: ')#, [(x[0],x[2],r*((-1)**(x[1]!=self.curPlayer))) for x in trainExamples])
                return [(x[0],x[2],r*((-1)**(x[1]!=self.curPlayer))) for x in trainExamples]

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximium length of maxlenofQueue).
        It then pits the new neural network against the old one and accepts it
        only if it wins >= updateThreshold fraction of games.
        """

        for i in range(1, self.args.numIters+1): #numIters = 1
            # bookkeeping
            print('------ITER ' + str(i) + '------')
            # examples of the iteration
            if not self.skipFirstSelfPlay or i>1:
                print ('Coach.py==>learn ', 'self.skipFirstSelfPlay: ', self.skipFirstSelfPlay)
                iterationTrainExamples = deque([], maxlen=self.args.maxlenOfQueue)

                eps_time = AverageMeter()
                bar = Bar('Self Play', max=self.args.numEps)
                end = time.time()

                for eps in range(self.args.numEps): #number of epochs=2
                    self.mcts = MCTS(self.game, self.nnet, self.args)   # reset search tree
                    iterationTrainExamples += self.executeEpisode()
                    # print ('Coach.py==>learn ', 'added to iterationTrainExamples deque self.executeEpisode(): ', self.executeEpisode())

                    # bookkeeping + plot progress :surag
                    eps_time.update(time.time() - end)
                    end = time.time()
                    bar.suffix  = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps+1, maxeps=self.args.numEps, et=eps_time.avg,
                                                                                                               total=bar.elapsed_td, eta=bar.eta_td)
                    bar.next()
                bar.finish()

                # save the iteration examples to the history
                self.trainExamplesHistory.append(iterationTrainExamples)

            if len(self.trainExamplesHistory) > self.args.numItersForTrainExamplesHistory: #numItersForTrainExamplesHistory:
                # print('Coach.py==>learn ',' BEFORE REMOVING self.trainExamplesHistory: ', self.trainExamplesHistory)
                # print("len(trainExamplesHistory) =", len(self.trainExamplesHistory), " => remove the oldest trainExamples")
                self.trainExamplesHistory.pop(0)
                # print('Coach.py==>learn ',' AFTER REMOVING self.trainExamplesHistory: ', self.trainExamplesHistory)

            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)
            self.saveTrainExamples(i-1)

            # shuffle examlpes before training
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e)
            shuffle(trainExamples)

            # training new network, keeping a copy of the old one
            self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            self.pnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            pmcts = MCTS(self.game, self.pnet, self.args)

            self.nnet.train(trainExamples)
            nmcts = MCTS(self.game, self.nnet, self.args)

            print('PITTING AGAINST PREVIOUS VERSION')
            arena = Arena(lambda x: np.argmax(pmcts.getActionProb(x, temp=0)),
                          lambda x: np.argmax(nmcts.getActionProb(x, temp=0)), self.game)
            pwins, nwins, draws = arena.playGames(self.args.arenaCompare)

            print('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))
            if pwins+nwins > 0 and float(nwins)/(pwins+nwins) < self.args.updateThreshold:
                print('REJECTING NEW MODEL')
                self.nnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            else:
                print('ACCEPTING NEW MODEL')
                self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=self.getCheckpointFile(i))
                self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='best.pth.tar')

    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration):
        folder = self.args.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration)+".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory)
        f.closed

    def loadTrainExamples(self):
        modelFile = os.path.join(self.args.load_folder_file[0], self.args.load_folder_file[1])
        examplesFile = modelFile+".examples"
        if not os.path.isfile(examplesFile):
            print(examplesFile)
            r = input("File with trainExamples not found. Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            print("File with trainExamples found. Read it.")
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory = Unpickler(f).load()
            f.closed
            # examples based on the model were already collected (loaded)
            self.skipFirstSelfPlay = True

    def bb2array(self, b): #board to vector of len 64
    	x = np.zeros(64, dtype=np.int8)
    	#print('Flipping: ', flip)
    	for pos in range(64):
    		piece = b.piece_type_at(pos) #Gets the piece type at the given square. 0==>blank,1,2,3,4,5,6
    		if piece :
    			color = int(bool(b.occupied_co[chess.BLACK] & chess.BB_SQUARES[pos])) #to check if piece is black or white
    			#print ('piece: ', piece, 'b.occupied_co[chess.BLACK]: ', b.occupied_co[chess.BLACK], 'chess.BB_SQUARES[pos]: ', chess.BB_SQUARES[pos], 'color: ', color, 'pos: ', pos, '\t', b.occupied_co[chess.BLACK] & chess.BB_SQUARES[pos])
    			col = int(pos % 8)
    			row = int(pos / 8)
    	#		if flip:
    	#		row = 7-row
    	#		color = 1 - color
    			x[row * 8 + col] = -piece if color else piece
    	t = b.turn
    	c = b.castling_rights
    	e = b.ep_square
    	h = b.halfmove_clock
    	f = b.fullmove_number
    	return x
    def vector2matrix(self, x):
        y = np.reshape(x, (8,8))
        return y
