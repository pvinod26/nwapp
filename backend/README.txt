CABLEDESK MAIN APP - VERSION 4

This is a Flask + SQLite starter application for a single administrator.

RUN LOCALLY (Windows):
1. Install Python 3.10 or newer.
2. Extract this ZIP.
3. Open Command Prompt in the extracted folder.
4. Run: py -m venv venv
5. Run: venv\Scripts\activate
6. Run: pip install -r requirements.txt
7. Run: python app.py
8. Open http://127.0.0.1:5000

DEMO LOGIN:
Username: admin
Password: ChangeMe123!
Change the password from Admin settings after logging in.

INCLUDED:
- Single admin login
- Companies: SSC, ZEE, SDV / Spandana, AP Fiber, GTPL, JKC
- Initial demo records for SSC, ZEE, SDV / Spandana and AP Fiber
- GTPL and JKC are available as providers but have no imported records yet
- Search and sorting
- Last 4 months of payment status, directly editable
- Demo assumption: previous 3 months Paid, latest month Pending
- Separate Recharge status on each customer row
- Clicking Not recharged asks for confirmation, marks Recharged and extends pack expiry by 30 days
- Clicking Rollback recharge restores the exact pack expiry saved immediately before that recharge
- Pack expiry labels show Expired N days ago, Expires today, Expires tomorrow, or Expires in N days
- Expiry dashboard buttons: expires today, expired and not recharged, expires tomorrow, expires within 7 days
- Expiry quick lists can be combined with provider tabs
- If expiry is already in the future, 30 days are added to that expiry; if expired/blank, 30 days are added from today
- Existing database rows that were recharged using an older app version do not contain the old expiry date. The app will refuse to roll those old recharges back rather than erase or guess the expiry. Recharges performed in this version can be fully rolled back.
- Add, edit, archive customer
- Pack expiry reminders and 3+ consecutive unpaid-month reminders
- CSV export
- Responsive desktop and mobile layouts

IMPORTANT DATA NOTE:
Customer names, IDs and a few phone numbers were transcribed from handwritten photos. They are demo seed data and must be checked against the original records before real use. Missing phone numbers are intentionally blank rather than invented. Pack expiry dates and monthly amounts are not guessed; enter them from the client's records.

DEPLOYMENT:
The included render.yaml is a starter Render blueprint. For a live production system, configure a persistent disk and set a strong ADMIN_PASSWORD and SECRET_KEY. SQLite is acceptable for this small single-admin starter; for larger/multi-user use, migrate to managed PostgreSQL.


VERSION 5 UPDATE
- Added a Call button for each customer beside the phone number in the desktop register.
- Added a Call button on each mobile customer card.
- The button uses the phone's standard tel: link. On a mobile device it opens the dialler with the customer's number filled in; the user confirms the call.
- Existing SMS and WhatsApp reminder placeholders remain unchanged. They still open the device's messaging app / WhatsApp manually.

\nVERSION 6 CALL BUTTON VISIBILITY FIX
- Call is now also shown in the desktop Actions column, as well as beside the phone number.
- Mobile customer cards show a prominent Call button beside Edit.
- If a customer has no phone number, the Call button remains visible but disabled; add the phone number to enable calling.
- Clicking an enabled Call button opens the device dialler using the saved customer number. The user confirms the call.

\nVERSION 7 PHONE VALIDATION FIX
- Fixed an escaped-regex bug that incorrectly displayed "Invalid..." beside valid phone numbers.
- Valid 10-digit Indian mobile numbers now enable the Call link.
- The Call link opens the device dialler with the saved number. No automatic call is placed.

\nVERSION 8 ACTIONS BAR CLEANUP
- Desktop Actions column now contains only Edit and Delete. The Call button remains beside the phone number, avoiding duplicate Call controls and clipped ellipsis in the Actions column.
- Mobile customer cards now show Call, Edit and Delete together in a clear action row.
- Adjusted action column sizing and overflow so action controls are fully visible without trailing ellipses.

\nVERSION 9 CALL BUTTON + INDIA COUNTRY CODE
- Retains the Call button beside each customer's phone number.
- Customer phone numbers are displayed with India's +91 country code.
- Calling links use +91 for 10-digit numbers; numbers already stored with +91 or 91 are not double-prefixed.
- A stored number beginning with 0 has that trunk prefix removed and is normalized to +91.
- Stored database values are not changed; formatting is applied when displayed and when opening the dialler.

\nVERSION 10 CALL BUTTON VISIBILITY CORRECTION
- The Call button is now explicitly placed in the desktop Actions column alongside Edit and Delete.
- The Actions column has been widened so Call, Edit and Delete remain visible and are not clipped.
- The phone column continues to show the normalized +91 number.
- Mobile cards retain the Call button in their action row.
- Clicking Call opens the device dialler with the normalized customer number; it does not place a call automatically.
