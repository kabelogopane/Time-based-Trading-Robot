"""Sample-size audit for the 09:45 research dataset.

This module reports how many complete sessions are available and checks whether
additional data is needed before treating walk-forward results as reliable.
Research only: no live trading or broker connectivity.
"""

from __future__ import annotations

import pandas as pd


def audit_sessions(diagnostics: pd.DataFrame) -> dict[str, object]:
    """Return a compact chronological sample-size audit."""
    if "date" not in diagnostics.columns:
        raise ValueError("diagnostics missing columns: ['date']")
    dates = pd.to_datetime(diagnostics["date"]).sort_values().drop_duplicates()
    return {
        "complete_sessions": int(len(dates)),
        "first_session": str(dates.iloc[0].date()) if len(dates) else None,
        "last_session": str(dates.iloc[-1].date()) if len(dates) else None,
        "recommended_next_step": (
            "Expand the historical sample before accepting a regime filter as robust."
            if len(dates) < 100
            else "Sample is large enough for a broader robustness review."
        ),
    }
