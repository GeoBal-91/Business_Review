"""Explicit ingestion and count/rate contracts; no work occurs at import time."""
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
import calendar
import hashlib
import math
import re

import numpy as np
import pandas as pd

from config import Settings

D = "# Delivered Orders"
N = "Sessions Store"
T = "Number of Total Orders"
P = "Number of Pna Orders"
C = "Number of Canceled Orders Due to Partner"
G = "€ GMV"
U = "% Uptime"
COUNTS = (D, N, T, P, C)
RATES = ("% CVR", "% PNA Orders", "% Cancels DTP", U, "% Prime Orders")


@dataclass(frozen=True)
class DataIssue:
    level: str
    code: str
    source: str
    message: str
    store_id: str = ""
    period: str = ""


class DataValidationError(ValueError):
    def __init__(self, issues):
        self.issues = list(issues)
        errors = [i for i in self.issues if i.level == "error"]
        super().__init__("Input validation failed:\n" + "\n".join(
            f"- {i.source} {i.store_id} {i.period}: {i.message}" for i in errors[:12]))


def present(value):
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def ratio(numerator, denominator):
    return float(numerator) / float(denominator) if present(numerator) and present(denominator) and denominator > 0 else np.nan


def strict_sum(series):
    """Even one missing partition must not silently become an observed zero."""
    return series.sum(min_count=len(series))


def strict_mean(series):
    return float(series.mean()) if len(series) and series.notna().all() else np.nan


def _empty(value):
    return value is None or (isinstance(value, str) and not value.strip()) or pd.isna(value)


def _period(month, year):
    if isinstance(year, (datetime, date, pd.Timestamp)):
        y = year.year
    else:
        text = str(year).strip()
        try:
            number = float(text)
            if not math.isfinite(number) or number != int(number):
                return pd.NaT
            y = int(number)
        except ValueError:
            try:
                y = pd.Timestamp(text).year
            except (ValueError, TypeError):
                return pd.NaT
    if not 1900 <= y <= 2200:
        return pd.NaT
    lookup = {name.casefold(): i for i in range(1, 13)
              for name in (calendar.month_name[i], calendar.month_abbr[i])}
    text = str(month).strip().casefold()
    if text in lookup:
        m = lookup[text]
    else:
        try:
            number = float(text)
            if number != int(number):
                return pd.NaT
            m = int(number)
        except (ValueError, OverflowError):
            return pd.NaT
    return pd.Timestamp(y, m, 1) if 1 <= m <= 12 else pd.NaT


def _identity(value):
    if isinstance(value, (float, np.floating)) and math.isfinite(value) and value.is_integer():
        return str(int(value))
    return re.sub(r"\s+", " ", str(value).strip())


def prepare_input(frame, source, settings, issues, partner=True):
    df = frame.copy(deep=True)
    df.columns = df.columns.astype(str).str.strip()
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    if df.columns.duplicated().any():
        issues.append(DataIssue("error", "duplicate_columns", source, "Duplicate column names after whitespace normalization"))
        raise DataValidationError(issues)
    required = ["Month", "Year", *COUNTS, G, U]
    required.append("% CVR")
    if not partner:
        required.append("Store Sub Business Unit")
    elif "Store ID" not in df:
        required.append("Store Address Address")
    missing = [c for c in required if c not in df]
    if missing:
        issues.append(DataIssue("error", "missing_columns", source, "Missing required columns: " + ", ".join(missing)))
        raise DataValidationError(issues)
    if not partner:
        df["Store Sub Business Unit"] = df["Store Sub Business Unit"].astype(str).str.strip().str.upper()
        df = df[df["Store Sub Business Unit"] == settings.partner_sbu].copy()
    if df.empty:
        issues.append(DataIssue("error", "empty_input", source, "No rows for the requested partner/SBU"))
        raise DataValidationError(issues)
    df = df.reset_index(drop=True)
    df["Period"] = [_period(m, y) for m, y in zip(df["Month"], df["Year"])]
    if partner:
        if "Store ID" in df:
            bad = df["Store ID"].map(_empty)
            if bad.any():
                issues.append(DataIssue("error", "missing_store_id", source, "Store ID must be populated in every row when the column is supplied"))
            df["Store ID"] = df["Store ID"].map(_identity)
        else:
            bad = df["Store Address Address"].map(_empty)
            if bad.any():
                issues.append(DataIssue("error", "missing_store_id", source, "Store address is empty; provide a stable Store ID"))
            df["Store ID"] = df["Store Address Address"].map(lambda x: "address:" + _identity(x).casefold())
            issues.append(DataIssue("info", "address_identity", source, "Store identity uses normalized address; a Store ID is recommended for renames"))
        if "Store Address Address" not in df:
            df["Store Address Address"] = df["Store ID"]
        df["Store Address Address"] = [sid if _empty(v) else _identity(v)
                                       for sid, v in zip(df["Store ID"], df["Store Address Address"])]
    else:
        df["Store ID"] = settings.partner_sbu
        df["Store Address Address"] = settings.partner_sbu

    def issue(level, code, idx, message):
        per = df.at[idx, "Period"]
        issues.append(DataIssue(level, code, source, message, str(df.at[idx, "Store ID"]),
                                per.strftime("%Y-%m") if pd.notna(per) else "invalid date"))

    for idx in df.index[df["Period"].isna()]:
        issue("error", "invalid_period", idx, f"Invalid Month/Year at Excel row {idx + 2}; row was not silently dropped")

    numeric = [*COUNTS, G, "Converted Sessions", "# Available Products", "# Avoidable WTP (min)"]
    for col in numeric:
        if col not in df:
            continue
        converted = pd.to_numeric(df[col], errors="coerce")
        for idx, original in df[col].items():
            v = converted.at[idx]
            if _empty(original):
                if col in COUNTS or col == G or (col == "Converted Sessions" and settings.cvr_mode == "converted_sessions"):
                    issue("warning", "missing_count", idx, f"{col} is missing; retained as unknown")
            elif not present(v) or v < 0:
                issue("error", "invalid_number", idx, f"{col} must be finite and nonnegative (row {idx + 2})")
            elif col in (*COUNTS, "Converted Sessions", "# Available Products") and abs(v - round(v)) > 1e-8:
                issue("error", "fractional_count", idx, f"{col} must contain whole counts (row {idx + 2})")
        df[col] = converted

    for col in RATES:
        if col not in df:
            df[col] = np.nan
            continue
        parsed = []
        for idx, original in df[col].items():
            if _empty(original):
                parsed.append(np.nan)
                continue
            explicit = isinstance(original, str) and original.strip().endswith("%")
            try:
                value = float(original.strip()[:-1] if explicit else original)
                if explicit or settings.percentage_units == "percent":
                    value /= 100
            except (TypeError, ValueError):
                value = np.nan
            if not present(value) or not 0 <= value <= 1:
                issue("error", "invalid_rate", idx, f"{col} is outside 0–100% or malformed; check PERCENTAGE_UNITS (row {idx + 2})")
            parsed.append(value)
        df[col] = parsed

    for idx, row in df.iterrows():
        for num in (D, P, C):
            if present(row[num]) and present(row[T]) and row[num] > row[T]:
                issue("error", "counts_exceed_total", idx, f"{num} exceeds total order attempts")
        if all(present(row[x]) for x in (D, C, T)) and row[D] + row[C] > row[T]:
            issue("error", "delivery_cancel_conflict", idx, "Delivered plus partner-cancelled orders exceed total attempts")
        if present(row[D]) and row[D] == 0 and present(row[G]) and row[G] > 0:
            issue("error", "gmv_delivery_conflict", idx, "Positive GMV with zero deliveries; reconcile the reporting scopes")
        if present(row[N]) and row[N] == 0 and any(present(row[k]) and row[k] > 0 for k in (D, T)):
            issue("warning", "session_coverage", idx, "Positive order activity with zero recorded sessions; conversion assessment unavailable")
        if settings.cvr_mode == "converted_sessions" and present(row["Converted Sessions"]) and present(row[N]) and row["Converted Sessions"] > row[N]:
            issue("error", "converted_exceed_sessions", idx, "Converted Sessions exceeds Sessions Store")
        for rate_col, num, den in (("% CVR", D, N), ("% PNA Orders", P, T), ("% Cancels DTP", C, T)):
            derived = ratio(row[num], row[den])
            if present(row[rate_col]) and present(derived) and abs(row[rate_col] - derived) > 0.0001:
                msg = (f"Source {rate_col}={row[rate_col]:.6f}; {num}/{den}={derived:.6f}. "
                       + (f"Using explicit {settings.cvr_mode} conversion contract." if rate_col == "% CVR" else "Count-derived rate is used; reconcile source scope."))
                issue("info" if rate_col == "% CVR" else "warning", "rate_reconciliation", idx, msg)

    if "Lifecycle Status" not in df:
        df["Lifecycle Status"] = ""
    df["Lifecycle Status"] = df["Lifecycle Status"].fillna("").astype(str).str.strip().str.casefold()
    for idx in df.index[~df["Lifecycle Status"].isin(["", "active", "closed", "not launched"])]:
        issue("error", "invalid_lifecycle", idx, "Lifecycle Status must be Active, Closed or Not Launched")
    if "Uptime Reliable" not in df:
        df["Uptime Reliable"] = settings.include_uptime
    else:
        booleans = {"true": True, "yes": True, "1": True, "1.0": True,
                    "false": False, "no": False, "0": False, "0.0": False}
        converted = []
        for idx, value in df["Uptime Reliable"].items():
            key = str(value).strip().casefold()
            if _empty(value):
                converted.append(settings.include_uptime)
            elif key in booleans:
                converted.append(booleans[key])
            else:
                issue("error", "invalid_uptime_reliability", idx, "Uptime Reliable must be true/false")
                converted.append(False)
        df["Uptime Reliable"] = converted

    dup = df.duplicated(["Store ID", "Period"], keep=False)
    if dup.any() and not settings.allow_partitioned_rows:
        for idx in df.index[dup]:
            issue("error", "duplicate_grain", idx, "Repeated store/SBU month. Remove duplicate exports or explicitly enable additive partitions")
    elif dup.any():
        issues.append(DataIssue("warning", "partitioned_input", source, "Additive partitions explicitly enabled; uptime is an unweighted mean of complete partition values"))
    if any(i.level == "error" for i in issues):
        raise DataValidationError(issues)
    return df.sort_values(["Store ID", "Period"]).reset_index(drop=True)


def aggregate_performance(df, group_cols, settings):
    records = []
    for key, group in df.groupby(group_cols, sort=True, dropna=False):
        key = key if isinstance(key, tuple) else (key,)
        row = dict(zip(group_cols, key))
        for col in (*COUNTS, G):
            row[col] = strict_sum(group[col])
        demand = group[N] > 0
        cvr_complete = group[N].notna().all() and group.loc[demand, "% CVR"].notna().all()
        row["% CVR"] = ratio((group.loc[demand, N] * group.loc[demand, "% CVR"]).sum(), row[N]) if cvr_complete else np.nan
        if "Store ID" in group_cols and len(group) == 1:
            row["% CVR"] = group["% CVR"].iloc[0]
        row["Delivered / Sessions Diagnostic"] = ratio(row[D], row[N])
        row["CVR Reconciliation Gap"] = row["% CVR"] - row["Delivered / Sessions Diagnostic"]
        row["% PNA Orders"] = ratio(row[P], row[T])
        row["% Cancels DTP"] = ratio(row[C], row[T])
        row["€ AOV Derived"] = ratio(row[G], row[D])
        known_uptime = group[U].dropna()
        row[U] = float(known_uptime.mean()) if not known_uptime.empty else np.nan
        row["Uptime Value Coverage"] = float(group[U].notna().mean())
        for col in ("# Available Products", "# Avoidable WTP (min)"):
            if col in group:
                row[col] = strict_sum(group[col]) if col == "# Available Products" else strict_mean(group[col])
        row["% Prime Orders"] = ratio((group["% Prime Orders"] * group[D]).sum(min_count=len(group)), row[D]) if "% Prime Orders" in group else np.nan
        row["Store Address Address"] = sorted(group["Store Address Address"].astype(str).unique())[0]
        if "Store ID" in group_cols:
            for metadata in ("Store Name", "City", "Location"):
                if metadata in group:
                    values = [str(v).strip() for v in group[metadata] if not _empty(v)]
                    row[metadata] = sorted(set(values))[0] if values else ""
        life = sorted(set(group["Lifecycle Status"]) - {""})
        if len(life) > 1 and "Store ID" in group_cols:
            raise DataValidationError([DataIssue("error", "conflicting_partitions", "input", "Multiple lifecycle values in the same group")])
        row["Lifecycle Status"] = life[0] if len(life) == 1 else ""
        row["Uptime Reliable"] = bool(group["Uptime Reliable"].all())
        records.append(row)
    return pd.DataFrame.from_records(records).sort_values(group_cols).reset_index(drop=True)


def period_row(frame, period):
    match = frame[frame["Period"] == period]
    return None if match.empty else match.iloc[-1]


def get_previous_month_row(frame, period):
    return period_row(frame, period - pd.DateOffset(months=1))


def get_yoy_row(frame, period):
    return period_row(frame, period - pd.DateOffset(years=1))


@dataclass
class DataBundle:
    settings: Settings
    partner_raw: pd.DataFrame
    sbu_raw: pd.DataFrame
    store_monthly: pd.DataFrame
    monthly: pd.DataFrame
    selected_sbu: pd.DataFrame
    reporting_period: pd.Timestamp
    benchmark_period: pd.Timestamp | None
    benchmark_row: pd.Series | None
    issues: list[DataIssue] = field(default_factory=list)
    input_hashes: dict = field(default_factory=dict)
    coverage: pd.DataFrame = field(default_factory=pd.DataFrame)


def load_frames(partner, sbu, settings):
    issues = []
    p = prepare_input(partner, "partner", settings, issues, True)
    s = prepare_input(sbu, "SBU", settings, issues, False)
    period = pd.Period(settings.reporting_period, freq="M").to_timestamp() if settings.reporting_period else p["Period"].max()
    if not (p["Period"] == period).any():
        raise DataValidationError([DataIssue("error", "reporting_period_missing", "partner", f"No partner rows for {period:%Y-%m}")])
    as_of = pd.Timestamp(settings.as_of_date or date.today()).to_period("M").to_timestamp()
    if period >= as_of and not settings.allow_partial_period:
        raise DataValidationError([DataIssue("error", "partial_period", "partner", f"{period:%Y-%m} is not complete; select REPORTING_PERIOD or explicitly allow partial-period analysis")])
    if period >= as_of:
        issues.append(DataIssue("warning", "partial_period", "partner", "Partial/future reporting month explicitly permitted; volume-based scores are not directly comparable"))
    # Never use future observations in lifecycle or restoration baselines.
    p = p[p["Period"] <= period].copy()
    s = s[s["Period"] <= period].copy()
    if s.empty:
        raise DataValidationError([DataIssue("error", "future_benchmarks", "SBU", "All SBU observations are after the requested reporting month")])
    stores = aggregate_performance(p, ["Store ID", "Period"], settings)
    monthly = aggregate_performance(p, ["Period"], settings)
    selected = aggregate_performance(s, ["Period"], settings)
    for _, month in monthly.iterrows():
        peer = period_row(selected, month["Period"])
        if peer is not None and present(month[G]) and present(peer[G]) and month[G] > peer[G]:
            issues.append(DataIssue("warning", "incomparable_share", "partner/SBU", "Partner GMV exceeds aggregate SBU GMV; reconcile population/currency/scope. Share is not displayed", period=month["Period"].strftime("%Y-%m")))
    candidate = selected["Period"].max()
    lag = (period.year - candidate.year) * 12 + period.month - candidate.month
    benchmark_period = candidate if lag <= settings.max_benchmark_lag_months else None
    benchmark_row = period_row(selected, benchmark_period) if benchmark_period is not None else None
    if benchmark_period is None:
        issues.append(DataIssue("warning", "missing_benchmark", "SBU", f"No allowed benchmark for {period:%Y-%m}; latest is {candidate:%Y-%m}. Business scores requiring it remain incomplete"))
    elif lag:
        issues.append(DataIssue("warning", "stale_benchmark", "SBU", f"Using explicitly allowed {lag}-month-old benchmark ({candidate:%Y-%m})"))
    return DataBundle(settings, p, s, stores, monthly, selected, period, benchmark_period, benchmark_row, issues)


def load_data(settings=None):
    settings = settings or Settings()
    paths = {"partner": settings.input_file, "SBU": settings.subbusiness_file}
    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        raise FileNotFoundError("Required input files not found: " + ", ".join(missing))
    data = load_frames(pd.read_excel(paths["partner"]), pd.read_excel(paths["SBU"]), settings)
    data.input_hashes = {str(k): hashlib.sha256(Path(p).read_bytes()).hexdigest() for k, p in paths.items()}
    return data
