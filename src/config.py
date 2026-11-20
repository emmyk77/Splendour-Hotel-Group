"""Shared paths and constants for the SHG booking analysis."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "SHG_Booking_Data.md.gz"
CLEAN_FILE = ROOT / "data" / "processed" / "shg_clean.csv.gz"
TABLES = ROOT / "outputs" / "tables"
TEMPLATE = ROOT / "dashboard" / "template.html"
DASHBOARD_OUT = ROOT / "docs" / "index.html"

CURRENCY = "NGN"          # all monetary values are reported in Nigerian naira
LEAD_BINS = [-1, 7, 30, 90, 180, 365, 10_000]
LEAD_LABELS = ["0-7", "8-30", "31-90", "91-180", "181-365", "366+"]
ADR_MAX_VALID = 5_000     # one extreme ADR of 5,400 is excluded from ADR averages
RANDOM_STATE = 42
