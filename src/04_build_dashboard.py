"""Aggregate the clean data into a compact cube and inject it into the dashboard template."""
import json
import numpy as np
import pandas as pd
from config import CLEAN_FILE, TEMPLATE, DASHBOARD_OUT, LEAD_LABELS

df = pd.read_csv(CLEAN_FILE)
top = list(df.country.value_counts().head(12).index)
df["cty"] = df.country.where(df.country.isin(top), "Other")
yms = sorted(df.arrival_ym.unique())
dims = {
    "hotel": sorted(df.hotel.unique()), "ym": yms,
    "ch": ["Online Travel Agent", "Offline Travel Agent", "Direct", "Corporate", "Undefined"],
    "ct": ["Transient", "Transient-Party", "Contract", "Group"],
    "dep": ["No Deposit", "Non Refundable", "Refundable"],
    "cty": top + ["Other"], "lb": LEAD_LABELS,
}
code = lambda col, lst: df[col].map({v: i for i, v in enumerate(lst)})
df["h"], df["m"] = code("hotel", dims["hotel"]), code("arrival_ym", yms)
df["c"], df["t"] = code("distribution_channel", dims["ch"]), code("customer_type", dims["ct"])
df["d"], df["y"], df["l"] = code("deposit_type", dims["dep"]), code("cty", dims["cty"]), code("lead_bin", LEAD_LABELS)
df["stay_nights"] = np.where(df.stay_completed == 1, df.nights, 0)
df["adr_sum"] = np.where(df.adr_valid == 1, df.adr, 0)

g = (df.groupby(["h", "m", "c", "t", "d", "y", "l", "is_duplicate"])
       .agg(n=("canceled", "size"), k=("canceled", "sum"), rev=("revenue", "sum"), loss=("loss_abs", "sum"),
            ln=("stay_nights", "sum"), lc=("stay_completed", "sum"), a_s=("adr_sum", "sum"),
            a_n=("adr_valid", "sum"), ld=("lead_time", "sum")).reset_index())
for c in ["rev", "loss", "a_s"]:
    g[c] = g[c].round(0)
rows = g.astype(int).values.tolist()
payload = json.dumps({"dims": dims, "rows": rows}, separators=(",", ":"))
DASHBOARD_OUT.parent.mkdir(exist_ok=True)
DASHBOARD_OUT.write_text(TEMPLATE.read_text(encoding="utf-8").replace("__DATA__", payload), encoding="utf-8")
print(f"Wrote {DASHBOARD_OUT} ({len(rows):,} cube rows, {DASHBOARD_OUT.stat().st_size/1e6:.2f} MB)")
