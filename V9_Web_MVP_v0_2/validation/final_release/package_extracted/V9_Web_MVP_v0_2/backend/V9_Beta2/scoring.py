"""Pure metric scoring. All values stay at full precision until presentation."""
from dataclasses import asdict, dataclass
import math

import numpy as np
import pandas as pd

import config as cfg
from data_pipeline import D, N, T, P, C, U, present

METRICS = ("CVR", "PNA", "Cancels", "Uptime")
RATE_COLUMNS = {"CVR": "% CVR", "PNA": "% PNA Orders", "Cancels": "% Cancels DTP", "Uptime": U}
ACTIONS = {"CVR": ("Review assortment, pricing and the conversion journey", "Improve conversion against the SBU benchmark"),
           "PNA": ("Review stock accuracy and availability of affected products", "Reduce PNA-affected demand"),
           "Cancels": ("Review partner-cancelled orders and resolve the main failure reasons", "Reduce partner-caused cancellations"),
           "Uptime": ("Restore availability during scheduled opening hours", "Improve uptime toward the 95% target")}


def interpolate_score(value, anchors):
    if not present(value):
        return None
    return float(np.interp(float(value), [p[0] for p in anchors], [p[1] for p in anchors]))


def confidence_adjusted_rate(rate, benchmark, denominator, k):
    if not all(present(x) for x in (rate, benchmark, denominator, k)) or denominator < 0 or k <= 0:
        return None
    weight = denominator / (denominator + k)
    return weight * rate + (1 - weight) * benchmark


def protected_average(values, weights):
    """Fixed eligible weights; unknown metrics are handled before official scoring."""
    if not values:
        return 0.0
    return max(sum(v * w for v, w in zip(values, weights)) / sum(weights),
               cfg.PEAK_SEVERITY_FLOOR_MULTIPLIER * max(values))


@dataclass
class MetricScore:
    metric: str
    eligible: bool
    raw_rate: float | None = None
    benchmark: float | None = None
    denominator: float | None = None
    numerator: float | None = None
    adjusted_rate: float | None = None
    confidence_weight: float | None = None
    relative_gap: float | None = None
    severity: float | None = None
    exposure: float | None = None
    impact: float | None = None
    paired_priority: float | None = None
    state: str = "Missing"
    reason: str = ""
    critical_flag: str = ""
    exposure_basis: str = "Adjusted benchmark gap"
    benchmark_period: str = ""
    action: str = ""
    intended_effect: str = ""

    def record(self):
        return asdict(self)


def _value(row, column):
    value = row.get(column) if row is not None else None
    return float(value) if present(value) else None


def _raw_flag(metric, rate, denominator, benchmark):
    if rate is None:
        return ""
    if metric == "CVR" and denominator is not None and denominator >= cfg.CRITICAL_CVR_MIN_SESSIONS and benchmark is not None and benchmark > 0:
        return "Critical CVR" if rate <= benchmark * (1 - cfg.CRITICAL_CVR_RELATIVE_GAP) + 1e-12 else ""
    if metric == "PNA" and rate >= cfg.CRITICAL_PNA_RATE:
        return "Critical PNA"
    if metric == "Cancels" and rate >= cfg.CRITICAL_CANCELS_RATE:
        return "Critical Cancels"
    if metric == "Uptime" and rate < cfg.CRITICAL_UPTIME_RATE:
        return "Critical Uptime"
    return ""


def uptime_exposure(row, history, period, settings):
    uptime = _value(row, U)
    attempts = _value(row, T)
    if uptime is None:
        return None, "Missing uptime"
    deficit = max(0.0, (cfg.UPTIME_TARGET - uptime) / cfg.UPTIME_TARGET)
    if deficit == 0:
        return 0.0, "At or above uptime target"
    past = history[(history["Period"] < period) &
                   (history["Period"] >= period - pd.DateOffset(months=settings.uptime_history_months))]
    rates = []
    for _, month in past.iterrows():
        u, n = _value(month, U), _value(month, T)
        if (u is not None and u >= cfg.UPTIME_TARGET and n is not None and n > 0
                and bool(month.get("Uptime Reliable", settings.include_uptime))
                and month.get("Data Quality", "OK") == "OK"):
            rates.append(n / (month["Period"].days_in_month * u))
    if len(rates) >= settings.uptime_min_healthy_months:
        target_volume = float(np.median(rates)) * period.days_in_month * cfg.UPTIME_TARGET
        # Growing current demand must not be capped by a quiet historical baseline.
        reference = max(target_volume, attempts or 0.0)
        return reference * deficit, f"Healthy-month baseline ({len(rates)} months; calendar-day adjusted), at least current attempts"
    if attempts is None:
        return None, "No reliable healthy-month baseline or current attempt count"
    return attempts * deficit, "Observed-attempt exposure fallback; restoration demand uncertain"


def score_metrics(row, benchmark, history, period, settings, benchmark_period=None):
    scores = []
    lifecycle = row.get("Store Status", "Unknown")
    uptime_eligible = settings.include_uptime and bool(row.get("Uptime Reliable", True))
    for metric in METRICS:
        eligible = metric != "Uptime" or uptime_eligible
        raw = _value(row, RATE_COLUMNS[metric])
        b = cfg.UPTIME_TARGET if metric == "Uptime" else _value(benchmark, RATE_COLUMNS[metric])
        n = None if metric == "Uptime" else _value(row, N if metric == "CVR" else T)
        numerator_column = ("Converted Sessions" if settings.cvr_mode == "converted_sessions" else D) if metric == "CVR" else P if metric == "PNA" else C
        numerator = None if metric == "Uptime" or (metric == "CVR" and settings.cvr_mode == "reported") else _value(row, numerator_column)
        action, effect = ACTIONS[metric]
        m = MetricScore(metric, eligible, raw, b, n, numerator,
                        benchmark_period=benchmark_period.strftime("%Y-%m") if benchmark_period is not None else "",
                        action=action, intended_effect=effect)
        if lifecycle in {"Closed", "No Activity"} and row.get("Data Quality") == "OK":
            m.state, m.reason = "Inactive", row.get("Store Status Reason", lifecycle)
            m.severity = m.exposure = m.impact = m.paired_priority = 0.0
            scores.append(m)
            continue
        m.critical_flag = _raw_flag(metric, raw, n, b)
        if metric == "Uptime":
            m.severity = interpolate_score(raw, cfg.UPTIME_SEVERITY_ANCHORS)
            if not eligible:
                m.state = "Excluded"
                m.reason = "Opening-hours/uptime data quality policy"
                m.action = "Verify and correct configured store opening hours"
                m.intended_effect = "Align scheduled hours with actual operations"
                m.exposure = m.impact = m.paired_priority = 0.0
                m.exposure_basis = "Excluded from business scoring"
            elif raw is not None:
                m.exposure, m.exposure_basis = uptime_exposure(row, history, period, settings)
                if m.exposure is not None:
                    m.state = "Assessed"
                    m.impact = interpolate_score(m.exposure, cfg.IMPACT_SCORE_ANCHORS)
                    m.paired_priority = m.severity * m.impact / 100
                else:
                    m.reason = m.exposure_basis
            else:
                m.reason = "Uptime is missing"
            scores.append(m)
            continue
        k = {"CVR": cfg.CVR_CONFIDENCE_K, "PNA": cfg.PNA_CONFIDENCE_K, "Cancels": cfg.CANCELS_CONFIDENCE_K}[metric]
        m.confidence_weight = n / (n + k) if n is not None else None
        if n == 0 and ((metric != "CVR") or not any(_value(row, key) and _value(row, key) > 0 for key in (D, T))):
            m.state, m.reason = "No exposure", "Zero observed denominator; rate not applicable"
            m.severity = m.exposure = m.impact = m.paired_priority = 0.0
            scores.append(m)
            continue
        if n is None or n <= 0 or raw is None or b is None or (metric == "CVR" and b <= 0):
            m.reason = "Missing/zero denominator, rate or usable benchmark"
            scores.append(m)
            continue
        m.adjusted_rate = confidence_adjusted_rate(raw, b, n, k)
        if metric == "CVR":
            gap = max(0.0, b - m.adjusted_rate)
            m.relative_gap = gap / b
            anchors = cfg.CVR_SEVERITY_ANCHORS
        else:
            gap = max(0.0, m.adjusted_rate - b)
            floor = cfg.PNA_BENCHMARK_FLOOR if metric == "PNA" else cfg.CANCELS_BENCHMARK_FLOOR
            m.relative_gap = gap / max(b, floor)
            anchors = cfg.PNA_SEVERITY_ANCHORS if metric == "PNA" else cfg.CANCELS_SEVERITY_ANCHORS
        m.severity = interpolate_score(m.relative_gap, anchors)
        m.exposure = n * gap
        m.impact = interpolate_score(m.exposure, cfg.IMPACT_SCORE_ANCHORS)
        m.paired_priority = m.severity * m.impact / 100
        m.state = "Assessed"
        scores.append(m)
    return scores


def summarize_scores(row, metrics, settings):
    eligible = [m for m in metrics if m.eligible]
    nonactive = row.get("Store Status") in {"Closed", "No Activity"} and row.get("Data Quality") == "OK"
    complete = nonactive or (row.get("Store Status") == "Active" and row.get("Data Quality") == "OK"
                            and all(m.state in {"Assessed", "No exposure"} for m in eligible))
    weights = [cfg.WEIGHTS[m.metric] for m in eligible]
    known_severity = protected_average([m.severity or 0.0 for m in eligible], weights)
    known_priority = protected_average([m.paired_priority or 0.0 for m in eligible], weights)
    known_impact = max((m.impact or 0.0 for m in eligible), default=0.0)
    simple = known_severity * known_impact / 100
    priority = known_priority if settings.priority_model == "paired" else simple
    def strongest(attribute):
        candidates = [m for m in eligible if getattr(m, attribute) is not None and getattr(m, attribute) > 0]
        if not candidates:
            return None
        return max(candidates, key=lambda m: (getattr(m, attribute), m.exposure or 0.0, m.severity or 0.0, -METRICS.index(m.metric)))
    driver = strongest("paired_priority")
    worst = strongest("severity")
    exposure = strongest("exposure")
    flags = [m.critical_flag for m in metrics if m.critical_flag]
    result = {
        "Scoring Status": "Not applicable" if nonactive else "Complete" if complete else "Incomplete",
        "Scoring Scope": "CVR, PNA, Cancels, Uptime" if any(m.eligible and m.metric == "Uptime" for m in metrics) else "Commercial only; uptime hygiene separate",
        "Performance Severity Score": known_severity if complete else np.nan,
        "Business Impact Score": known_impact if complete else np.nan,
        "Opportunity Score": priority if complete else np.nan,
        "Known Severity": known_severity, "Known Impact": known_impact, "Known Priority": priority,
        "Simple Product Priority": simple if complete else np.nan,
        "Paired Priority": known_priority if complete else np.nan,
        "Main Driver": driver.metric if driver else "None",
        "Severity Driver": worst.metric if worst else "None",
        "Impact Source": exposure.metric if exposure else "No assessed exposure" if complete else "Not assessed",
        "Critical Flags": " | ".join(flags),
        "Recommended Focus": driver.action if driver and complete and not nonactive else "Review incomplete assessment" if not complete else "Review store activity" if row.get("Store Status") == "No Activity" else "Maintain performance",
        "Modeled Exposure Units": max((m.exposure or 0.0 for m in eligible), default=0.0) if complete else np.nan,
        "Metric Coverage": sum(cfg.WEIGHTS[m.metric] for m in eligible if m.state in {"Assessed", "No exposure", "Inactive"}) / sum(weights) if weights else 0.0,
        "Eligible Opportunity": bool(complete and not nonactive and driver and priority >= settings.min_priority),
    }
    for m in metrics:
        result.update({f"{m.metric} Severity": m.severity, f"{m.metric} Exposure": m.exposure,
                       f"{m.metric} Impact": m.impact, f"{m.metric} Priority Component": m.paired_priority,
                       f"{m.metric} Assessment": m.state,
                       f"{m.metric} Confidence Weight": m.confidence_weight})
    return result
