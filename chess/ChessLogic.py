from pythonchess import chess as chess
import numpy

'''
Author: Eric P. Nichols
Date: Feb 8, 2008.
Board class.
Board data:
  1=white, -1=black, 0=empty
  first dim is column , 2nd is row:
     pieces[1][7] is the square in column 2,
     at the opposite end of the board in row 8.
Squares are stored and manipulated as (x,y) tuples.
x is the column, y is the row.
'''
class Board():

    # list of all 8 directions on the board, as (x,y) offsets
    #__directions = [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]

    letters = { 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5, 'f' : 6, 'g' : 7, 'h' : 8 }
    numbers = { '1' : 1, '2' : 2, '3' : 3, '4' : 4, '5' : 5, '6' : 6, '7' : 7, '8' : 8 }

    def __init__(self, n):
        "Set up initial board configuration."
        self.n = n
        # Create the empty board array.
        # self.pieces = [None]*self.n
        # for i in range(self.n):
        #     self.pieces[i] = [0]*self.n
        #
        # # Set up the initial 4 pieces.
        # self.pieces[int(self.n/2)-1][int(self.n/2)] = 1
        # self.pieces[int(self.n/2)][int(self.n/2)-1] = 1
        # self.pieces[int(self.n/2)-1][int(self.n/2)-1] = -1;
        # self.pieces[int(self.n/2)][int(self.n/2)] = -1;
        board = chess.Board()
        X = numpy.array([self.bb2array(board)])
        self.pieces = self.vector2matrix(X[0])
        self.chessboard = board

    # add [][] indexer syntax to the Board
    def __getitem__(self, index):
        return self.pieces[index]

    def countDiff(self, color):
        """Counts the # pieces of the given color
        (1 for white, -1 for black, 0 for empty spaces)"""
        count = 0
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==color:
                    count += 1
                if self[x][y]==-color:
                    count -= 1
        return count

    def numeric_notation(self, move):
    	#m = numpy.zeros( 4, dtype=numpy.int8)
        m=list()
        m.append(self.letters[move[0]])
        m.append(self.numbers[move[1]])
        m.append(self.letters[move[2]])
        m.append(self.numbers[move[3]])
        return m

    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color.
        (1 for white, -1 for black
        """
        allmoves = list()  # stores the legal moves.
        moves = self.chessboard.generate_legal_moves()
        for move in moves:
            notation = self.numeric_notation(str(move))
            #print("notation: ", notation)
            allmoves.append(notation)

        # Get all the squares with pieces of the given color.
        # for y in range(self.n):
        #     for x in range(self.n):
        #         if self[x][y]==color:
        #             newmoves = self.get_moves_for_square((x,y))
        #             moves.update(newmoves)
        if not self.chessboard.turn:
            self.chessboard.turn = True

        print("PLAYER : ",self.chessboard.turn, "LIST OF MOVES: ", list(allmoves))

        return list(allmoves)

    def has_legal_moves(self, color):
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==color:
                    newmoves = self.get_moves_for_square((x,y))
                    if len(newmoves)>0:
                        return True
        return False

    def get_moves_for_square(self, square):
        """Returns all the legal moves that use the given square as a base.
        That is, if the given square is (3,4) and it contains a black piece,
        and (3,5) and (3,6) contain white pieces, and (3,7) is empty, one
        of the returned moves is (3,7) because everything from there to (3,4)
        is flipped.
        """
        (x,y) = square

        # determine the color of the piece.
        color = self[x][y]

        # skip empty source squares.
        if color==0:
            return None

        # search all possible directions.
        moves = []
        for direction in self.__directions:
            move = self._discover_move(square, direction)
            if move:
                # print(square,move,direction)
                moves.append(move)

        # return the generated move list
        return moves
    def check_promotions(board, crdn):
    	# workaround for pawn promotions
    	move = chess.Move.from_uci(crdn)
    	if board.piece_at(move.from_square).piece_type == chess.PAWN:
    		if int(move.to_square/8) in [0, 7]:
    			move.promotion = chess.QUEEN # always promote to queen
    	return move

    def execute_move(self, move, color):
        """Perform the given move on the board; flips pieces as necessary.
        color gives the color pf the piece to play (1=white,-1=black)
        """

        #Much like move generation, start at the new piece's square and
        #follow it on all 8 directions to look for a piece allowing flipping.

        # Add the piece to the empty square.
        # print(move)
        # flips = [flip for direction in self.__directions
        #               for flip in self._get_flips(move, direction, color)]
        # assert len(list(flips))>0
        # for x, y in flips:
        #     #print(self[x][y],color)
        #     self[x][y] = color
        print("board: ", self.chessboard)
        print("MOOOVOVOEOE: ", move)
        position = chess.Move.from_uci(move)
        print("MOVE FROM: ", position.from_square, "MOVE TO: ", position.to_square)


        print ("TYPE BOARD:", type(self.chessboard))
        print("MOOOVOVOEOEaaaa: ", position.to_square)
        if (self.chessboard.piece_at(position.from_square)).piece_type == chess.PAWN:
            print("piece moved: PAWN")
            if int(position.to_square/8) in [0, 7]: #changed from 1,8
                position.promotion = chess.QUEEN # always promote to queen
        print("position: ", str(position))
        self.chessboard.push(chess.Move.from_uci(str(position)))

        print("board: ", self.chessboard)


    def _discover_move(self, origin, direction):
        """ Returns the endpoint for a legal move, starting at the given origin,
        moving by the given increment."""
        x, y = origin
        color = self[x][y]
        flips = []

        for x, y in Board._increment_move(origin, direction, self.n):
            if self[x][y] == 0:
                if flips:
                    # print("Found", x,y)
                    return (x, y)
                else:
                    return None
            elif self[x][y] == color:
                return None
            elif self[x][y] == -color:
                # print("Flip",x,y)
                flips.append((x, y))

    def _get_flips(self, origin, direction, color):
        """ Gets the list of flips for a vertex and direction to use with the
        execute_move function """
        #initialize variables
        flips = [origin]

        for x, y in Board._increment_move(origin, direction, self.n):
            #print(x,y)
            if self[x][y] == 0:
                return []
            if self[x][y] == -color:
                flips.append((x, y))
            elif self[x][y] == color and len(flips) > 0:
                #print(flips)
                return flips

        return []
    def bb2array(self, b): #board to vector of len 64
    	x = numpy.zeros(64, dtype=numpy.int8)
    	#print('Flipping: ', flip)
    	for pos in range(64) :
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

    @staticmethod
    def _increment_move(move, direction, n):
        # print(move)
        """ Generator expression for incrementing moves """
        move = list(map(sum, zip(move, direction)))
        #move = (move[0]+direction[0], move[1]+direction[1])
        while all(map(lambda x: 0 <= x < n, move)):
        #while 0<=move[0] and move[0]<n and 0<=move[1] and move[1]<n:
            yield move
            move=list(map(sum,zip(move,direction)))
            #move = (move[0]+direction[0],move[1]+direction[1])
