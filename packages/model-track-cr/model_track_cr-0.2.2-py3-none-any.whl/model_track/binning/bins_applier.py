import pandas as pd
from typing import List


class BinApplier:
    """
    Aplica bins em uma única coluna do DataFrame.

    df: DataFrame base
    apply(column, bins) -> retorna uma Series com labels em string
    """

    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("df must be a pandas DataFrame")
        self.df = df

    # ------------------------
    # VALIDAÇÃO DOS BINS
    # ------------------------
    def _validate_bins(self, bins: List[float]):
        if not isinstance(bins, list):
            raise ValueError("Bins must be a list of numeric values")

        if len(bins) < 1:
            raise ValueError("Must provide at least one bin edge")

        if sorted(bins) != bins:
            raise ValueError("Bins must be sorted ascending")

        if len(bins) != len(set(bins)):
            raise ValueError("Bins contain duplicated edges")

    # ------------------------
    # GERAR LABELS
    # ------------------------
    def _generate_labels(self, bins: List[float]) -> List[str]:
        """
        Regras:
        - 1 bin  => "<= x", "> x"
        - n bins => "<= b0", "(b0,b1]", "(b1,b2]", ..., "> b_last"
        """
        if len(bins) == 1:
            edge = bins[0]
            return [f"<= {edge}", f"> {edge}"]

        labels = [f"<= {bins[0]}"]

        for left, right in zip(bins[:-1], bins[1:]):
            labels.append(f"({left}, {right}]")

        labels.append(f"> {bins[-1]}")
        return labels

    # ------------------------
    # APLICAÇÃO DOS BINS
    # ------------------------
    def apply(self, column: str, bins: List[float]) -> pd.Series:
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")

        self._validate_bins(bins)

        labels = self._generate_labels(bins)
        cut_edges = [-float("inf")] + bins + [float("inf")]

        # pd.cut gera categorias → converteremos p/ string depois
        binned = pd.cut(
            self.df[column],
            bins=cut_edges,
            labels=labels,
            include_lowest=True
        )

        # Converte para string e substitui NaN por "N/A"
        return binned.astype(object).where(binned.notna(), "N/A")