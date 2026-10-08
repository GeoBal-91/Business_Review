"""V9_Beta2 settings. Importing this module does not read data or create files."""
from dataclasses import dataclass
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PARTNER_SBU = "JEWELRY"
INPUT_FILE = BASE_DIR / "partner_data.xlsx"
SUBBUSINESS_FILE = BASE_DIR / "subbusiness_unit_data.xlsx"
OUTPUT_FILE = BASE_DIR / "Partner_Business_Review_V9_Beta2.pptx"

# Official contract: source % CVR, session-weighted at partner/SBU level.
# Delivered / sessions is a reconciliation diagnostic, never a scoring option.
CVR_MODE = "reported"
PERCENTAGE_UNITS = "fraction"       # fraction (0.8) or percent (80); "80%" is explicit.
PRIORITY_MODEL = "paired"          # paired or simple_product; both have zero floor.
MIN_PRIORITY_FOR_MAIN_SLIDES = 5.0  # provisional Dev6 threshold; validate with AMs.
FLOWERS_UPTIME_IMPACT_EXCLUDED = True
REPORTING_PERIOD = None             # optional "2026-08"; default latest input month.
MAX_BENCHMARK_LAG_MONTHS = 0         # 0 requires same-month benchmark.
ALLOW_PARTIAL_PERIOD = False
ALLOW_PARTITIONED_ROWS = False      # only enable for genuinely additive input rows.
TREND_MONTHS = 12
TOP_OPPORTUNITIES_COUNT = 6
FONT = "Montserrat"

CVR_CONFIDENCE_K = 150.0
PNA_CONFIDENCE_K = 30.0
CANCELS_CONFIDENCE_K = 10.0
UPTIME_TARGET = 0.95
WEIGHTS = {"CVR": 0.30, "PNA": 0.30, "Cancels": 0.25, "Uptime": 0.15}
PEAK_SEVERITY_FLOOR_MULTIPLIER = 0.50
PNA_BENCHMARK_FLOOR = 0.05
CANCELS_BENCHMARK_FLOOR = 0.03
CRITICAL_CVR_RELATIVE_GAP = 0.70
CRITICAL_CVR_MIN_SESSIONS = 30
CRITICAL_PNA_RATE = 0.30
CRITICAL_CANCELS_RATE = 0.20
CRITICAL_UPTIME_RATE = 0.60
CLOSED_STORE_MONTHS = 3
CVR_TOLERANCE_PP = 0.01

CVR_SEVERITY_ANCHORS = ((0, 0), (.10, 10), (.20, 28), (.30, 45), (.40, 58),
                        (.50, 68), (.70, 85), (1, 100))
PNA_SEVERITY_ANCHORS = ((0, 0), (.20, 10), (.50, 25), (1, 50), (2, 75), (3, 90), (4, 100))
CANCELS_SEVERITY_ANCHORS = ((0, 0), (.25, 10), (.50, 25), (1, 50), (1.5, 70), (2, 85), (3, 100))
UPTIME_SEVERITY_ANCHORS = ((.40, 100), (.60, 75), (.75, 45), (.85, 25), (.90, 10), (.95, 0), (1, 0))
IMPACT_SCORE_ANCHORS = ((0, 0), (5, 15), (10, 25), (25, 40), (50, 55), (100, 70), (200, 85), (400, 100))


@dataclass(frozen=True)
class Settings:
    partner_sbu: str = PARTNER_SBU
    input_file: Path = INPUT_FILE
    subbusiness_file: Path = SUBBUSINESS_FILE
    output_file: Path = OUTPUT_FILE
    cvr_mode: str = CVR_MODE
    percentage_units: str = PERCENTAGE_UNITS
    priority_model: str = PRIORITY_MODEL
    min_priority: float = MIN_PRIORITY_FOR_MAIN_SLIDES
    flowers_uptime_excluded: bool = FLOWERS_UPTIME_IMPACT_EXCLUDED
    reporting_period: str | None = REPORTING_PERIOD
    max_benchmark_lag_months: int = MAX_BENCHMARK_LAG_MONTHS
    allow_partial_period: bool = ALLOW_PARTIAL_PERIOD
    allow_partitioned_rows: bool = ALLOW_PARTITIONED_ROWS
    as_of_date: date | None = None
    trend_months: int = TREND_MONTHS
    top_opportunities: int = TOP_OPPORTUNITIES_COUNT
    uptime_history_months: int = 6
    uptime_min_healthy_months: int = 2

    def __post_init__(self):
        object.__setattr__(self, "partner_sbu", self.partner_sbu.strip().upper())
        for key in ("input_file", "subbusiness_file", "output_file"):
            object.__setattr__(self, key, Path(getattr(self, key)))
        if self.cvr_mode != "reported":
            raise ValueError("Dev6.1 official CVR is reported; alternate CVR scoring modes are disabled. Delivered / sessions is diagnostic only.")
        if self.percentage_units not in {"fraction", "percent"}:
            raise ValueError("PERCENTAGE_UNITS must be fraction or percent")
        if self.priority_model not in {"paired", "simple_product"}:
            raise ValueError("PRIORITY_MODEL must be paired or simple_product")
        if not 0 <= self.min_priority <= 100:
            raise ValueError("MIN_PRIORITY_FOR_MAIN_SLIDES must be between 0 and 100")
        if self.max_benchmark_lag_months < 0:
            raise ValueError("Benchmark lag cannot be negative")
        if min(self.trend_months, self.top_opportunities, self.uptime_history_months, self.uptime_min_healthy_months) < 1:
            raise ValueError("Window sizes and output counts must be positive")

    @property
    def include_uptime(self):
        return not (self.partner_sbu == "FLOWERS" and self.flowers_uptime_excluded)

    @property
    def conversion_label(self):
        return "CVR"

    @property
    def conversion_description(self):
        return "Official reported CVR; partner/SBU aggregate weighted by sessions"
