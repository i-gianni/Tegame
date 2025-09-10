import numpy as np
from random import shuffle
from sys import exit
from copy import deepcopy

class tegame:

    def __init__(self,verbose=False):

        self.n_players = 2
        self.n_draw = 2
        self.n_mandatory_moves = 2
        card_per_player = {2:7, 3:6, 4:6, 5:6}
        self.n_inhand = card_per_player[self.n_players]

        self.thresh_secondchoice = 10
        self.thresh_nonmandatory = 2

        self.verbose = verbose

        self.original_deck = [int(i) for i in np.arange(2,100)]
        shuffle(self.original_deck)
        self.original_piles = [[1],[1],[100],[100]]

        self.restart()         
        
    def restart(self):

        self.deck = deepcopy(self.original_deck)
        self.piles = deepcopy(self.original_piles)

        deck = self.deck
        N = self.n_players
        m = self.n_inhand
        self.hands = np.asarray(deck[:N*m]).reshape([N,m]).tolist()
        deck = deck[N*m:]
        
        self.deck = deck
        self.deck_empty = False

    def print_stat(self):

        self.print_stat_deck()
        self.print_stat_piles()
        self.print_stat_hands()

    def print_stat_deck(self):
        print("\nCurrent deck is")
        step = 25
        for i in range(0, len(self.deck),step):
            line = self.deck[i:i+step]
            print(" ".join(f"{num:3n}" for num in line))
                  
    def print_stat_piles(self):
        print("\nCurrent piles are")
        for pile in self.piles:
            print(" ".join(f"{num:3n}" for num in pile))

    def print_stat_hands(self):
        print("\nCurrent player hands are")
        for hand in self.hands:
            print(" ".join(f"{num:3n}" for num in hand))

    def run_game(self):
    #Convention: decreasing piles start with 100 but for sake of ease
    # we consider them at -100 so that they are increasing
    # in this way we simply change the sign for cards in hands
    
        N = self.n_players
        game_over = False

        while game_over != True:
            for active_player in range(N):
                game_over, game_status = self.play_turn(active_player)

        if game_status == 0:
            print('You Won!')
        else:
            print('Game Over')

    # Wrapper to actual scan_hand, correctly unpacks hand and pile indexes
    def scan_hand(self,player,discards=[],mandatory_move=True):

        delta,ind = self.scan_hand_(player,discards=discards,mandatory_move=mandatory_move)
        if ind==[]:
            return delta,[None,None]
        elif len(ind)==2:
            return delta,ind
        else:
            raise ValueError("Output of scan_hand not recognized")

    # Look for the best card to play from current player's hand onto the field
    # return the card, the pile and the damage done by the possible move
    # delta is the distance of the bast match (the so called damage)
    # ind contains first the in-hand index then the pile index
    def scan_hand_(self,player,discards=[],mandatory_move=True):

        tops = [pile[-1] for pile in self.piles]
        delta = 100
        ind = []

        hand = self.hands[player]

        for i, hand_i in enumerate(hand):
            for j, top_j in enumerate(tops):

                if j in discards: continue

                old_delta = delta
                old_ind = ind

                ind = [i,j]
                delta = hand_i - top_j
                if j > 1: delta = -delta #inversion due to descending piles

                if delta == -10:
                    return delta, ind
                elif delta >= old_delta or delta < 0 : #can't be right to simply accept negative delta, check later
                    delta = old_delta
                    ind = old_ind

        #replace this with exit program command when the code is implemented in a script
        if delta==100 and discards==[] and mandatory_move:
            self.game_over = True
            self.game_status = 1

        if self.verbose:
            print(f"\nPlayer {player} would like to play card {hand[ind[0]]}")
            print(f"On pile {ind[1]}")
            print(f"Dealing {delta} damage")

        return delta, ind
    
    # Modellize the interaction with other players
    # the hand that are passed are of the inactive players
    # they look for the pile onto which they would like to play
    # the list of piles is returned
    def interaction(self,active_player):
        #things to implement: give higher priority to closest players
        print("\nInteraction")

        players = [i for i in range(self.n_players) if i is not active_player]
        pile_idx_list = []

        for player in players:
            delta,(card_idx,pile_idx)=self.scan_hand(player,mandatory_move=False)
            pile_idx_list.append(pile_idx)
            if card_idx is not None: 
                print(f"Player {player} would like to play:")
                print(f"Card {self.hands[player][card_idx]} on pile {pile_idx} with delta {delta}")

        return list(set(pile_idx_list))

    # Physical action of placing one card onto a pile
    def place_card(self,player,card,pile):
        print(f"Placing card: {self.hands[player][card]} on pile {pile}")
        self.piles[pile].append(self.hands[player][card]) #add played card to the piles
        self.hands.pop(card) #remove card played from the hand

    # Pick one card from the deck.
    # Also check if the deck is empty
    def draw_one(self,player):

        if self.deck == [] and not deck_empty:
            self.n_mandatory_moves -= 1 ### Don't know if this is always correct
            print("\n------------------------------- Deck is over, last few rounds. Hold on! -------------------------------\n")
            deck_empty = True

        if self.deck == []:
            return
        
        self.hands[player].append(self.deck[0])
        self.deck.pop(0)

    # Main action in a player turn
    # perform several actions to undestand which card to play
    def play_card(self,player,mandatory_move=True):
        delta_1,(card_idx1,pile_idx1)=self.scan_hand(player,mandatory_move=mandatory_move)
        if delta_1 == -10:
            hand = place_card(player,card_idx1,pile_idx1)
        elif not mandatory_move and delta_1 > self.thresh_nonmandatory:
            return
        else:
            dont_pile_idx_list = self.interaction(player)
            
            if not pile_idx1 in dont_pile_idx_list: #case 1: the pile of interest can be played
                hand = place_card(hand,card_idx1,pile_idx1)

            elif sorted(dont_pile_idx_list) == [0,1,2,3] and not mandatory_move: #case 2: all piles are taken, so fuck it
                hand = place_card(hand,card_idx1,pile_idx1)

            else: #case 3: check other piles
                delta_2, (card_idx2,pile_idx2) = self.scan_hand(player,discards=dont_pile_idx_list,mandatory_move=mandatory_move)
                if delta_2 - delta_1 > self.thresh_secondchoice or delta_2 == 100:
                    hand = place_card(hand,card_idx1,pile_idx1)
                else:
                    if delta_2 > self.thresh_nonmandatory and not mandatory_move:
                        return 
                    else: 
                        hand = place_card(hand,card_idx2,pile_idx2)


    # Play a full turn
    # Play all the reasonable cards in hand
    def play_turn(self,player):
              
        print("\n=======================")
        print(f"New turn for player {player}")
        print("=======================")
        for _ in range(self.n_mandatory_moves):
            hand=self.play_card(player)

        n_played = self.n_mandatory_moves
        while True:

            hand_old = self.hands[player].copy()
            self.play_card(player,mandatory_move=False)

            if self.hands[player] == hand_old: break
            n_played = n_played + 1
            
        print(f"\nn. played cards: {n_played}")
        for _ in range(n_played):
            self.draw_one(player)



if __name__ == "__main__":
    
    mygame = tegame.tegame()
    mygame.restart()
    mygame.run()