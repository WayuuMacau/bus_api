# Bus API Dashboard

Real-time bus arrival information dashboard for Hong Kong routes.

## Features
- Auto-updates every 30 seconds
- Shows ETA (Estimated Time of Arrival) for multiple routes
- Displays countdown timer for next update
- Smooth transitions without page reloads

## Running the Application

### Dynamic Version (Auto-updating)
```bash
uv run streamlit run main.py
```
This version automatically refreshes data every 30 seconds.

### Static Version (Manual update)
```bash
uv run streamlit run main-static.py
```
This version requires manual refresh to update data.

## Requirements
- Python 3.12+
- Streamlit 1.32+
- uv package manager

## Notes
- Data sourced from Hong Kong public transport APIs
- All times shown in HKT (Hong Kong Time)