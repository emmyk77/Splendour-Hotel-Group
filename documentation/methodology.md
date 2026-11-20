# Methodology

## Data preparation
- The raw file is a markdown table. It is parsed into a data frame and the three date fields, stored as spreadsheet serial numbers, are converted to calendar dates.
- Checks confirm that Booking ID is unique and that Lead Time equals arrival date minus booking date on every row.
- For completed stays, Status Update equals the check-out date, which is used for the check-out analysis.
- Revenue equals ADR times nights on completed stays. On cancelled bookings, Revenue is the amount retained (the full stay value for non-refundable deposits) and Revenue Loss is the stay value not retained.

## Definitions
| Measure | Definition |
|---|---|
| Cancellation rate | Share of bookings with the Canceled flag equal to 1 (includes 1,207 no-shows) |
| Revenue | Sum of the Revenue field |
| Lost revenue | Sum of the absolute Revenue Loss field |
| Potential revenue | Revenue plus lost revenue |
| Revenue realisation | Revenue divided by potential revenue |
| ADR | Mean Avg Daily Rate over bookings with ADR above zero and below 5,000 |
| Average stay | Mean nights over completed stays of at least one night |
| Lead time bands | 0-7, 8-30, 31-90, 91-180, 181-365, 366+ days |

## Cleaning decisions
| Issue | Count | Treatment |
|---|---|---|
| Exact duplicate rows (all fields except Booking ID) | 35,284 | Kept, because each has its own Booking ID. Sensitivity results are in `outputs/tables/60_duplicate_sensitivity.csv`, and the dashboard can exclude them |
| Zero ADR | 1,959 | Kept for counts and revenue, excluded from ADR averages |
| Negative ADR | 1 | Excluded from ADR averages |
| ADR of 5,400 | 1 | Excluded from ADR averages |
| Zero guests | 180 | Kept |
| Zero nights | 715 | Kept, excluded from average stay |
| Channel Undefined | 5 | Kept as its own category |
| Blank country | 488 | Labelled Unknown |

## Seasonality
Arrivals cover July 2015 to August 2017, so 2016 is the only complete calendar year. Seasonal profiles use 2016 and yearly averages across the years each month appears.

## Cancellation model
A gradient boosting classifier (scikit-learn `HistGradientBoostingClassifier`) and a logistic regression were trained on 75% of bookings and tested on 25%, stratified by outcome, with a fixed random seed. Inputs are hotel, channel, customer type, country (top 20 plus Other), deposit type, lead time, nights, guests, ADR, arrival month and arrival year. Feature importance is the fall in test AUC when a feature's values are shuffled (average of three shuffles). The model shows association, not cause.

## Statistical test
A Kruskal-Wallis test compares lead time across customer types (`08_kruskal_lead_by_customer_type.csv`).

## Limitations
- Two hotels over about 26 months, so seasonal findings rest on one full year.
- No commission, cost or satisfaction data.
- Headline results include duplicate rows. If these are system errors, use the duplicates-removed figures.
- The currency is taken to be naira, as instructed; no conversion was applied.
