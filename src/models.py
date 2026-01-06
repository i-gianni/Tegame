import torch.nn as nn
MAX_HAND = 7        # max carte reali in mano
N_PILES = 4         # pile reali

class TegamePolicy(nn.Module):
    """
    Policy network that predicts a distribution over (card, pile) actions
    plus a NO-OP action.
    """

    def __init__(self, input_dim, hidden_dim=128):
        super().__init__()

        self.shared = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )

        self.action_head = nn.Linear(
            hidden_dim,
            MAX_HAND * N_PILES + 1  # +1 = NO-OP
        )

    def forward(self, x):
        h = self.shared(x)
        return self.action_head(h)

class TegameScoreModel(nn.Module):
    """
    Modello che valuta UNA mossa e restituisce UNO score.
    """
    def __init__(self, input_dim, hidden_dim=128):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)   # <--- UNO score
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)   # shape: [batch]
