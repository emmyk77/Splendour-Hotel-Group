"""Parse the raw markdown table, convert dates, add derived fields, save a clean CSV."""
import gzip
import numpy as np
import pandas as pd
from config import RAW_FILE, CLEAN_FILE, TABLES, LEAD_BINS, LEAD_LABELS, ADR_MAX_VALID


def read_markdown_table(path):
    rows = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("|"):
                rows.append([c.strip() for c in line.strip("|").split("|")])
    header, body = rows[0], rows[2:]          # rows[1] is the |---| separator
    return pd.DataFrame(body, columns=header)


def excel_serial_to_date(s):
    return pd.to_datetime("1899-12-30") + pd.to_timedelta(pd.to_numeric(s), unit="D")


def main():
    raw = read_markdown_table(RAW_FILE)
    df = pd.DataFrame({
        "booking_id": pd.to_numeric(raw["Booking ID"]),
        "hotel": raw["Hotel"],
        "booking_date": excel_serial_to_date(raw["Booking Date"]),
        "arrival_date": excel_serial_to_date(raw["Arrival Date"]),
        "lead_time": pd.to_numeric(raw["Lead Time"]),
        "nights": pd.to_numeric(raw["Nights"]),
        "guests": pd.to_numeric(raw["Guests"]),
        "distribution_channel": raw["Distribution Channel"],
        "customer_type": raw["Customer Type"],
        "country": raw["Country"].replace("", "Unknown"),
        "deposit_type": raw["Deposit Type"],
        "adr": pd.to_numeric(raw["Avg Daily Rate"]),
        "status": raw["Status"],
        "status_update": excel_serial_to_date(raw["Status Update"]),
        "canceled": pd.to_numeric(raw["Cancelled (0/1)"]),
        "revenue": pd.to_numeric(raw["Revenue"]),
        "revenue_loss": pd.to_numeric(raw["Revenue Loss"]),
    })

    # Derived fields
    df["arrival_year"] = df.arrival_date.dt.year
    df["arrival_month"] = df.arrival_date.dt.month
    df["arrival_ym"] = df.arrival_date.dt.to_period("M").astype(str)
    df["lead_bin"] = pd.cut(df.lead_time, LEAD_BINS, labels=LEAD_LABELS).astype(str)
    df["loss_abs"] = -df.revenue_loss                      # lost revenue as a positive number
    df["potential_revenue"] = df.revenue + df.loss_abs
    df["adr_valid"] = ((df.adr > 0) & (df.adr < ADR_MAX_VALID)).astype(int)
    df["stay_completed"] = ((df.canceled == 0) & (df.nights > 0)).astype(int)
    keys = [c for c in df.columns[:17] if c != "booking_id"]
    df["is_duplicate"] = df.duplicated(subset=keys, keep="first").astype(int)

    # Quality checks
    assert df.booking_id.is_unique
    assert ((df.arrival_date - df.booking_date).dt.days == df.lead_time).all()
    TABLES.mkdir(parents=True, exist_ok=True)
    quality = pd.DataFrame([
        ("Rows", len(df)),
        ("Exact duplicate rows (all fields except Booking ID)", int(df.is_duplicate.sum())),
        ("Zero ADR", int((df.adr == 0).sum())),
        ("Negative ADR", int((df.adr < 0).sum())),
        ("ADR of 5,000 or more", int((df.adr >= ADR_MAX_VALID).sum())),
        ("Zero guests", int((df.guests == 0).sum())),
        ("Zero nights", int((df.nights == 0).sum())),
        ("Channel recorded as Undefined", int((df.distribution_channel == "Undefined").sum())),
        ("Blank country", int((raw["Country"] == "").sum())),
        ("Canceled flag = 1 (includes no-shows)", int(df.canceled.sum())),
        ("Status = No-Show", int((df.status == "No-Show").sum())),
    ], columns=["check", "count"])
    quality.to_csv(TABLES / "00_data_quality.csv", index=False)

    df.to_csv(CLEAN_FILE, index=False, date_format="%Y-%m-%d")
    print(quality.to_string(index=False))
    print(f"Saved {len(df):,} rows to {CLEAN_FILE}")


if __name__ == "__main__":
    main()
