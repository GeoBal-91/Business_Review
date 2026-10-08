"""Presentation-only rounding. No scoring or eligibility decisions live here."""
import math
from data_pipeline import present


def format_percent(value):
    return f"{value:.1%}" if present(value) else "Not assessed"


def format_currency(value):
    return f"€{value:,.0f}" if present(value) else "Not assessed"


def format_currency_2(value):
    return f"€{value:,.2f}" if present(value) else "Not assessed"


def format_number(value):
    return f"{value:,.0f}" if present(value) else "Not assessed"


def format_score(value, threshold=None):
    if not present(value):
        return "Not assessed"
    if 0 < value < .005:
        return "<0.01"
    shown = f"{value:.2f}"
    if threshold is not None and value < threshold <= float(shown):
        return f"<{threshold:.2f}"
    if threshold is not None and value > threshold == float(shown):
        return f"≥{threshold:.2f}"
    return shown


def relative_change(current, previous):
    return current / previous - 1 if present(current) and present(previous) and previous != 0 else None


def pp_change(current, previous):
    return current - previous if present(current) and present(previous) else None


def get_row_value(row, column):
    return row.get(column) if row is not None else None


def valid_positive_rate(value):
    return present(value) and value > 0


def delta_info(change, metric_type="relative", higher_is_better=True, comparison_label="vs prev. month"):
    from theme import GREEN, RED, GREY
    if not present(change):
        return {"text": "Comparison unavailable", "color": GREY}
    if abs(change) < 1e-6:
        return {"text": f"No change {comparison_label}", "color": GREY}
    better = change > 0 if higher_is_better else change < 0
    amount = f"{abs(change) * 100:.1f} pp" if metric_type == "pp" else f"{abs(change):.1%}"
    return {"text": f"{'▲' if change > 0 else '▼'} {amount} {comparison_label}", "color": GREEN if better else RED}


def benchmark_gap_info(partner_value, benchmark_value, metric_type="pp", higher_is_better=True, label="SBU"):
    from theme import GREEN, RED, GREY
    if not present(partner_value) or not present(benchmark_value):
        return {"text": "Benchmark unavailable", "color": GREY}
    gap = partner_value - benchmark_value
    if abs(gap) < 1e-6:
        return {"text": f"In line with {label}", "color": GREY}
    if metric_type == "pp":
        amount = f"{abs(gap) * 100:.1f} pp"
    elif benchmark_value != 0:
        amount = f"{abs(partner_value / benchmark_value - 1):.1%}"
    else:
        return {"text": "Relative comparison unavailable", "color": GREY}
    better = gap > 0 if higher_is_better else gap < 0
    return {"text": f"{amount} {'better' if better else 'worse'} than {label}", "color": GREEN if better else RED}
