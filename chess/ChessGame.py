from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .ChessLogic import Board
import numpy as np
from pythonchess import chess as chess
import numpy



class ChessGame():
    """
    This class specifies the base Game class. To define your own game, subclass
    this class and implement the functions below. This works when the game is
    two-player, adversarial and turn-based.

    Use 1 for player1 and -1 for player2.

    See othello/OthelloGame.py for an example implementation.
    """

    letters = { 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5, 'f' : 6, 'g' : 7, 'h' : 8 }
    numbers = { '1' : 1, '2' : 2, '3' : 3, '4' : 4, '5' : 5, '6' : 6, '7' : 7, '8' : 8 }
    letters_inv = { 1 : 'a', 2 : 'b', 3:  'c', 4 : 'd', 5 : 'e', 6 : 'f', 7 : 'g', 8 : 'h' }

    def __init__(self, n):
        self.n = n #n is the size of the square board (n=6)
        #boardtemp = Board(n)
        #print ("Chesslogic: ",X[0])


    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board(self.n)
        #return np.array(b.pieces)
        return b.chessboard

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.n)

    def getActionSize(self):
        # return number of actions
        return ((self.n**2)*(self.n**2))
        #return self.n*self.n + 1

    def getChessMoveFormat(self, x1, y1, x2, y2):
        row1 = self.letters_inv[x1]
        row2 = self.letters_inv[x2]
        # print(row2)
        move = ""
        move += str(row1)
        move += str(y1)
        move += str(row2)
        move += str(y2)
        return move

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move

        print('ChessGame==>getNextState ','param action number: ', action, 'self.n*self.n: ', self.n*self.n)
        # if action == (self.n**2)*(self.n**2): #it means there is no valid action possible therefore just change the player
        	# return (board, -player) #36+1 (valid board moves + no moves possible flag :  indexed 0-36)
        b = Board(self.n)
        b.chessboard = board.copy()
        temp1 = int(action/(self.n*self.n))
        temp2 = action%(self.n*self.n)

        #converting from 0 index to 1 index
        x1 = int(temp1/self.n)+1
        y1 = temp1%self.n+1
        x2 = int(temp2/self.n)+1
        y2 = temp2%self.n+1
        print("selected action: ", x1,y1,x2,y2) #1 indexed
        #move = (int(action/self.n), action%self.n) #to convert the wrapped around vector index to 2D matrix(board) index
        #print('ChessGame==>getNextState ','move: ', str(move),'action/self.n: ', int(action/self.n), 'action%self.n: ', action%self.n)

        move = self.getChessMoveFormat(x1,y1,x2,y2)

        print("MOVE: ", move, " by converting: ", x1,y1,x2,y2)

        b.execute_move(move, player)
        b.chessboard = b.chessboard.mirror()
        return (b.chessboard, -player)




    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        # print('ChessGame.py==>getValidMoves ', 'parms: ','board: ',board, 'player: ', player)
        # print('ChessGame.py==>getValidMoves ', 'self.getActionSize(): ', self.getActionSize())


        valids = [0]*self.getActionSize()
        #b = Board(self.n)
        b = Board(self.n)
        b.chessboard = board.copy()
        # print('OthelloGame.py==>getValidMoves ', 'Board(in OthelloLogic) Object b: ', (b))

        #b.pieces = np.copy(board)
        # print('OthelloGame.py==>getValidMoves ', 'Board(in OthelloLogic) Object b.pieces: ', str(b.pieces))

        legalMoves =  b.get_legal_moves(player)
        # print('ChessGame.py==>getValidMoves ','player: ', player, 'legalMoves LENGTH: ', len(str(legalMoves)))

        if len(legalMoves)==0:
        	valids[-1]=1
        	return np.array(valids)

        for move in legalMoves:
            #converting 1 index to 0 index
            #and converted back
            x1 = move[0]-1
            y1 = move[1]-1
            x2 = move[2]-1
            y2 = move[3]-1
            #print(x1,y1,x2,y2)
            print ("inserting: ", x1,y1,x2,y2, " at: ", (self.n*self.n)*(self.n*x1+y1)+(self.n*x2+y2) )
            valids[(self.n*self.n)*(self.n*x1+y1)+(self.n*x2+y2)]=1
            count = 0
            for val in valids:
                if val==1 :
                    count=count+1
            print("count: ", count)
        print('OthelloGame.py==>getValidMoves ','returns: valids array: ', str(np.array(valids)))
        return np.array(valids)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        print('ChessGame.py==>getGameEnded ', 'parms: ','board: ',board, 'player: ', player)
        #b = Board(self.n)
        # b.pieces = np.copy(board)
        # if b.has_legal_moves(player):
        #     return 0
        # if b.has_legal_moves(-player):
        # 	return 0
        # if b.countDiff(player) > 0:
        # 	return 1
        # return -1
        b = Board(self.n)
        b = board.copy()
        if b.is_game_over(claim_draw=True):
            if b.result() == "1-0":
                print("current player won")
                return 1
            elif b.result() == "1/2-1/2":
                print("game draw")
                return -0.5
            elif b.result() == "0-1":
                print("opposite player won")
                return -1
            else:
                print("can_claim_threefold_repetition: ", b.can_claim_threefold_repetition())
                print("is_fivefold_repetition(): ", b.is_fivefold_repetition())
                print("can_claim_draw(): ", b.can_claim_draw())
                print("is_seventyfive_moves(): ", b.is_seventyfive_moves())
                print("can_claim_fifty_moves(): ", b.can_claim_fifty_moves())
                return -0.5
                print("b.result: ", b.result())
        else:
            print("returning 0")
            return 0

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        print('OthelloGame.py==>getCanonicalForm ', 'parms: ','board: ',board, 'player: ', player)
        #print('OthelloGame.py==>getCanonicalForm ', 'returns: ','player*board: ',player*board)
        #b = Board()
        if board.turn:
            print("if player boardturn1: ", board.turn)
            #board.turn = False
            return board
        elif not board.turn:
            print("if player boardturn2: ", board.turn)
            # board.turn = True removed mar 27
            return board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        assert(len(pi) == self.n**4)  # 1 for pass
        pi_board = np.reshape(pi, (self.n**2, self.n**2))
        l = []

        # for i in range(1, 5):
        #     for j in [True, False]:
        #         newB = np.rot90(board, i)
        #         newPi = np.rot90(pi_board, i)
        #         if j:
        #             newB = np.fliplr(newB)
        #             newPi = np.fliplr(newPi)
        #         l += [(newB, list(newPi.ravel()) + [pi[-1]])]

        l=[(board, list(pi_board.ravel())+[pi[-1]])]
        return l

    def stringRepresentation(self, board):
    	# 8x8 numpy array (canonical board)
        print('ChessGame.py==>stringRepresentation ', 'returns: ','board.tostring() ')
        print("type: ", type(board))
        X = numpy.array([self.bb2array(board)])
        #self.pieces = self.vector2matrix(X[0])
        print('X[0]', X[0])
        return str(X[0])

    def getScore(self, board, player):
        b = Board(self.n)
        b.pieces = np.copy(board)
        return b.countDiff(player)

    def bb2array(self, b): #board to vector of len 64
    	x = numpy.zeros(64, dtype=numpy.int8)
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
        y = numpy.reshape(x, (8,8))
        return y

def display(board):
    # n = board.shape[0]
    #
    # for y in range(n):
    #     print (y,"|",end="")
    # print("")
    # print(" -----------------------")
    # for y in range(n):
    #     print(y, "|",end="")    # print the row #
    #     for x in range(n):
    #         piece = board[y][x]    # get the piece to print
    #         if piece == -1: print("b ",end="")
    #         elif piece == 1: print("W ",end="")
    #         else:
    #             if x==n:
    #                 print("-",end="")
    #             else:
    #                 print("- ",end="")
    #     print("|")
    #
    # print("   -----------------------")
    print(board)
