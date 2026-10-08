"""Lifecycle inference is separate from data quality and business scoring."""
import numpy as np
import pandas as pd

from config import CLOSED_STORE_MONTHS
from data_pipeline import D, N, T, U, present


def activity(row):
    return any(present(row.get(k)) and row.get(k) > 0 for k in (D, N, T))


def derive_store_status(row, history, period, settings, current_present=True):
    if not current_present:
        return {"Store Status": "Unknown", "Data Quality": "Missing current data",
                "Store Status Reason": "No store row in the reporting month", "Closure Evidence": "Unassessed",
                "Operating Cohort": False}
    complete = all(present(row.get(k)) for k in (D, N, T))
    active = activity(row)
    lifecycle = str(row.get("Lifecycle Status", "")).casefold()
    reliable = settings.include_uptime and bool(row.get("Uptime Reliable", settings.include_uptime))
    expected = pd.date_range(end=period, periods=CLOSED_STORE_MONTHS, freq="MS")
    recent = history[history["Period"].isin(expected)]
    zero_run = len(recent) == CLOSED_STORE_MONTHS and all(
        present(v) and abs(float(v)) <= 1e-12 for v in recent[U])
    earlier = history[history["Period"] < expected[0]]
    prior_operating = any(activity(r) or (present(r.get(U)) and r.get(U) > 0)
                          for _, r in earlier.iterrows())
    any_prior = history[history["Period"] < period]
    ever_operating = active or any(activity(r) or (present(r.get(U)) and r.get(U) > 0)
                                  for _, r in any_prior.iterrows())
    positive_uptime = present(row.get(U)) and row.get(U) > 0
    conflict = active and (zero_run or lifecycle in {"closed", "not launched"})
    if lifecycle == "closed" and positive_uptime:
        conflict = True
    if lifecycle == "active" and zero_run:
        conflict = True
    if conflict:
        return {"Store Status": "Active" if active else "No Activity", "Data Quality": "Conflict",
                "Store Status Reason": "Activity/lifecycle contradicts closure or zero-uptime telemetry",
                "Closure Evidence": "Conflicting", "Operating Cohort": False}
    if not complete:
        return {"Store Status": "Active" if active else "Unknown", "Data Quality": "Incomplete",
                "Store Status Reason": "Activity counts are incomplete; missing is not zero",
                "Closure Evidence": "Unassessed", "Operating Cohort": bool(positive_uptime or ever_operating)}
    if lifecycle == "closed":
        return {"Store Status": "Closed", "Data Quality": "OK", "Store Status Reason": "Confirmed closed in source lifecycle",
                "Closure Evidence": "Confirmed", "Operating Cohort": False}
    if not active and zero_run and reliable and prior_operating and lifecycle != "active":
        return {"Store Status": "Closed", "Data Quality": "OK",
                "Store Status Reason": f"Inferred closed: {CLOSED_STORE_MONTHS} consecutive zero-uptime months after operating history",
                "Closure Evidence": "Inferred", "Operating Cohort": False}
    if not active:
        reason = "No sessions, order attempts or deliveries in reporting month"
        if lifecycle == "not launched":
            reason = "Not launched according to source lifecycle"
        elif zero_run and not reliable:
            reason += "; verify closure/opening hours because uptime is untrusted"
        elif not ever_operating and not positive_uptime:
            reason += "; no observed operating history—verify activation"
        return {"Store Status": "No Activity", "Data Quality": "OK", "Store Status Reason": reason,
                "Closure Evidence": "Unconfirmed" if zero_run else "None",
                "Operating Cohort": bool((ever_operating or positive_uptime) and lifecycle != "not launched")}
    return {"Store Status": "Active", "Data Quality": "OK", "Store Status Reason": "Current sessions or order activity",
            "Closure Evidence": "None", "Operating Cohort": True}


def add_lifecycle(data):
    records = []
    for _, history in data.store_monthly.groupby("Store ID", sort=True):
        history = history.sort_values("Period")
        for _, row in history.iterrows():
            record = row.to_dict()
            record.update(derive_store_status(row, history[history["Period"] <= row["Period"]], row["Period"], data.settings))
            records.append(record)
    data.store_monthly = pd.DataFrame(records)
    # Recompute uptime over the observed operating cohort, retaining coverage.
    for idx, month in data.monthly.iterrows():
        group = data.store_monthly[data.store_monthly["Period"] == month["Period"]]
        cohort = group[group["Operating Cohort"]]
        known_uptime = cohort[U].dropna()
        data.monthly.at[idx, "All Store Uptime"] = group[U].mean()
        data.monthly.at[idx, U] = float(known_uptime.mean()) if not known_uptime.empty else np.nan
        data.monthly.at[idx, "Operating Store Count"] = len(cohort)
        data.monthly.at[idx, "Uptime Known Store Count"] = int(cohort[U].notna().sum())
        data.monthly.at[idx, "Uptime Value Coverage"] = float(cohort[U].notna().mean()) if len(cohort) else 0.0
        data.monthly.at[idx, "Closed Store Count"] = int((group["Store Status"] == "Closed").sum())
        data.monthly.at[idx, "Excluded Store Count"] = len(group) - len(cohort)


def current_store_rows(data):
    records = []
    for sid, history in data.store_monthly.groupby("Store ID", sort=True):
        latest = history.sort_values("Period").iloc[-1]
        if latest["Period"] == data.reporting_period:
            record = latest.to_dict()
        else:
            record = {column: np.nan for column in data.store_monthly.columns}
            record.update({"Store ID": sid, "Store Address Address": latest["Store Address Address"],
                           "Period": data.reporting_period, "Lifecycle Status": "", "Uptime Reliable": False})
            record.update(derive_store_status(record, history, data.reporting_period, data.settings, False))
        record["Last Observed Period"] = latest["Period"]
        records.append(record)
    return pd.DataFrame(records)
