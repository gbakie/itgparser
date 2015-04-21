# 04/2015
# author: gbakie
# Inversion Transduction Grammar

from collections import defaultdict
from math import exp

W_EPS_EN = -20
W_EPS_GE = -21
W_UNK = -30
W_DIR = -1
W_INV = -2
DIR = 0
INV = 1

class ItgParser():

    def __init__(self, _vocab, _grammar=None):
        self.vocab = _vocab
        self.grammar = _grammar
        self.n_rules = 0
        self.inv_rules = 0
        self.dir_rules = 0
        self.n_alignments = 0
        self.eps_en_alignments = 0
        self.eps_ge_alignments = 0
        self.inv = True

    def parse(self, s_en, s_ge):
        T = len(s_en)
        V = len(s_ge)

        self.deltas = defaultdict(float)
        self.thetas = defaultdict(int)
        self.sigmas = defaultdict(int)
        self.upsilons = defaultdict(int)

        self.__initialize(s_en, s_ge, T, V)
        self.__estimate(T,V)
        R = self.__reconstruct((0,T,0,V),0)
        return self.__best_alignment(R)

    def enable_inv_rules(self, inv):
        self.inv = inv

    def per_english_no_alignment(self):
        return float(self.eps_en_alignments)/self.n_alignments

    def per_german_no_alignment(self):
        return float(self.eps_ge_alignments)/self.n_alignments

    def per_dir_rules(self):
        return float(self.dir_rules)/self.n_rules

    def per_inv_rules(self):
        return float(self.inv_rules)/self.n_rules

    def __initialize(self, s_en, s_ge, T, V):
        for t in range(1,T+1):
            for v in range(1,V+1):
                k = (t-1, t, v-1, v)
                b = (s_en[t-1], s_ge[v-1])
                if (self.vocab[b] == 0):
                    self.deltas[k] = exp(W_UNK)
                else: 
                    self.deltas[k] = exp(self.vocab[b])

        for t in range(1,T+1):
            for v in range(0,V+1):
                k = (t-1, t, v, v) 
                self.deltas[k] = exp(W_EPS_EN)
        
        for t in range(0,T+1):
            for v in range(1,V+1):
                k = (t, t, v-1, v) 
                self.deltas[k] = exp(W_EPS_GE)


    def __estimate(self,T,V):
        for s in range(0,T+1):
            for t in range(s+1,T+1):
                for u in range(0,V+1):
                    for v in range(u+1,V+1):
                        if (t - s + v - u) > 2:
                            delta1, params1 = self.__max_delta_dir(s,t,u,v)

                            delta2 = 0
                            if self.inv:
                                delta2, params2 = self.__max_delta_inv(s,t,u,v)

                            if (delta1 >= delta2):
                                self.deltas[(s,t,u,v)] = delta1
                                self.thetas[(s,t,u,v)] = DIR
                                self.sigmas[(s,t,u,v)] = params1[0]
                                self.upsilons[(s,t,u,v)] = params1[1]
                            else:
                                self.deltas[(s,t,u,v)] = delta2
                                self.thetas[(s,t,u,v)] = INV
                                self.sigmas[(s,t,u,v)] = params2[0]
                                self.upsilons[(s,t,u,v)] = params2[1]
                                
     
    def __max_delta_dir(self,s,t,u,v):
        max_delta = 0. 
        max_params = (t,v)

        for S in range(s,t+1):
            for U in range(u,v+1):
                if ( (S-s)*(t-S) + (U-u)*(v-U)) != 0:
                    d = exp(W_DIR) * self.deltas[(s,S,u,U)] * self.deltas[(S,t,U,v)] 
                    if d > max_delta:
                        max_delta = d
                        max_params = (S,U)

        return max_delta, max_params

    def __max_delta_inv(self,s,t,u,v):
        max_delta = 0. 
        max_params = (t,v)

        for S in range(s,t+1):
            for U in range(u,v+1):
                if ( (S-s)*(t-S) + (U-u)*(v-U)) != 0:
                    d = exp(W_INV) * self.deltas[(s,S,U,v)] * self.deltas[(S,t,u,U)] 

                    if d > max_delta:
                        max_delta = d
                        max_params = (S,U)

        return max_delta, max_params

    def __reconstruct(self,q,n):
        node = [q]

        # protection against infinite recursion
        if n > 50:
            print "max recursion"
            return None

        if q == None:
            return None

        (s,t,u,v) = q
        #print q

        left_q = None
        if (t-s+v-u <= 2):
            left_q = None
        elif (self.thetas[q] == DIR and (t-s+v-u) > 3):
            self.n_rules += 1
            self.dir_rules += 1
            left_q = (s,self.sigmas[q],u,self.upsilons[q])
        elif (self.thetas[q] == INV):
            self.n_rules += 1
            self.inv_rules += 1
            left_q = (s,self.sigmas[q],self.upsilons[q],v)
            
        right_q = None
        if (t-s+v-u <= 2):
            right_q = None
        elif (self.thetas[q] == DIR and (t-s+v-u) > 3):
            self.n_rules += 1
            self.dir_rules += 1
            right_q = (self.sigmas[q],t,self.upsilons[q],v)
        elif (self.thetas[q] == INV):
            self.n_rules += 1
            self.inv_rules += 1
            right_q = (self.sigmas[q],t,u,self.upsilons[q])

        node.append(self.__reconstruct(left_q,n+1))
        node.append(self.__reconstruct(right_q,n+1)) 

        return node


    def __best_alignment(self, R):
        align = []
 
        visit = [R]
        while len(visit) > 0:
            node = visit.pop(0)

            [a,l,r] = node 
            if l == None and r == None:
                self.n_alignments += 1
                (s,t,u,v) = a 
                al = (t,v)
                if (s == t):
                    self.eps_ge_alignments += 1
                    al = (0,v)
                elif (u == v):
                    self.eps_en_alignments += 1
                    al = (t,0)

                align.append(al) 
            else:
                visit.append(l)
                visit.append(r)

        return align
