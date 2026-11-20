# Data dictionary

## Raw file (`data/raw/SHG_Booking_Data.md`)

| Field | Description |
|---|---|
| Booking ID | Unique identifier for each booking |
| Hotel | City or Resort hotel within Splendor Hotel Groups |
| Booking Date | Date the booking was made (spreadsheet serial number in the raw file) |
| Arrival Date | Scheduled arrival date (serial number) |
| Lead Time | Days between booking date and arrival date |
| Nights | Nights booked |
| Guests | Number of guests |
| Distribution Channel | Online Travel Agent, Offline Travel Agent, Direct, Corporate, or Undefined |
| Customer Type | Transient, Transient-Party, Contract, or Group |
| Country | Country of origin of the guests |
| Deposit Type | No Deposit, Non Refundable, or Refundable |
| Avg Daily Rate | Average daily rate for the booking (₦) |
| Status | Check-Out, Canceled, or No-Show |
| Status Update | Date of the last status change. For completed stays this is the check-out date |
| Cancelled (0/1) | 1 if cancelled (includes no-shows), otherwise 0 |
| Revenue | Revenue retained from the booking (₦). Equals ADR times nights for completed stays, and the retained amount for cancelled bookings |
| Revenue Loss | Negative value equal to the stay value that was not retained on cancelled bookings, zero otherwise (₦) |

## Cleaned file (`data/processed/shg_clean.csv`)

The 17 raw fields renamed to snake_case (`booking_id`, `hotel`, `booking_date`, `arrival_date`, `lead_time`, `nights`, `guests`, `distribution_channel`, `customer_type`, `country`, `deposit_type`, `adr`, `status`, `status_update`, `canceled`, `revenue`, `revenue_loss`), with dates converted to calendar dates and blank countries set to `Unknown`. Derived fields:

| Field | Description |
|---|---|
| arrival_year, arrival_month, arrival_ym | Parts of the arrival date |
| lead_bin | Lead time band: 0-7, 8-30, 31-90, 91-180, 181-365, 366+ days |
| loss_abs | Lost revenue as a positive number (`-revenue_loss`) |
| potential_revenue | `revenue + loss_abs` |
| adr_valid | 1 if ADR is above zero and below 5,000 (used for ADR averages) |
| stay_completed | 1 if not cancelled and nights is at least 1 (used for average stay) |
| is_duplicate | 1 if the row matches an earlier row on every field except booking_id |
