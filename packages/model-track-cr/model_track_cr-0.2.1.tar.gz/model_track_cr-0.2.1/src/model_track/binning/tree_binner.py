from sklearn.tree import DecisionTreeClassifier


class TreeBinner:
    """
    Generates binning cut points using a shallow decision tree.
    """

    def __init__(self, max_depth=2, min_samples_leaf=50):
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.model_ = None
        self.bins_ = []

    def _prepare_data(self, df, feature, target):
        """Handles NaNs and ensures numeric-only series."""
        series = df[feature]

        # Drop rows where either feature or target is missing
        valid = series.notna() & df[target].notna()
        X = series[valid].astype(float).values.reshape(-1, 1)
        y = df.loc[valid, target].astype(int).values

        return X, y, series.min(), series.max()

    def fit(self, df, feature, target):
        """
        Fit a shallow decision tree and extract valid splits.
        """
        X, y, min_val, max_val = self._prepare_data(df, feature, target)

        # Not enough data
        if len(X) < max(self.min_samples_leaf * 2, 3):
            self.bins_ = []
            return self

        tree = DecisionTreeClassifier(
            max_depth=self.max_depth,
            min_samples_leaf=self.min_samples_leaf,
        )

        tree.fit(X, y)
        self.model_ = tree

        thresholds = tree.tree_.threshold
        thresholds = thresholds[thresholds != -2]  # remove leaf markers

        # No splits found
        if len(thresholds) == 0:
            self.bins_ = []
            return self

        # Keep only valid internal cut points
        valid_thresholds = [
            float(t)
            for t in thresholds
            if min_val < t < max_val
        ]

        # Sorted + unique
        valid_thresholds = sorted(set(valid_thresholds))

        self.bins_ = valid_thresholds

        return self