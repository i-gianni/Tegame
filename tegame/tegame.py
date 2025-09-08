import numpy as np
from random import shuffle
from sys import exit
from copy import deepcopy

class tegame:

    def __init__(self,verbose=False):

        self.n_players = 2
        self.n_draw = 2
        self.thresh_pile = 10
        self.tresh_nonmandatory = 2

        self.verbose = verbose

        card_per_player = {2:7, 3:6, 4:6, 5:6}
        self.n_inhand = card_per_player[self.n_players]

        self.original_deck = [int(i) for i in np.arange(2,100)]
        shuffle(self.original_deck)
        self.original_piles = [[1],[1],[100],[100]]

        self.refresh()

    def refresh(self):
               
        self.deck = deepcopy(self.original_deck)
        self.piles = deepcopy(self.original_piles)
        self.restart()
        
    def restart(self):

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
    
    def scan_hand(self,active_player,discards=[],mandatory_move=True):

        delta,ind = self.scan_hand_(active_player,discards=discards,mandatory_move=mandatory_move)
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
    def scan_hand_(self,active_player,discards=[],mandatory_move=True):

        tops = [pile[-1] for pile in self.piles]
        delta = 100
        ind = []

        hand = self.hands[active_player]

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
            print(f"\nPlayer {active_player} would like to play card {hand[ind[0]]}")
            print(f"On pile {ind[1]}")
            print(f"Dealing {delta} damage")

        return delta, ind



# Play a full turn
# Play all the reasonable cards in hand
def play_turn(player_idx):
    n_played=n   #this is incremented only in case one or more non-obbligatory cards are played
    hand=hands[player_idx]

    print('player ', player_idx,' , hand: ',hand)
    print_piles(piles)
    
    for _ in range(n):
        hand=play_card(hand,player_idx)

    while True:
        hand_old=hand.copy()
        hand=play_card(hand,player_idx,mandatory_move=False)
        #print(hand,hand_old)
        if hand==hand_old: break
        n_played = n_played + 1
        
    print('n. played cards: ',n_played,'\n')
    for _ in range(n_played):
        hand=pick_one(hand)
    hands[player_idx]=hand

# Main action in a player turn
# perform several actions to undestand which card to play
def play_card(hand,player_idx,mandatory_move=True):
    delta_1,(card_idx1,pile_idx1)=scan_hand(hand,mandatory_move=mandatory_move)
    if delta_1==-10:
        hand=place_card(hand,card_idx1,pile_idx1)
    elif not mandatory_move and delta_1>one_more_tresh:
        return hand
    else:
        #mask_inactive = [i!=player_idx for i in range(N)]
        hands_non_active = [hand for i,hand in enumerate(hands) if not i==player_idx] #np.asarray(hands)[mask_inactive].tolist()
        dont_pile_idx_list = interaction(hands_non_active)
        
        if not pile_idx1 in dont_pile_idx_list: #case 1: the pile of interest can be played
            hand=place_card(hand,card_idx1,pile_idx1)
        elif dont_pile_idx_list==[0,1,2,3]: #case 2: all piles are taken, so fuck it
            hand=place_card(hand,card_idx1,pile_idx1)
        else: #case 3: check other piles
            delta_2,(card_idx2,pile_idx2)=scan_hand(hand,discards=dont_pile_idx_list,mandatory_move=mandatory_move)
            if delta_2-delta_1>danger_thresh or delta_2==100:
                hand=place_card(hand,card_idx1,pile_idx1)
            else:
                if not mandatory_move and delta_2>one_more_tresh:
                    return hand
                else: hand=place_card(hand,card_idx2,pile_idx2)
    return hand    

# Wrapper to actual scan_hand, correctly unpacks hand and pile indexes

# Modellize the interaction with other players
# the hand that are passed are of the inactive players
# they look for the pile onto which they would like to play
# the list of piles is returned
def interaction(hands):
    print("")
    print("Interaction")
    #things to implement: give higher priority to closest players
    n_hands = len(hands)
    delta_list = []
    pile_idx_list = []
    for i in range(n_hands):
        delta,(card_idx,pile_idx)=scan_hand(hands[i],mandatory_move=False)
        pile_idx_list.append(pile_idx)
        if card_idx is not None: print("Card ",hands[i][card_idx]," playable on pile ",pile_idx,"with delta ",delta)
    print("")
    return list(set(pile_idx_list))

# Physical action of placing one card onto a pile
def place_card(hand,card_idx,pile_idx):
    print('Card placed: ', hand[card_idx], 'on pile ',pile_idx)
    piles[pile_idx].append(hand[card_idx]) #add played card to the piles
    hand.pop(card_idx) #remove card played from the hand
    return hand    


# Pick one card from the deck.
# Also check if the deck is empty
def pick_one(hand):
    global n,deck_empty
    if deck == [] and not deck_empty:
        n = card_per_turn - 1
        print("\n------------------------------- Deck is over, last few rounds. Hold on! -------------------------------\n")
        deck_empty = True
    if deck == []:
        return hand
    hand.append(deck[0])
    deck.pop(0)
    return hand

#Print current piles situation
def print_piles(piles):
    print("")
    print("Printing Piles")
    for pile in piles:
        string = ""
        for element in pile:
             string = string + f"{element:3d}" + " "
        print(string)
    print("")




if __name__ == "__main__":
    
    mygame = tegame.tegame()
    mygame.restart()
    mygame.run()