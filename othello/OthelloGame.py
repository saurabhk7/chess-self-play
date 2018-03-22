from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .OthelloLogic import Board
import numpy as np


class OthelloGame(Game):
    def __init__(self, n):
        self.n = n #n is the size of the square board (n=6)

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board(self.n)
        return np.array(b.pieces)

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.n)

    def getActionSize(self):
        # return number of actions
        return self.n*self.n + 1

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        print('OthelloGame==>getNextState ','param action number: ', action, 'self.n*self.n: ', self.n*self.n)
        if action == self.n*self.n: #it means there is no valid action possible therefore just change the player
        	return (board, -player) #36+1 (valid board moves + no moves possible flag :  indexed 0-36)
        b = Board(self.n)
        b.pieces = np.copy(board)
        move = (int(action/self.n), action%self.n) #to convert the wrapped around vector index to 2D matrix(board) index
        print('OthelloGame==>getNextState ','move: ', str(move),'action/self.n: ', int(action/self.n), 'action%self.n: ', action%self.n)

        b.execute_move(move, player)
        return (b.pieces, -player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        print('OthelloGame.py==>getValidMoves ', 'parms: ','board: ',board, 'player: ', player)
        print('OthelloGame.py==>getValidMoves ', 'self.getActionSize(): ', self.getActionSize())

        valids = [0]*self.getActionSize()
        b = Board(self.n)
        print('OthelloGame.py==>getValidMoves ', 'Board(in OthelloLogic) Object b: ', str(b))

        b.pieces = np.copy(board)
        print('OthelloGame.py==>getValidMoves ', 'Board(in OthelloLogic) Object b.pieces: ', str(b.pieces))

        legalMoves =  b.get_legal_moves(player)
        print('OthelloGame.py==>getValidMoves ','player: ', player, 'legalMoves: ', str(legalMoves))

        if len(legalMoves)==0:
        	valids[-1]=1
        	return np.array(valids)
        for x, y in legalMoves:
        	valids[self.n*x+y]=1
        print('OthelloGame.py==>getValidMoves ','returns: valids array: ', str(np.array(valids)))
        return np.array(valids)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        print('OthelloGame.py==>getGameEnded ', 'parms: ','board: ',board, 'player: ', player)
        b = Board(self.n)
        b.pieces = np.copy(board)
        if b.has_legal_moves(player):
            return 0
        if b.has_legal_moves(-player):
        	return 0
        if b.countDiff(player) > 0:
        	return 1
        return -1

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        print('OthelloGame.py==>getCanonicalForm ', 'parms: ','board: ',board, 'player: ', player)
        print('OthelloGame.py==>getCanonicalForm ', 'returns: ','player*board: ',player*board)
        return player*board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        assert(len(pi) == self.n**2+1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.n, self.n))
        l = []

        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l

    def stringRepresentation(self, board):
    	# 8x8 numpy array (canonical board)
        print('OthelloGame.py==>stringRepresentation ', 'returns: ','board.tostring() ')
        return board.tostring()

    def getScore(self, board, player):
        b = Board(self.n)
        b.pieces = np.copy(board)
        return b.countDiff(player)

def display(board):
    n = board.shape[0]

    for y in range(n):
        print (y,"|",end="")
    print("")
    print(" -----------------------")
    for y in range(n):
        print(y, "|",end="")    # print the row #
        for x in range(n):
            piece = board[y][x]    # get the piece to print
            if piece == -1: print("b ",end="")
            elif piece == 1: print("W ",end="")
            else:
                if x==n:
                    print("-",end="")
                else:
                    print("- ",end="")
        print("|")

    print("   -----------------------")
