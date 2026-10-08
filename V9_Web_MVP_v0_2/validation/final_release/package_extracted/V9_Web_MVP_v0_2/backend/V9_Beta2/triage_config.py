"""V2.1 interpretation settings only; never imported by the analytical engine."""
from dataclasses import asdict, dataclass
import math


@dataclass(frozen=True)
class TriageSettings:
    # Working presentation/review heuristics, not claimed calibrated model constants.
    healthy_priority_below: float = 1.0
    healthy_cvr_gap_pp: float = 1.0
    healthy_pna_gap_pp: float = 0.5
    healthy_cancels_gap_pp: float = 0.5
    healthy_uptime_min: float = 0.93
    low_delivered_max: int = 10
    low_attempts_max: int = 10
    ultra_delivered_max: int = 2
    ultra_attempts_max: int = 3

    def __post_init__(self):
        if any(not math.isfinite(v) or v < 0 for v in asdict(self).values()):
            raise ValueError('Triage settings must be finite and nonnegative')
        if not 0 <= self.healthy_priority_below <= 1 or not .93 <= self.healthy_uptime_min <= .95:
            raise ValueError('Healthy tolerance must remain conservative: Priority ≤1 and uptime ≥93%')
        if self.healthy_cvr_gap_pp > 1 or max(self.healthy_pna_gap_pp, self.healthy_cancels_gap_pp) > .5:
            raise ValueError('Healthy KPI tolerances cannot exceed the controlled defaults')
        if self.ultra_delivered_max > self.low_delivered_max or self.ultra_attempts_max > self.low_attempts_max:
            raise ValueError('Ultra-low scale must be a subset of low scale')
