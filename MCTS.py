import math
import numpy as np

class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        self.Qsa = {}       # stores Q values for s,a (as defined in the paper)
        self.Nsa = {}       # stores #times edge s,a was visited
        self.Ns = {}        # stores #times board s was visited
        self.Ps = {}        # stores initial policy (returned by neural net)

        self.Es = {}        # stores game.getGameEnded ended for board s
        self.Vs = {}        # stores game.getValidMoves for board s

    def getActionProb(self, canonicalBoard, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS starting from
        canonicalBoard.

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """
        for i in range(self.args.numMCTSSims): #numMCTSSims: 25 -- bored factor (ref. udacity)
            self.search(canonicalBoard)

        #NOW MAKE THE ACTUAL FINAL MOVE of MCTS by analysing MCTS

        s = self.game.stringRepresentation(canonicalBoard)
        print('MCTS.py==>getActionProb self.game.stringRepresentation(canonicalBoard) ','s: ', s)

        counts = [self.Nsa[(s,a)] if (s,a) in self.Nsa else 0 for a in range(self.game.getActionSize())]
        #counts array represent the number of time each action edge from your current state was traversed

        if temp==0: #temprature is 0 representing taking the best action possible (greedy)
            bestA = np.argmax(counts) #bestA: best action number : argmax Returns the indices of the maximum values
            probs = [0]*len(counts)
            probs[bestA]=1
            return probs #returns the definite move(s) with same greedy reward, out of which one move HAS to be played

        counts = [x**(1./temp) for x in counts]
        probs = [x/float(sum(counts)) for x in counts]
        print('MCTS.py==>getActionProb returns: probs ','counts: ',counts,'probs: ', probs)
        return probs #returns the probablity of different moves that CAN be played resulting in uniform distribution


    def search(self, canonicalBoard):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.

        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propogated
        up the search path. In case the leaf node is a terminal state, the
        outcome is propogated up the search path. The values of Ns, Nsa, Qsa are
        updated.

        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.

        Returns:
            v: the negative of the value of the current canonicalBoard
        """

        s = self.game.stringRepresentation(canonicalBoard)
        # s represents the state of the board as a string

        if s not in self.Es:
            self.Es[s] = self.game.getGameEnded(canonicalBoard, 1)
            #Es :  'end state' array : maps the state string 's' to -1, 0 , 1 to check if the state s is end state
            #-1: Black has won : End state
            #+1: White has won: End state
            # 0: Not an end state ==> continue the search iteration

        print('MCTS.py==>search ', 'self.Es[s]: ',self.Es[s])
        if self.Es[s]!=0:
            # terminal node : game ended
            print('MCTS.py==>search ', 'Game ended returning: -self.Es[s]: ', -self.Es[s])
            return -self.Es[s]

        if s not in self.Ps: #if the current state 's' is not explored/expanded before n=0 by MCTS then create a new node and rollout

            #If it does not exist, we create a new node in our tree and initialize its
            #P (s, ·) = p ~ θ (s) and the expected reward v = v θ (s) from
            #our neural network, and initialize Q(s, a) and N (s, a)
            #to 0 for all a ==>leaf node wrt current half explored MCTS

            self.Ps[s], v = self.nnet.predict(canonicalBoard)
            valids = self.game.getValidMoves(canonicalBoard, 1)
            print('MCTS.py==>search ', 'valid moves returned by getValidMoves(): ', valids)
            self.Ps[s] = self.Ps[s]*valids      # masking invalid moves i.e the policies from the policy vector which are useless validmove = 0
            sum_Ps_s = np.sum(self.Ps[s])
            if sum_Ps_s > 0:
                self.Ps[s] /= sum_Ps_s    # renormalize
            else:
                # if all valid moves were masked make all valid moves equally probable

                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.
                print("All valid moves were masked, do workaround.") #print:surag
                self.Ps[s] = self.Ps[s] + valids
                self.Ps[s] /= np.sum(self.Ps[s])

            self.Vs[s] = valids #Vs: valid moves the game board at state 's'
            self.Ns[s] = 0
            print('MCTS.py==>search ', 'returning value of canonical board -v: ', -v)
            return -v

        valids = self.Vs[s] #as already visited the valid moves array 'Vs' is already initialized
        cur_best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        for a in range(self.game.getActionSize()):
            if valids[a]:
                if (s,a) in self.Qsa:
                    u = self.Qsa[(s,a)] + self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s])/(1+self.Nsa[(s,a)])
                else:
                    u = self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s])     # Q = 0 ? : node exists but not explored as added and initilized during nnet phase

                if u > cur_best:
                    cur_best = u
                    best_act = a

        a = best_act
        next_s, next_player = self.game.getNextState(canonicalBoard, 1, a) #next node in MCTS is selected greedily as we had the policies for that node
        next_s = self.game.getCanonicalForm(next_s, next_player) #TODO: chess board symmetry issue
        print('MCTS.py==>search ', 'best_act: ', a,'next_s: ',next_s,'next_player', next_player)

        v = self.search(next_s) #RECURSION until leaf node or terminal node is found

        #BACK-UP of MCTS STARTS HERE: after returning from RECURSIVE CALL
        if (s,a) in self.Qsa:
            self.Qsa[(s,a)] = (self.Nsa[(s,a)]*self.Qsa[(s,a)] + v)/(self.Nsa[(s,a)]+1) #update the Q Value
            self.Nsa[(s,a)] += 1 #increment number of visits to this node in MCTS

        else:
            self.Qsa[(s,a)] = v #INITIALIZE the new node
            self.Nsa[(s,a)] = 1

        self.Ns[s] += 1
        print('MCTS.py==>search ', 'returning value of canonical board -v: ', -v)
        return -v
