import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from model_track.woe import WoeCalculator
from model_track.woe import WoeByPeriod


class WoeStability:
    """
    Provides WOE stability visualization over time for a single feature.

    Responsibilities:
    - Compute global WOE table
    - Plot WOE evolution by period

    This class does NOT evaluate stability.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        date_col: str,
        event_value: int = 1,
    ):
        self.df = df.copy()
        self.date_col = date_col
        self.event_value = event_value

        if date_col not in df.columns:
            raise KeyError(
                f"Period column '{date_col}' not found in DataFrame."
            )

    # ------------------------------------------------------------------
    # Global WOE
    # ------------------------------------------------------------------
    def global_table(
        self,
        feature_col: str,
        target_col: str,
    ) -> pd.DataFrame:
        """
        Computes and returns the global WOE table
        (no temporal split).
        """
        return WoeCalculator.compute_table(
            df=self.df,
            feature_col=feature_col,
            target_col=target_col,
            event_value=self.event_value,
        )

    # ------------------------------------------------------------------
    # WOE stability view
    # ------------------------------------------------------------------
    def generate_view(
        self,
        feature_col: str,
        target_col: str,
        ax: plt.Axes=None,
    ):
        """
        Plots WOE evolution over time for a feature.

        Parameters
        ----------
        feature_col : str
            Categorical feature name.
        target_col : str
            Binary target column.
        ax : matplotlib axis, optional
            If provided, plot is drawn on this axis.
            If None, a new figure is created and returned.

        Returns
        -------
        matplotlib.figure.Figure or None
        """

        woe_period = WoeByPeriod.compute(
            df=self.df,
            feature_col=feature_col,
            target_col=target_col,
            date_col=self.date_col,
            event_value=self.event_value,
        )

        created_fig = False
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 5))
            created_fig = True

        for category, df_cat in woe_period.groupby(feature_col):
            df_cat = df_cat.sort_values(self.date_col)

            ax.plot(
                df_cat[self.date_col],
                df_cat["woe"],
                marker="o",
                label=str(category),
            )

        ax.axhline(0, color="black", linestyle="--", linewidth=1)
        ax.set_title(f"WOE Stability Over Time — {feature_col}")
        ax.set_xlabel("Period")
        ax.set_ylabel("WOE")
        ax.legend(title=feature_col)
            # Ajustando a estética
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.grid(True, linestyle='-', linewidth=0.2)
        ax.xaxis.grid(True, linestyle='-', linewidth=0.2)
        
        ax.legend(title=feature_col, bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        # se em x for datetime exibir apenas yyyy-mm
        if pd.api.types.is_datetime64_any_dtype(woe_period[self.date_col]):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        
        if created_fig:
            return fig
        return None
