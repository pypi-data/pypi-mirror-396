import numpy as np


class QuantileBinner:
    """
    Generates binning cut points using quantiles.
    Same interface as TreeBinner.

    Parameters
    ----------
    n_bins: int
        Number of desired bins (e.g. 3 => tercis, 4 => quartis).
    min_unique: int
        Minimum required distinct values to compute bins.
    """

    def __init__(self, n_bins=3, min_unique=5):
        self.n_bins = n_bins
        self.min_unique = min_unique
        self.bins_ = []

    def _prepare_data(self, df, feature):
        """Extracts a clean numeric series."""
        series = df[feature]

        # Keep only numeric non-null values
        valid = series.notna()
        values = series[valid].astype(float).values

        return values

    def fit(self, df, feature, target=None):
        """
        Creates bins based on quantiles.
        TreeBinner requires a target, so we keep it for API compatibility,
        but it is ignored here.
        """
        values = self._prepare_data(df, feature)

        # Not enough unique values → no bins
        if len(np.unique(values)) < self.min_unique:
            self.bins_ = []
            return self

        # Compute quantile cut points
        quantiles = np.linspace(0, 1, self.n_bins + 1)

        # Only internal cut points (exclude 0 and 1)
        cut_points = np.quantile(values, quantiles)[1:-1]

        # Remove duplicates (possible in discrete fields)
        cut_points = sorted(set(cut_points))

        # If too few distinct cut points → fallback sem bins
        if len(cut_points) == 0:
            self.bins_ = []
            return self

        self.bins_ = [float(x) for x in cut_points]
        return self