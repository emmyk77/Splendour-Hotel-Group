# SHG Booking Data Analysis: Findings and Recommendations

All amounts are in Nigerian naira (₦); M means millions. Figures include all 119,390 rows unless stated. Supporting tables are in `outputs/tables/`, and definitions are in `documentation/methodology.md`.

## 1. Summary

Revenue collected is ₦29.60M and ₦13.12M was lost to cancellations, so 69.3% of potential revenue (₦42.72M) was realised. The cancellation rate is 37.0%. Online travel agents (OTAs) supply 62.0% of bookings, 58.3% of revenue and 82.2% of lost revenue. Revenue for January to August 2017 was 21.7% above the same period of 2016, while the cancellation rate rose from 34.7% to 38.7%.

**Data caveat.** 35,284 rows are exact copies of another row except for Booking ID. Without them the cancellation rate is 28.2%, revenue ₦22.51M and lost revenue ₦11.15M. The ranking of channels does not change. Confirm with the data owner which baseline is correct.

## 2. Booking patterns

- 2016 is the only complete year. Bookings peak in spring (April to June) and autumn (September and October, with October the busiest month at 6,203 arrivals). January is the weakest month (2,248).
- Revenue peaks in July and August because ADR peaks then (₦128.5 in July, ₦141.8 in August, against ₦71.9 in January).
- Mean lead time is 104 days. By channel: Corporate 44.9, Direct 57.8, OTA 108.3, Offline agents 135.6. By customer type: Group 55.1, Transient 93.3, Transient-Party 137.0, Contract 143.0. The difference by customer type is significant (Kruskal-Wallis, p below 0.001).

## 3. Customer behaviour and channels

| Channel | Bookings | Share | ADR (₦) | Cancel rate | Revenue (₦M) |
|---|---|---|---|---|---|
| Online Travel Agent | 74,072 | 62.0% | 109.50 | 43.2% | 17.26 |
| Offline Travel Agent | 23,991 | 20.1% | 88.14 | 34.2% | 6.99 |
| Direct | 14,645 | 12.3% | 112.88 | 17.5% | 4.43 |
| Corporate | 6,677 | 5.6% | 71.38 | 22.1% | 0.92 |

Five countries supply 72.9% of bookings: Portugal (40.7%), the UK (10.2%), France (8.7%), Spain (7.2%) and Germany (6.1%). International guests are 59.3% of bookings but 69.5% of revenue, because they cancel less (23.6% against 56.6% for Portugal) and stay longer (3.7 nights against 2.6).

## 4. Cancellations

- Strongest correlations with cancellation: non-refundable deposit (0.48), lead time (0.29), OTA channel (0.16), City hotel (0.14), and international guest (-0.34).
- A gradient boosting model reaches AUC 0.908 (accuracy 82.5%, precision 81.4%, recall 68.4%). On de-duplicated data the AUC is 0.835. Most important drivers: country, deposit type, lead time, channel, customer type.
- Lost revenue by channel: OTA ₦10.78M (82.2%), Offline agents ₦1.11M (8.5%), Direct ₦1.03M (7.9%), Corporate ₦0.20M (1.5%). Transient guests account for 87.7% of the loss.
- Revenue realisation: OTA 61.5%, Direct 81.1%, Corporate 82.4%, Offline agents 86.3%.

## 5. Revenue and pricing

- Revenue was ₦13.30M in 2016, the only full year, and ₦10.98M in the eight months of 2017. The peak month was August 2017 (₦1.99M).
- Transient guests pay the most (ADR ₦108.7 against about ₦88 for other types) and cancel the most.
- The Resort is strongly seasonal (ADR ₦50.9 in January, ₦188.5 in August). The City hotel is steadier (₦84 to ₦123).
- Corporate Resort bookings average ₦54.7 against ₦87.5 at the City hotel.

## 6. Geography

Large markets that cancel least: Germany (16.7%), France (18.6%), UK (20.2%). Brazil, Italy and China cancel well above the international average of 23.6%. Ireland (5.3 nights) and the UK (5.0) stay longest. The United States (₦123.7) and Switzerland (₦122.3) pay the highest rates among markets with at least 500 bookings.

## 7. Operations

- Average completed stay is 3.42 nights (Resort 4.20, City 2.94). Contract customers stay 6.2 nights, corporate guests 2.4.
- Average check-outs per day are 93. Sunday is busiest (120.2) and Tuesday quietest (78.0). May and October average about 113 to 116 per day, December 62.5. The peak day was 8 December 2015 with 243 check-outs.

## 8. Deposit types

| Deposit type | Bookings | Cancel rate | Revenue lost (₦M) |
|---|---|---|---|
| No Deposit | 104,641 | 28.4% | 13.10 |
| Non Refundable | 14,587 | 99.4% | 0 |
| Refundable | 162 | 22.2% | 0.02 |

Non-refundable bookings are almost always cancelled, but their value is retained (₦3.62M), so they cause no loss. 97.2% are Portuguese and the pattern is concentrated in duplicate rows, so it should be treated as a data question rather than a behavioural finding.

## 9. Corporate bookings

Corporate is 5.6% of bookings and 3.1% of revenue. ADR is ₦71.4 against ₦103.5 overall. Median lead time is 9 days, the cancellation rate is 22.1%, and 79% of arrivals fall Monday to Thursday (57% for all bookings). Corporate demand fills midweek and off-peak periods, so the opportunity lies in rate rather than volume.

## 10. Lead time

| Lead time (days) | Cancel rate | Revenue per booking (₦) | Revenue realisation |
|---|---|---|---|
| 0 to 7 | 9.6% | 167.5 | 88.4% |
| 8 to 30 | 27.9% | 234.9 | 69.8% |
| 31 to 90 | 37.7% | 258.0 | 67.3% |
| 91 to 180 | 44.7% | 302.1 | 67.1% |
| 181 to 365 | 55.5% | 262.5 | 64.9% |
| 366 or more | 67.7% | 181.7 | 88.8% |

Value per booking is highest at 91 to 180 days, but risk climbs with lead time. Satisfaction is not recorded, so no link to satisfaction can be shown.

## 11. Online and offline agents

OTAs bring ₦17.26M (58.3% of revenue) at a 43.2% cancellation rate (35.7% excluding non-refundable). Offline agents bring ₦6.99M (23.6%) at 34.2% (16.9% excluding non-refundable). For every ₦100 of stay value booked, ₦86 is realised through offline agents and ₦61 through OTAs. Commission costs are not in the data and would narrow the OTA advantage further.

## 12. Recommendations

1. Cut OTA cancellation losses, the largest lever (₦10.78M): stricter cancellation windows, partial prepayment or a discounted non-refundable rate.
2. Shift mix towards direct bookings, which have the highest ADR and revenue per booking and low cancellation.
3. Use the cancellation model to flag risky bookings (long lead time, OTA, high-risk country), confirm them 30 to 60 days out, and resell likely cancellations.
4. Price the Resort seasonally: protect July and August, raise shoulder-season floors, and review corporate Resort rates.
5. Market to the UK, Germany, France and Ireland; add the United States and Switzerland for rate; require guarantees for Brazil, Italy and China.
6. Limit free cancellation on bookings made more than 180 days ahead.
7. Roster for Sunday check-outs and the May and October peaks; lighter cover on Tuesdays and in December and January.
8. Build midweek corporate packages for the City hotel and Resort off-season, with rates reviewed against overall ADR.
9. Resolve data questions with the source owner: duplicate rows, non-refundable cancellations, and missing satisfaction and commission data.
