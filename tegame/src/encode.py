import torch
N_PILES=4
MAX_HAND=7

def encode_hand(hand):
    """
    Encode the player's hand into a fixed-size vector.

    Parameters
    ----------
    hand : list[int]
        Sorted list of cards in the player's hand.

    Returns
    -------
    list[int]
        Length MAX_HAND vector with zero padding.
    """
    hand = hand[:MAX_HAND]
    return hand + [0] * (MAX_HAND - len(hand))

def encode_piles(piles):
    """
    Encode the current piles using only their top cards.

    Parameters
    ----------
    piles : list[list[int]]

    Returns
    -------
    list[int]
        Length N_PILES vector of top cards (0 if empty).
    """
    return [pile[-1] if len(pile) > 0 else 0 for pile in piles]

def encode_pile_preference(piles_to_avoid):
    """
    Encode discouraged piles as soft preferences.

    Parameters
    ----------
    piles_to_avoid : list[int] or None

    Returns
    -------
    list[int]
        Binary vector where 0 = discouraged, 1 = preferred.
    """
    pref = [1] * N_PILES
    
    if piles_to_avoid is not None and not piles_to_avoid==[None]:
        for idx in piles_to_avoid:
            pref[idx] = 0

    return pref

def build_state_vector(hand, piles, mandatory_move, piles_to_avoid):
    state = (
            encode_hand(hand) +
            encode_piles(piles) +
            [int(mandatory_move)] +
            encode_pile_preference(piles_to_avoid)
        )
    return state

def generate_all_possible_features(hand, piles, mandatory_move, piles_to_avoid):
    """
    Costruisce TUTTE le mosse possibili (incl. NOOP)
    e restituisce SOLO X_group (tensor [num_moves, feature_dim]).
    """

    # 1. Stato
    state_vector = build_state_vector(
        hand=hand,
        piles=piles,
        mandatory_move=mandatory_move,
        piles_to_avoid=piles_to_avoid
    )

    features = []

    # 2. Mosse reali
    for card_idx, card_value in enumerate(hand):
        for pile_idx in range(len(piles)):

            move_features = build_move_features(
                hand=hand,
                piles=piles,
                card_value=card_value,
                pile_idx=pile_idx
            )

            features.append(state_vector + move_features)

    # 3. NOOP
    noop_features = state_vector + build_noop_features()
    features.append(noop_features)

    return features

def build_noop_features():
    MOVE_FEATURES_DIM = len(build_move_features(hand=[1], piles=[[0]], card_value=1, pile_idx=0))
    return [0.0] * MOVE_FEATURES_DIM

def build_move_features(hand, piles, card_value, pile_idx):
    pile_top = piles[pile_idx][-1] if isinstance(piles[pile_idx], list) else piles[pile_idx]

    delta = card_value - pile_top
    abs_delta = abs(delta)

    pile_is_ascendent=1 if pile_idx<=1 else 0

    is_10combo = 1 if ((card_value == pile_top - 10 and pile_is_ascendent) or (card_value == pile_top + 10 and not pile_is_ascendent)) else 0

    is_20combo=False
    if pile_is_ascendent:
        for card_i in hand:
            if card_i!=card_value and card_value-card_i==10:
                is_20combo=True
                break
    else:
        for card_i in hand:
            if card_i!=card_value and card_i-card_value==10:
                is_20combo=True
                break
            
    is_legal = 1 if ((card_value > pile_top and pile_is_ascendent) or (card_value < pile_top and not pile_is_ascendent) or is_10combo) else 0

    return [
        float(card_value),
        float(pile_is_ascendent),
        float(pile_top),
        float(delta),
        float(abs_delta),
        float(is_legal),
        float(is_10combo),
        float(is_20combo),
    ]

def decode_feature(feature,hand,piles_top):
    move_features=feature[MAX_HAND+4+1+4:]
    card=move_features[0]
    if card==0: return None,None #NO-OP move
    card_idx=hand.index(card)
    pile_top=move_features[2]
    pile_idx=piles_top.index(pile_top)
    return card_idx,pile_idx
    
    
def unzip_state_vector(state_vector):
    """
    Convert a state vector into its human-readable components.

    Parameters
    ----------
    state_vector : list or 1D torch.tensor
        State vector containing:
        - hand (padded with zeros up to MAX_HAND)
        - piles (length N_PILES * 2 if using increasing/decreasing)
        - mandatory_move flag (1 value)
        - piles_to_avoid (length N_PILES, binary or numeric)

    Returns
    -------
    hand : list of int
        Actual cards in the player's hand (padding zeros removed)
    piles : list
        Current piles on the table (as in state vector)
    mandatory_move : bool
        Whether this is a mandatory move
    piles_to_avoid : list
        List or vector indicating piles to avoid
    """
    # Convert to list if tensor
    if isinstance(state_vector, torch.Tensor):
        state_vector = state_vector.tolist()

    # Slice the hand and remove padding zeros
    hand = [int(c) for c in state_vector[:MAX_HAND] if c != 0]

    # Slice piles (adjust depending on how many elements you encoded)
    piles_start = MAX_HAND
    piles_end = MAX_HAND + N_PILES  # assuming two values per pile: increasing + decreasing
    piles = [int(c) for c in state_vector[piles_start:piles_end]]

    # Mandatory flag
    mandatory_move = bool(state_vector[piles_end])

    # Piles to avoid
    piles_to_avoid = [i for i,c in enumerate(state_vector[piles_end + 1: piles_end + 1 + N_PILES]) if int(c)==0]

    return hand, piles, mandatory_move, piles_to_avoid

def decode_action(action_idx):
    if action_idx == MAX_HAND * N_PILES:
        return None, None  # NO-OP

    card_idx = action_idx // N_PILES
    pile_idx = action_idx % N_PILES
    return card_idx.item(), pile_idx.item()

def encode_action(card_idx, pile_idx):
    if card_idx is None or pile_idx is None:
        return MAX_HAND * N_PILES #no operation move
    else:
        return card_idx * N_PILES + pile_idx