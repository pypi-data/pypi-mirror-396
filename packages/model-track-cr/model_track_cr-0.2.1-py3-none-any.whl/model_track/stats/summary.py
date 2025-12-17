import pandas as pd

def get_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for col in df.columns:
        series = df[col]
        n_na = series.isna().sum()
        pct_na = n_na / len(series)*100

        # dtype
        dtype = str(series.dtype)

        # distinct values (com NA)
        distinct_vals = series.unique().tolist()
        n_distinct = len(distinct_vals)

        if n_distinct > 10:
            distinct_repr = "..."
        else:
            distinct_repr = list(distinct_vals)

        # top class
        vc = series.value_counts(dropna=True)
        if len(vc) > 0:
            top_class = vc.index[0]
            top_class_pct = vc.iloc[0] / vc.sum()*100
        else:
            top_class = None
            top_class_pct = None

        #  min / max
        if pd.api.types.is_numeric_dtype(series):
            col_min = series.min()
            col_max = series.max()

        elif pd.api.types.is_datetime64_any_dtype(series):
            col_min = series.min()
            col_max = series.max()

        else:
            col_min = None
            col_max = None

        
        rows.append({
            "column_name": col,
            "dtype": dtype,
            "n_na": n_na,
            "pct_na": pct_na,
            "top_class": top_class,
            "top_class_pct": top_class_pct,
            "n_distinct": n_distinct,
            "distinct_values": distinct_repr,
            "min": col_min,
            "max": col_max
        })

    return pd.DataFrame(rows)

