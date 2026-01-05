from random import shuffle
from copy import deepcopy

class Tegame:
    "Core class implementing the game logic for the board game 'The Game'."

    def __init__(
        self,
        players: int = 2,
        verb_lvl: int = 2,
        thresh_secondchoice: int = 4,
        thresh_nonmandatory: int = 2
    ):
        """
        Initialize a new game instance.

        Parameters
        ----------
        players : int, default=2
            Number of players in the game.
            Valid values are 2–5.

        verb_lvl : int, default=2
            Verbosity level:
                0 → silent
                1 → final result only (win / loss)
                2 → game story
                3 → detailed story / debug

        thresh_secondchoice : int, default=4
            Risk tolerance when selecting a non-preferred pile
            due to interference from other players.

        thresh_nonmandatory : int, default=2
            Maximum allowed damage to a pile during
            a non-mandatory move.
        """

        # --- Player configuration ---
        self.n_players = players

        # Number of cards drawn per turn
        self.n_draw = 2

        # Number of mandatory card plays per turn
        self.n_mandatory_moves = 2

        # Cards in hand per player (depends on player count)
        card_per_player = {2: 7, 3: 6, 4: 6, 5: 6}
        self.n_inhand = card_per_player[self.n_players]

        # --- Strategy / risk thresholds ---
        self.thresh_secondchoice = thresh_secondchoice
        self.thresh_nonmandatory = thresh_nonmandatory

        # --- Verbosity / logging ---
        self.verb_lvl = verb_lvl

        # --- Deck initialization ---
        # Standard The Game deck: cards 2–99
        self.original_deck = [i for i in range(2, 100)]
        shuffle(self.original_deck)

        # Four piles:
        #   two ascending piles starting at 1
        #   two descending piles starting at 100
        self.original_piles = [[1], [1], [100], [100]]

        # Initialize the runtime game state
        self.restart()
      
        
    def restart(self):

        self.deck_empty = False
        self.game_over = False
        self.game_ongoing =  True

        self.deck = deepcopy(self.original_deck)
        self.piles = deepcopy(self.original_piles)
        self.n_mandatory_moves = 2 # this must be set here but it sucks like this, fix it somehow ## nah

        N = self.n_players
        m = self.n_inhand

        self.hands=[]
        for _ in range(N):
            self.hands.append([i for i in self.deck[:m]])
            self.hands[-1].sort()
            self.deck = self.deck[m:]

    def get_state(self):
        return {
            "hands": self.hands,
            "piles": self.piles,
            "deck": self.deck,
        }

    def set_state(self, state):
        self.hands = state["hands"]
        self.piles = state["piles"]
        self.deck = state["deck"]


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
        for i,pile in enumerate(self.piles):
            print(f"{i}: " + " ".join(f"{num:3n}" for num in pile))

    def print_stat_hands(self):
        print("\nCurrent players hands are")
        for i,hand in enumerate(self.hands):
            print(f"Player {i}:" + " ".join(f"{num:3n}" for num in hand))

    def print_proposal(self,player,card,pile,delta):
        print(f"\nPlayer {player} would like to play card {self.hands[player][card]}")
        print(f"On pile {pile}")
        print(f"Dealing {delta} damage")
    
    def run_game(self):
        """
        Execute a full game of 'The Game' for the current instance.
    
        Game conventions:
            - Decreasing piles start at 100, but for computational convenience,
              they are treated as -100 internally, so that all piles can be
              handled as "increasing". Card values in hand are negated accordingly
              when interacting with decreasing piles.
    
        Gameplay:
            - The game continues in rounds until no more moves are possible.
            - Each player takes turns sequentially, executing their moves
              via `self.play_turn(active_player)`.
    
        Verbosity Levels:
            - 0 : Silent mode, no output.
            - 1 : Only final result (win/loss).
            - 2 : Basic game story printed.
            - 3 : Detailed, step-by-step game story.
    
        Returns
        -------
        game_won : bool
            True if the game was won (players completed all cards successfully),
            False if the game ended unsuccessfully.
    
        Notes
        -----
        - `self.restart()` is called at the start to reset the game state.
        - The game loop runs while `self.game_ongoing` is True, which should
          be updated by internal game logic (e.g., after each turn).
        """
        
        # Reset the game state
        #self.restart()
    
        # Print initial message if verbosity >= 2
        if self.verb_lvl >= 2:
            print("###################")
            print(" STARTING NEW GAME")
            print("###################")
    
        N = self.n_players  # number of players
    
        # Main game loop: continue while the game is ongoing
        while self.game_ongoing:
            for active_player in range(N):
                self.play_turn(active_player)  # each player takes their turn
    
        # Print final result if verbosity > 0
        if self.verb_lvl > 0 and not self.game_over:
            print("\nWow, you've won. Must’ve been pure luck… or the cards felt sorry for you!\n")
        elif self.verb_lvl > 0 and self.game_over:
            print('\nYou Lose, Game Over\n')
    
        # Determine if the game was won
        game_won = not self.game_over
    
        # Return True if the game was won, False otherwise
        return game_won


    # Wrapper to actual scan_hand, correctly unpacks hand and pile indexes
    def scan_hand(self,player,discards=[],mandatory_move=True):

        delta, ind = self.scan_hand_(player,discards=discards,mandatory_move=mandatory_move)
        
        if ind==[]:

            return delta,[None,None]
        
        elif len(ind)==2:

            if self.verb_lvl>=3: self.print_proposal(player,ind[0],ind[1],delta)            
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
            self.game_ongoing = False

        return delta, ind

    def scan_combo(self,player):
        
        hand = self.hands[player]

        combo_list=[]
        for i, card_i in enumerate(hand):
            combo = []
            combo.append(i)
            old = card_i
            if card_i in combo_list: continue
            for j, card_j in enumerate(hand):
                if card_j - old == 10:
                    combo.append(j)
                    old = card_j
            if is_empty_lists(combo_list):
                if (len(combo) > 1) : combo_list.append(combo)
            else:
                if (len(combo) > 1) and not is_list_of(combo_list,combo) : combo_list.append(combo)
        
        return combo_list



    # Modellize the interaction with other players
    # the hand that are passed are of the inactive players
    # they look for the pile onto which they would like to play
    # the list of piles is returned
    def interaction(self,active_player):
        #things to implement: give higher priority to closest players
        if self.verb_lvl>=3:
            print("\n------------")
            print("Interaction")
            print("------------")

        players = [i for i in range(self.n_players) if i is not active_player]
        pile_idx_list = []

        for player in players:
            _,(__,pile_idx)=self.scan_hand(player,mandatory_move=False)
            pile_idx_list.append(pile_idx)

        return list(set(pile_idx_list))


    # Physical action of placing one card onto a pile
    def place_card(self,player,card,pile):
        if self.verb_lvl>=2: print(f"\nDECISION:\nPlayer {player} places card: {self.hands[player][card]} on pile {pile}")
        self.piles[pile].append(self.hands[player][card]) #add played card to the piles
        self.hands[player].pop(card) #remove card played from the hand

    # Pick one card from the deck.
    # Also check if the deck is empty
    def draw_one(self,player):

        if self.deck == [] and not self.deck_empty:
            self.deck_empty = True
            self.n_mandatory_moves -= 1 ### Don't know if this is always correct

        if self.deck_empty:
            if self.verb_lvl>=2:
                print("\n------------------------------- Deck is over, last few rounds. Hold on! -------------------------------\n")
            return
        
        self.hands[player].append(self.deck[0])
        self.deck.pop(0)

    # Main action in a player turn
    # perform several actions to undestand which card to play
    def play_card(self,player,mandatory_move=True):

        
        delta_1,(card_idx1,pile_idx1)=self.scan_hand(player,mandatory_move=mandatory_move)
        if self.game_over: return

        combo_list = self.scan_combo(player)

        # if the playable card is part of a combo, play the cards in reverse order
        #print(self.hands[player],combo_list)
        for combo in combo_list:
            if card_idx1 in combo:
                combo_cards = [self.hands[player][card] for card in combo]
                if (delta_1 != -10) and self.verb_lvl>=3: print("\n COMBO: "+" ".join(str(_)for _ in combo_cards))
                if pile_idx1 > 1:
                    self.place_card(player,combo[0],pile_idx1)
                else:
                    self.place_card(player,combo[-1],pile_idx1)
                return

        if delta_1 == -10:
            # if the card is a -10 play it right away
            self.place_card(player,card_idx1,pile_idx1)

        elif not mandatory_move and delta_1 > self.thresh_nonmandatory:
            # if this is a non mandatory move and the card is shit,
            # just don't play it
            return
        
        else:
            # Check if you don't step on somebody else's foot
            dont_pile_idx_list = self.interaction(player)
            
            if not pile_idx1 in dont_pile_idx_list: #case 1: the pile of interest can be played
                if self.verb_lvl>=3: print("\nNo conflict detected!\n.........")
                self.place_card(player,card_idx1,pile_idx1)

            elif sorted(dont_pile_idx_list) == [0,1,2,3] and not mandatory_move: #case 2: all piles are taken, so fuck it
                if self.verb_lvl>=3: print("\nNo other choice..\n.........")
                self.place_card(player,card_idx1,pile_idx1)

            else: #case 3: check other piles
                if self.verb_lvl>=3: print("\nChecking second choice\n.........")
                delta_2, (card_idx2,pile_idx2) = self.scan_hand(player,discards=dont_pile_idx_list,mandatory_move=mandatory_move)
                if delta_2 - delta_1 > self.thresh_secondchoice or delta_2 == 100:
                    self.place_card(player,card_idx1,pile_idx1)
                else:
                    if delta_2 > self.thresh_nonmandatory and not mandatory_move:
                        return 
                    else: 
                        self.place_card(player,card_idx2,pile_idx2)


    # Play a full turn
    # Play all the reasonable cards in hand
    def play_turn(self,player):
              
        if is_empty_lists(self.hands):
            self.game_ongoing = False
            return

        if self.verb_lvl>=2:
            print("\n=======================")
            print(f"New turn for player {player}")
            print("=======================")
        self.hands[player].sort()
        if self.verb_lvl>=2: self.print_stat_hands()
        
        for _ in range(self.n_mandatory_moves):
            if self.verb_lvl>=3: print(f"\nMandatory move #{_}")
            self.play_card(player)
            if self.game_over: return

        n_played = self.n_mandatory_moves
        while True:
            if self.verb_lvl>=3: print(f"\nOne more move?")

            hand_old = self.hands[player].copy()
            self.play_card(player,mandatory_move=False)

            if self.hands[player] == hand_old:
                if self.verb_lvl>=3:
                    print("\nNo other meaningfull moves, turn is ending")
                    print(f"#played cards: {n_played}")
                break
            n_played = n_played + 1
            
        for _ in range(n_played):
            self.draw_one(player)

        if self.verb_lvl>=2: self.print_stat_piles()
        return
#
# OUT OF CLASS
#
#Utility functions
#
def is_empty_lists(lst):
    return all(isinstance(x, list) and not x for x in lst) if lst else True

def is_list_of(a,b):
    ls = []
    for l in a:
        ls.append(all(item in l for item in b))
    return any(ls)

def argsort(seq):
    """Return the indices that would sort the sequence."""
    return [i for i, _ in sorted(enumerate(seq), key=lambda x: x[1])]

def inverse_permutation(indices):
    """Return the inverse permutation of the given indices."""
    return [idx for idx, _ in sorted(enumerate(indices), key=lambda x: x[1])]

