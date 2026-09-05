"""Export session observations as a simple CSV trade journal."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .session import SessionObservation


def observations_to_frame(observations: list[SessionObservation]) -> pd.DataFrame:
    """Convert observations into a tabular research journal."""
    return pd.DataFrame([observation.__dict__ for observation in observations])


def write_csv(observations: list[SessionObservation], path: str | Path) -> Path:
    """Write observations to CSV and return the output path."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    observations_to_frame(observations).to_csv(destination, index=False)
    return destination
