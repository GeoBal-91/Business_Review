"""Dataset-backed SBU discovery for command-line and future web clients.

Reading is explicit: importing this module performs no IO. Pass a workbook
path or an already loaded frame. No SBU aliases or benchmark fallbacks.
"""
from pathlib import Path
import pandas as pd
from config import SUBBUSINESS_FILE
from data_pipeline import DataIssue, DataValidationError


def supported_sbus(source=SUBBUSINESS_FILE):
    """Return sorted canonical SBU names from the selected benchmark dataset."""
    frame = pd.read_excel(Path(source)) if not isinstance(source, pd.DataFrame) else source
    frame = frame.rename(columns=lambda name: str(name).strip())
    column = 'Store Sub Business Unit'
    if list(frame.columns).count(column) != 1:
        raise DataValidationError([DataIssue('error', 'sbu_catalog_schema', 'SBU',
                                            'Expected one Store Sub Business Unit column')])
    values = frame[column].dropna().astype(str).str.strip().str.upper()
    names = tuple(sorted(set(values[values != ''])))
    if not names:
        raise DataValidationError([DataIssue('error', 'empty_input', 'SBU',
                                            'No SBU values in benchmark dataset')])
    return names
