import pandas as pd

from .woe_calculator import WoeCalculator


class WoeByPeriod:
    """
    Calcula o Weight of Evidence (WOE) por período temporal.

    Esta classe é responsável apenas por:
    - segmentar o DataFrame por período
    - delegar o cálculo de WOE para o WoeCalculator
    - organizar a saída em formato long para análise temporal

    Não reimplementa lógica de WOE.
    """

    @staticmethod
    def compute(
        df: pd.DataFrame,
        target_col: str,
        feature_col: str,
        date_col: str,
        event_value: int = 1,
    ) -> pd.DataFrame:
        """
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame contendo os dados.
        target_col : str
            Nome da coluna alvo binária.
        feature_col : str
            Nome da coluna categórica.
        date_col : str
            Nome da coluna que representa o período.
        event_value : int, optional
            Valor que representa o evento na coluna alvo (default=1).

        Returns
        -------
        pd.DataFrame
            DataFrame em formato long com colunas:
            ['period', feature_col, 'n_event', 'n_non_event',
            'event_rate', 'non_event_rate', 'exposure', 'woe']

        Raises
        ------
        KeyError
            Se date_col não existir.
        ValueError
            Se date_col contiver apenas valores nulos.
        """

        if date_col not in df.columns:
            raise KeyError(f"Column '{date_col}' not found in DataFrame")

        if df[date_col].isna().all():
            raise ValueError(f"Column '{date_col}' contains only null values")

        results = []

        for period, df_period in df.groupby(date_col):
            woe_table = WoeCalculator.compute_table(
                df=df_period,
                target_col=target_col,
                feature_col=feature_col,
                event_value=event_value,
                add_totals=False,
            )

            woe_table = woe_table.copy()
            woe_table.insert(0, "period", period)

            results.append(woe_table)

        return pd.concat(results, ignore_index=True)