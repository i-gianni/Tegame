from torch.utils.data import Dataset

class TegameDataset(Dataset):
    def __init__(self, groups):
        # groups is a list of (X_group, y_group) pairs.
        # Each element represents one decision group:
        #   X_group : tensor [num_moves, feature_dim]
        #   y_group : int (index of the correct move)
        self.groups = groups

    def __len__(self):
        # Number of decision groups in the dataset
        return len(self.groups)

    def __getitem__(self, idx):
        # Return the (X_group, y_group) pair at the given index
        X_group, y_group = self.groups[idx]
        return X_group, y_group
