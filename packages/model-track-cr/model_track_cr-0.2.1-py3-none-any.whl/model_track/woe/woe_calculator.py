import numpy as np
import pandas as pd
from typing import Dict


class WoeCalculator:
    """
    Computes Weight of Evidence (WOE) and Information Value (IV)
    for categorical features.

    Weight of Evidence is commonly used in credit scoring and risk modeling
    to quantify the predictive power of a categorical variable with respect
    to a binary target.

    Formula
    -------
    WOE_i = ln(event_rate_i / non_event_rate_i)

    IV_i = (event_rate_i - non_event_rate_i) * WOE_i

    IV_total = sum(IV_i)
    """

    @staticmethod
    def compute_table(
        df: pd.DataFrame,
        target_col: str,
        feature_col: str,
        event_value: int = 1,
        epsilon: float = 1e-8,
        add_totals: bool = True,
        round: int = 4
    ) -> pd.DataFrame:
        """
        Computes the Weight of Evidence (WOE) and Information Value (IV)
        table for a categorical feature.

        Returns
        -------
        pd.DataFrame
            Columns:
            - feature_col
            - n_event
            - n_non_event
            - event_rate
            - non_event_rate
            - exposure
            - woe
            - iv
            - iv_total

            Optionally includes a totals row identified by '__TOTAL__'.
        """

        # --- validations -------------------------------------------------
        if target_col not in df.columns:
            raise KeyError(f"Target column '{target_col}' not found in DataFrame.")

        if feature_col not in df.columns:
            raise KeyError(f"Feature column '{feature_col}' not found in DataFrame.")

        target_values = df[target_col].dropna().unique()
        if len(target_values) != 2:
            raise ValueError(
                f"Target column '{target_col}' must be binary. "
                f"Found values: {target_values}"
            )

        if event_value not in target_values:
            raise ValueError(
                f"event_value '{event_value}' not found in target column '{target_col}'."
            )

        # --- prepare data -----------------------------------------------
        data = df[[feature_col, target_col]].copy()
        data["_event"] = (data[target_col] == event_value).astype(int)
        data["_non_event"] = 1 - data["_event"]

        # --- aggregation ------------------------------------------------
        agg = (
            data
            .groupby(feature_col, dropna=False)
            .agg(
                n_event=("_event", "sum"),
                n_non_event=("_non_event", "sum"),
            )
            .reset_index()
        )

        total_events = agg["n_event"].sum()
        total_non_events = agg["n_non_event"].sum()
        total_obs = total_events + total_non_events

        # --- rates ------------------------------------------------------
        agg["event_rate"] = agg["n_event"] / max(total_events, epsilon)
        agg["non_event_rate"] = agg["n_non_event"] / max(total_non_events, epsilon)
        agg["exposure"] = (agg["n_event"] + agg["n_non_event"]) / max(total_obs, epsilon)

        # --- woe & iv ---------------------------------------------------
        with np.errstate(divide="ignore", invalid="ignore"):
            agg["woe"] = np.log(agg["event_rate"] / agg["non_event_rate"])
            agg["iv"] = (agg["event_rate"] - agg["non_event_rate"]) * agg["woe"]
        if np.isinf(agg["woe"]).any():
            iv_total = np.inf
        else:
            iv_total = agg["iv"].sum()
        agg["iv_total"] = iv_total
        agg.sort_values(by="woe", ascending=False, inplace=True)

        # --- totals row -------------------------------------------------
        if add_totals:
            total_row = {
                feature_col: "__TOTAL__",
                "n_event": total_events,
                "n_non_event": total_non_events,
                "event_rate": agg.event_rate.sum().round(2),
                "non_event_rate": agg.non_event_rate.sum().round(2),
                "exposure": agg["exposure"].sum().round(2),
                "woe": np.nan,
                "iv": iv_total,
                "iv_total": iv_total,
            }

            agg = pd.concat(
                [agg, pd.DataFrame([total_row])],
                ignore_index=True,
            )

        return agg[
            [
                feature_col,
                "n_event",
                "n_non_event",
                "event_rate",
                "non_event_rate",
                "exposure",
                "woe",
                "iv",
                "iv_total",
            ]
        ].round(round)

    @staticmethod
    def compute_mapping(
        df: pd.DataFrame,
        target_col: str,
        feature_col: str,
        event_value: int = 1,
        epsilon: float = 1e-8,
    ) -> Dict:
        """
        Computes WOE mapping for a categorical feature.
        """

        table = WoeCalculator.compute_table(
            df=df,
            target_col=target_col,
            feature_col=feature_col,
            event_value=event_value,
            epsilon=epsilon,
            add_totals=False,
        )

        return dict(zip(table[feature_col], table["woe"]))