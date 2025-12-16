"""Core operations for data transformation."""

from __future__ import annotations

import polars as pl

from .market import Market


def parse_time(
    df: pl.LazyFrame,
    market: Market,
    timestamp_col: str = "timestamp",
) -> pl.LazyFrame:
    """Add elapsed_seconds column based on market sessions.

    Args:
        df: Input LazyFrame
        market: Market definition (only CN supported)
        timestamp_col: Column with integer timestamp (H/HHMMSSMMM format)
            e.g., 93012145 = 09:30:12.145, 142058425 = 14:20:58.425

    Returns:
        LazyFrame with elapsed_seconds column (float, includes milliseconds)
        e.g., 09:30:12.145 → 12.145 (12 seconds + 145ms into trading)

    Raises:
        NotImplementedError: If market is not CN
    """
    if market.name != "CN":
        raise NotImplementedError(f"Market {market.name} not supported yet")

    col = pl.col(timestamp_col)

    # Parse H/HHMMSSMMM → hour, minute, second, millisecond
    h = col // 10000000  # 93012145 // 10000000 = 9
    m = (col // 100000) % 100  # 93012145 // 100000 = 930, 930 % 100 = 30
    s = (col // 1000) % 100  # 93012145 // 1000 = 93012, 93012 % 100 = 12
    ms = col % 1000  # 93012145 % 1000 = 145

    # CN market: calculate elapsed seconds from market open
    # Morning: 09:30-11:30 (2 hours = 7200 seconds)
    # Afternoon: 13:00-15:00 (2 hours = 7200 seconds)
    base_seconds = (
        pl.when((h == 9) & (m >= 30))
        .then((m - 30) * 60 + s)  # 09:30-09:59
        .when(h == 10)
        .then(30 * 60 + m * 60 + s)  # 10:00-10:59
        .when((h == 11) & (m < 30))
        .then(90 * 60 + m * 60 + s)  # 11:00-11:29
        .when((h >= 13) & (h < 15))
        .then(7200 + (h - 13) * 3600 + m * 60 + s)  # 13:00-14:59
        .when((h == 15) & (m == 0) & (s == 0))
        .then(14400)  # 15:00:00 exactly
        .otherwise(None)  # Outside trading hours
    )

    # Include milliseconds as fractional part
    elapsed = base_seconds.cast(pl.Float64) + ms.cast(pl.Float64) / 1000.0

    return df.with_columns(elapsed.alias("elapsed_seconds"))


def bin(df: pl.LazyFrame, widths: dict[str, float]) -> pl.LazyFrame:
    """Add bin columns for specified columns.

    Args:
        df: Input LazyFrame
        widths: Column name to bin width mapping

    Returns:
        LazyFrame with {col}_bin columns added

    Formula:
        bin_value = round(raw_value / binwidth)
        actual_value = bin_value * binwidth  # To recover
    """
    exprs = [
        (pl.col(col) / width).round().cast(pl.Int64).alias(f"{col}_bin")
        for col, width in widths.items()
    ]
    return df.with_columns(exprs)


def aggregate(
    df: pl.LazyFrame,
    group_by: list[str],
    metrics: dict[str, pl.Expr],
) -> pl.LazyFrame:
    """Aggregate data with custom metrics.

    Args:
        df: Input LazyFrame
        group_by: Columns to group by
        metrics: Name to Polars expression mapping

    Returns:
        Aggregated LazyFrame

    Example:
        metrics = {
            "count": pl.len(),
            "total_qty": pl.col("quantity").sum(),
            "vwap": pl.col("notional").sum() / pl.col("quantity").sum(),
        }
    """
    agg_exprs = [expr.alias(name) for name, expr in metrics.items()]
    return df.group_by(group_by).agg(agg_exprs)
