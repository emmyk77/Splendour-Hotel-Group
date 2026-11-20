# Splendor Hotel Groups (SHG): Booking Data Analysis

Business intelligence project analysing 119,390 bookings from two SHG hotels (City and Resort), with arrivals from July 2015 to August 2017. It answers the questions set in the project brief: booking patterns, customer behaviour, cancellations, revenue and pricing, geography, operations, deposits, corporate bookings, lead time, and online versus offline travel agents.

**Currency.** All monetary values are reported in Nigerian naira (₦). The source file does not state a currency, and no conversion was applied.

**Author:** Emmanuel Kebodi Friday

## Dashboard preview

![Booking analysis dashboard highlights](images/dashboard-preview.png)

*Static preview created from the project result tables. The interactive dashboard is available in [docs/index.html](docs/index.html); download the repository and open that file in a browser.*

## Deliverables

| Deliverable | Where |
|---|---|
| Interactive dashboard (filters for hotel, channel, customer type, deposit, country, lead time, year) | `docs/index.html` |
| Full written report and methodology | `reports/` and `documentation/` |
| Every result table behind the report (41 CSV files) | `outputs/tables/` |
| Reproducible code | `src/` |

To view the dashboard, open `docs/index.html` in a browser. To publish it as a web page, go to the repository's Settings, then Pages, and choose the `main` branch with the `/docs` folder. The dashboard loads Chart.js and fonts from the internet, so it needs a connection.

## Headline findings

- Revenue collected is ₦29.60M. A further ₦13.12M was lost to cancellations, so 69.3% of potential revenue (₦42.72M) was realised.
- 37.0% of bookings carry the cancellation flag. Online travel agents provide 62.0% of bookings but 82.2% of lost revenue, with a 43.2% cancellation rate against 17.5% for direct bookings.
- Revenue for January to August 2017 was 21.7% above the same months of 2016, but the cancellation rate rose from 34.7% to 38.7%.
- Direct bookings have the best profile: ADR of ₦112.88 and revenue per booking of ₦302.7, with the lowest cancellation rate among the large channels.
- Portugal supplies 40.7% of bookings and cancels at 56.6%. Guests from the UK, Germany and France cancel at 17% to 20% and stay longer.
- Bookings made more than 180 days ahead cancel at 55% to 68%. Bookings made within a week cancel at 9.6%.
- Resort pricing is highly seasonal: August ADR is ₦188.5 against ₦50.9 in January.
- Corporate bookings are 5.6% of volume with the lowest ADR (₦71.4 against ₦103.5 overall).
- A gradient boosting model predicts cancellations with an AUC of 0.91 (0.83 after removing duplicate rows). Country, deposit type, lead time and channel are the strongest drivers.
- Sunday is the busiest check-out day (120 per day on average) and Tuesday the quietest (78).

## Data notes you should know about

1. **Duplicate rows.** 35,284 rows (29.6%) match another row on every field except Booking ID. Headline figures include them. Without them the cancellation rate is 28.2% instead of 37.0%. The dashboard has a filter to exclude them.
2. **Non-refundable deposits** are 99.4% cancelled, which is the opposite of what one would expect. 97% are Portuguese bookings, so this is probably how one market or rate plan is recorded. Treat it as a data question, not as a causal result.
3. **Revenue Loss** is negative for cancelled bookings in the data, the reverse of the wording in the brief.
4. **Corporate** exists only as a distribution channel, not a customer type, so the corporate analysis uses the channel.
5. **Customer satisfaction** is not in the data, so revenue per booking and cancellation rate stand in for it in the lead time analysis.
6. The Canceled flag includes 1,207 no-shows.

See `documentation/methodology.md` for definitions and every cleaning decision.

## Project structure

```
shg-booking-analysis/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/SHG_Booking_Data.md.gz     original data, gzip-compressed
│   └── processed/shg_clean.csv.gz     cleaned data, gzip-compressed
├── src/
│   ├── config.py                      paths and constants
│   ├── 01_prepare_data.py             parse, clean, add derived fields, quality checks
│   ├── 02_analysis.py                 all brief questions, saved as CSV tables
│   ├── 03_cancellation_model.py       cancellation prediction and feature importance
│   └── 04_build_dashboard.py          builds the dashboard from the template
├── outputs/tables/                    41 result tables (CSV)
├── dashboard/template.html            dashboard source
├── docs/index.html                    built dashboard (GitHub Pages ready)
├── documentation/
│   ├── project_brief.md
│   ├── data_dictionary.md
│   └── methodology.md
└── reports/
    └── SHG_Analysis_Report.md         findings and recommendations
```

The datasets are gzip-compressed to make uploading and downloading easier. Extract them to view the original Markdown or CSV files; the Python scripts read the compressed files directly.

## How to reproduce

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd src
python 01_prepare_data.py
python 02_analysis.py
python 03_cancellation_model.py
python 04_build_dashboard.py
```

The scripts run in order and rebuild `data/processed/`, `outputs/tables/` and `docs/index.html`. Tested with Python 3.12, pandas 3, scikit-learn 1.9.

## Tools

Python (pandas, NumPy, SciPy, scikit-learn) for analysis and modelling. HTML, JavaScript and Chart.js for the dashboard.
