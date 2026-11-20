"""Run the analyses listed in the project brief and save each result as a CSV table."""
import numpy as np
import pandas as pd
from scipy import stats
from config import CLEAN_FILE, TABLES, LEAD_LABELS

df = pd.read_csv(CLEAN_FILE, parse_dates=["booking_date", "arrival_date", "status_update"])
df["origin"] = np.where(df.country == "Portugal", "Portugal", "International")
adr_ok = df[df.adr_valid == 1]
done = df[df.stay_completed == 1]
TABLES.mkdir(parents=True, exist_ok=True)


def save(table, name, index=True):
    table.round(3).to_csv(TABLES / f"{name}.csv", index=index)


def segment(col, data=df, order=None):
    """Standard KPI table for any grouping column."""
    g = data.groupby(col, observed=True)
    t = pd.DataFrame({
        "bookings": g.size(),
        "share_pct": g.size() / len(data) * 100,
        "cancel_rate_pct": g.canceled.mean() * 100,
        "revenue": g.revenue.sum(),
        "revenue_share_pct": g.revenue.sum() / data.revenue.sum() * 100,
        "revenue_lost": g.loss_abs.sum(),
        "loss_share_pct": g.loss_abs.sum() / data.loss_abs.sum() * 100,
        "revenue_realisation_pct": g.revenue.sum() / g.potential_revenue.sum() * 100,
        "revenue_per_booking": g.revenue.mean(),
        "avg_lead_time": g.lead_time.mean(),
    })
    t["adr"] = adr_ok.groupby(col, observed=True).adr.mean()
    t["avg_stay_nights"] = done.groupby(col, observed=True).nights.mean()
    t = t.sort_values("bookings", ascending=False)
    return t.reindex(order) if order else t


# ---- Headline -------------------------------------------------------------
headline = pd.Series({
    "bookings": len(df), "revenue": df.revenue.sum(), "revenue_lost": df.loss_abs.sum(),
    "potential_revenue": df.potential_revenue.sum(),
    "revenue_realisation_pct": df.revenue.sum() / df.potential_revenue.sum() * 100,
    "cancel_rate_pct": df.canceled.mean() * 100, "avg_adr": adr_ok.adr.mean(),
    "avg_stay_nights": done.nights.mean(), "avg_lead_time": df.lead_time.mean(),
    "retained_revenue_from_canceled": df[df.canceled == 1].revenue.sum(),
})
save(headline.to_frame("value"), "01_headline_kpis")

# ---- Booking patterns -----------------------------------------------------
monthly = df.groupby("arrival_ym").agg(bookings=("canceled", "size"), cancel_rate_pct=("canceled", lambda s: s.mean() * 100),
                                       revenue=("revenue", "sum"), revenue_lost=("loss_abs", "sum"))
monthly["adr"] = adr_ok.groupby("arrival_ym").adr.mean()
save(monthly, "02_monthly_trend")

years_seen = df.groupby("arrival_month").arrival_year.nunique()
season = pd.DataFrame({
    "bookings_2016": df[df.arrival_year == 2016].groupby("arrival_month").size(),
    "avg_bookings_per_year": df.groupby("arrival_month").size() / years_seen,
    "avg_revenue_per_year": df.groupby("arrival_month").revenue.sum() / years_seen,
    "cancel_rate_pct": df.groupby("arrival_month").canceled.mean() * 100,
    "adr": adr_ok.groupby("arrival_month").adr.mean(),
})
save(season, "03_seasonality")
save(df[df.arrival_month <= 8].groupby("arrival_year").agg(
    bookings=("canceled", "size"), revenue=("revenue", "sum"), cancel_rate_pct=("canceled", lambda s: s.mean() * 100)),
    "04_jan_to_aug_year_on_year")

lead_ch = df.groupby("distribution_channel").lead_time.agg(["mean", "median"])
lead_ct = df.groupby("customer_type").lead_time.agg(["mean", "median"])
save(lead_ch, "05_lead_time_by_channel"); save(lead_ct, "06_lead_time_by_customer_type")
save(df.pivot_table(index="distribution_channel", columns="customer_type", values="lead_time", aggfunc="mean"), "07_lead_time_channel_x_customer")
kw = stats.kruskal(*[g.lead_time.values for _, g in df.groupby("customer_type")])
save(pd.DataFrame({"statistic": [kw.statistic], "p_value": [kw.pvalue]}), "08_kruskal_lead_by_customer_type", index=False)

# ---- Segments -------------------------------------------------------------
save(segment("hotel"), "10_hotel")
save(segment("distribution_channel"), "11_channel")
save(segment("customer_type"), "12_customer_type")
save(segment("deposit_type"), "13_deposit_type")
save(segment("lead_bin", order=LEAD_LABELS), "14_lead_time_bands")
country = segment("country")
save(country.head(25), "15_country_top25")
save(segment("origin"), "16_portugal_vs_international")

# ---- Pricing --------------------------------------------------------------
save(adr_ok.pivot_table(index="distribution_channel", columns="customer_type", values="adr", aggfunc="mean"), "20_adr_channel_x_customer")
save(adr_ok.pivot_table(index="arrival_month", columns="hotel", values="adr", aggfunc="mean"), "21_adr_month_x_hotel")
save(adr_ok.pivot_table(index="distribution_channel", columns="hotel", values="adr", aggfunc="mean"), "22_adr_channel_x_hotel")

# ---- Cancellation and revenue loss ---------------------------------------
save(df.pivot_table(index="distribution_channel", columns="customer_type", values="loss_abs", aggfunc="sum"), "30_loss_channel_x_customer")
save(df.pivot_table(index="distribution_channel", columns="hotel", values="loss_abs", aggfunc="sum"), "31_loss_channel_x_hotel")
canc = df[df.canceled == 1]
save(pd.DataFrame({"by_channel": canc.groupby("distribution_channel").loss_abs.mean()}), "32_avg_loss_per_canceled_booking")
d = df.assign(intl=(df.country != "Portugal").astype(int), city=(df.hotel == "City").astype(int),
              non_refundable=(df.deposit_type == "Non Refundable").astype(int),
              ota=(df.distribution_channel == "Online Travel Agent").astype(int),
              transient=(df.customer_type == "Transient").astype(int))
cols = ["lead_time", "nights", "guests", "adr", "non_refundable", "intl", "city", "ota", "transient"]
save(d[cols + ["canceled"]].corr()["canceled"].drop("canceled").sort_values(ascending=False).to_frame("correlation_with_cancellation"), "33_cancellation_correlations")
df["guest_band"] = pd.cut(df.guests, [-1, 1, 2, 3, 100], labels=["0-1", "2", "3", "4+"]).astype(str)
df["stay_band"] = pd.cut(df.nights, [-1, 0, 1, 3, 7, 100], labels=["0", "1", "2-3", "4-7", "8+"]).astype(str)
for col in ["guest_band", "stay_band", "arrival_month"]:
    save(df.groupby(col).canceled.mean().mul(100).to_frame("cancel_rate_pct"), f"34_cancel_rate_by_{col}")
nr = df[df.deposit_type == "Non Refundable"]
save(pd.Series({"non_refundable_bookings": len(nr), "share_portugal_pct": (nr.country == "Portugal").mean() * 100,
                "mean_lead_time": nr.lead_time.mean(), "cancel_rate_pct": nr.canceled.mean() * 100,
                "revenue_retained": nr.revenue.sum()}).to_frame("value"), "35_non_refundable_profile")
save(pd.crosstab(df.customer_type, df.deposit_type, normalize="index") * 100, "36_deposit_mix_by_customer_type")
save(pd.crosstab(df.distribution_channel, df.deposit_type, normalize="index") * 100, "37_deposit_mix_by_channel")

# ---- Corporate and travel agents -----------------------------------------
corp = df[df.distribution_channel == "Corporate"]
save(pd.Series({
    "bookings": len(corp), "share_pct": len(corp) / len(df) * 100, "revenue": corp.revenue.sum(),
    "revenue_share_pct": corp.revenue.sum() / df.revenue.sum() * 100,
    "adr": adr_ok[adr_ok.distribution_channel == "Corporate"].adr.mean(), "overall_adr": adr_ok.adr.mean(),
    "median_lead_time": corp.lead_time.median(), "avg_guests": corp.guests.mean(),
    "avg_stay_nights": corp[corp.stay_completed == 1].nights.mean(), "cancel_rate_pct": corp.canceled.mean() * 100,
    "mon_to_thu_arrival_share_pct": corp.arrival_date.dt.dayofweek.le(3).mean() * 100,
    "all_bookings_mon_to_thu_share_pct": df.arrival_date.dt.dayofweek.le(3).mean() * 100,
    "portugal_share_pct": (corp.country == "Portugal").mean() * 100,
}).to_frame("value"), "40_corporate_profile")
save(corp.groupby("arrival_month").size().to_frame("bookings"), "41_corporate_by_month")
save(adr_ok[adr_ok.distribution_channel == "Corporate"].groupby("hotel").adr.mean().to_frame("adr"), "42_corporate_adr_by_hotel")
agents = segment("distribution_channel").loc[["Online Travel Agent", "Offline Travel Agent"]]
ex_nr = df[df.deposit_type != "Non Refundable"].groupby("distribution_channel").canceled.mean() * 100
agents["cancel_rate_ex_non_refundable_pct"] = ex_nr
save(agents, "43_online_vs_offline_agents")
save(df[df.distribution_channel.isin(["Online Travel Agent", "Offline Travel Agent"])].groupby(["distribution_channel", "hotel"]).canceled.mean().mul(100).to_frame("cancel_rate_pct"), "44_agents_cancel_by_hotel")

# ---- Operations -----------------------------------------------------------
save(done.pivot_table(index="arrival_month", columns="hotel", values="nights", aggfunc="mean"), "50_stay_by_month_hotel")
co = df[df.status == "Check-Out"]
daily = co.groupby("status_update").size()
daily = daily.reindex(pd.date_range(daily.index.min(), daily.index.max()), fill_value=0)
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
save(daily.groupby(daily.index.day_name()).mean().reindex(order).to_frame("avg_checkouts_per_day"), "51_checkouts_by_weekday")
save(daily.groupby(daily.index.month).mean().to_frame("avg_checkouts_per_day"), "52_checkouts_by_month")
save(pd.Series({"avg_per_day": daily.mean(), "peak_day": str(daily.idxmax().date()), "peak_count": daily.max()}).to_frame("value"), "53_checkout_peak")

# ---- Duplicate sensitivity -----------------------------------------------
nd = df[df.is_duplicate == 0]
save(pd.DataFrame({
    "all_rows": [len(df), df.canceled.mean() * 100, df.revenue.sum(), df.loss_abs.sum()],
    "duplicates_removed": [len(nd), nd.canceled.mean() * 100, nd.revenue.sum(), nd.loss_abs.sum()],
}, index=["bookings", "cancel_rate_pct", "revenue", "revenue_lost"]), "60_duplicate_sensitivity")
print(headline.round(2).to_string())
print(f"Saved {len(list(TABLES.glob('*.csv')))} tables to {TABLES}")
