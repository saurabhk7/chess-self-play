import numpy as np


class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a]!=1:
            a = np.random.randint(self.game.getActionSize())
        return a


class HumanChessPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        # display(board)
        valid = self.game.getValidMoves(board, 1)
        for i in range(len(valid)):
            if valid[i]:
                temp1 = int(action/(self.n*self.n))
                temp2 = action%(self.n*self.n)

                #converting from 0 index to 1 index
                x1 = int(temp1/self.n)+1
                y1 = temp1%self.n+1
                x2 = int(temp2/self.n)+1
                y2 = temp2%self.n+1

                print(i, " : ",x1," ",y1," ",x2," ",y2)
        while True:
        	a = input()

        	x1,y1,x2,y2 = [int(x) for x in a.split(' ')]
        	a = (self.n*self.n)*(self.n*x1+y1)+(self.n*x2+y2) if x!= -1 else self.game.n ** 2
        	if valid[a]:
                print("Move detected!")
        		break
        	else:
        		print('Invalid')

        return a


class GreedyChessPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        valids = self.game.getValidMoves(board, 1)
        candidates = []
        for a in range(self.game.getActionSize()):
            if valids[a]==0:
                continue
            nextBoard, _ = self.game.getNextState(board, 1, a)
            score = self.game.getScore(nextBoard, 1)
            candidates += [(-score, a)]
        candidates.sort()
        return candidates[0][1]
