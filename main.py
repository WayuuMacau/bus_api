
"""
Bus ETA Dashboard - Real-time bus arrival information for Hong Kong routes.
Auto-updates every 30 seconds with smooth transitions.
"""

import streamlit as st
import requests
from datetime import datetime, timezone, timedelta
import time

# Constants
UPDATE_INTERVAL = 30  # seconds
HKT = timezone(timedelta(hours=8))
MAX_RESULTS = 5


# API endpoints for each route
ROUTE_API = {
    "297": ["https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/A1C35E976ACF46FD"],
    "33": ["https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/A21BEB6F4E6D43E6"],
    "234D": ["https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/62A1C8EFAC876BDB"],
    "259X": ["https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/0EAFBD8737911A6A"],
    "A25": ["https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/003537/A25"],
    "A26": ["https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001690/A26"],
    "A28": ["https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001690/A28"],
    "A29": ["https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001690/A29"],
    "608": ["https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/003537/608"],
    "22M": ["https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/003537/22M"]
}

# Route pairs, add_time (minutes), and get_off info
ROUTE_PAIRS = [
    ("297", "A25", 12, "土瓜灣落山道"),
    ("33", "A26", 7, "黃大仙轉車站"),
    ("33", "A28", 7, "黃大仙轉車站"),
    ("33", "A29", 7, "黃大仙轉車站"),
    ("234D", "A26", 8, "黃大仙轉車站"),
    ("234D", "A28", 8, "黃大仙轉車站"),
    ("234D", "A29", 8, "黃大仙轉車站"),
    ("259X", "A26", 10, "黃大仙轉車站"),
    ("259X", "A28", 10, "黃大仙轉車站"),
    ("259X", "A29", 10, "黃大仙轉車站"),
    ("608", "A25", 12, "德朗邨, 承啟道"),
    ("22M", "A25", 12, "德朗邨, 承啟道")
]


def get_upcoming_etas(route: str, urls: list, max_results: int = None) -> list:
    """
    Fetch and process upcoming ETAs for a specific route.

    Args:
        route: The route number to fetch ETAs for.
        urls: List of API endpoints for the route.
        max_results: Maximum number of ETAs to return.

    Returns:
        List of tuples (eta_time, remaining_minutes, eta_datetime).
    """
    now = datetime.now(HKT)
    etas = []

    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            for item in data.get("data", []):
                if item.get("route") == route and item.get("eta"):
                    try:
                        eta_dt = datetime.fromisoformat(
                            item["eta"].replace("Z", "+00:00"))
                        eta_dt = eta_dt.astimezone(HKT)
                    except Exception:
                        continue

                    if eta_dt > now:
                        eta_hhmmss = eta_dt.strftime("%H:%M:%S")
                        etr_minutes = int((eta_dt - now).total_seconds() // 60)
                        etas.append((eta_hhmmss, etr_minutes, eta_dt))
        except Exception:
            continue

    etas.sort(key=lambda x: x[2])
    return etas[:max_results] if max_results else etas


def build_route_comparison_table(route_pairs: list, route_api: dict) -> list:
    """
    Build a comparison table for all route pairs showing transfer possibilities.

    Args:
        route_pairs: List of tuples (route1, route2, transfer_time, location).
        route_api: Dictionary of route numbers to API endpoints.

    Returns:
        List of dictionaries containing route comparison data.
    """
    table = []
    for route1, route2, transfer_time, location in route_pairs:
        upcoming1 = get_upcoming_etas(route1, route_api[route1], MAX_RESULTS)
        upcoming2 = get_upcoming_etas(route2, route_api[route2], MAX_RESULTS)

        for eta1_hh, etr1, eta1_dt in upcoming1:
            for eta2_hh, etr2, eta2_dt in upcoming2:
                transfer_etr = etr2 - transfer_time - etr1
                if transfer_etr >= 0:
                    table.append({
                        "Route 1": route1,
                        "ETA to 常悅道": eta1_hh,
                        "ETR for 常悅道": etr1,
                        "Get Off": location,
                        "Route 2": route2,
                        "ETA to 2nd Route": eta2_hh,
                        "ETR for 2nd Route": etr2,
                        "Shortest ETR": transfer_etr,
                        "_eta2_dt": eta2_dt
                    })

    # Sort by earliest ETA for Route 2, then by earliest ETA to 常悅道
    table.sort(key=lambda row: (row.get("_eta2_dt") or datetime.max, row.get("ETA to 常悅道") or ""))
    return [{k: v for k, v in row.items() if k != "_eta2_dt"} for row in table]


def update_data():
    """Update the session state data with new ETAs."""
    new_table = build_route_comparison_table(ROUTE_PAIRS, ROUTE_API)
    st.session_state.data.update({
        'table': new_table,
        'last_update': datetime.now(HKT),
        'start_time': time.time(),
        'counter': st.session_state.data['counter'] + 1
    })


def calculate_countdown():
    """Calculate the countdown until next update."""
    elapsed = time.time() - st.session_state.data['start_time']
    return max(0, UPDATE_INTERVAL - int(elapsed))


def render_timer(countdown: int):
    """Render the countdown timer and update information."""
    st.progress(countdown / UPDATE_INTERVAL)
    st.caption(
        f"Next update in {countdown} seconds "
        f"(Last updated: {st.session_state.data['last_update'].strftime('%H:%M:%S')}) "
        f"[更新次數: {st.session_state.data['counter']}]"
    )


def render_legend():
    """Render the legend explaining ETA and ETR."""
    st.info("ETA: 預計到站時間 Estimated Time of Arrival")
    st.info("ETR: 預計剩餘時間 (分鐘) Estimated Time Remaining (minutes)")
    st.warning(
        "Shortest ETR: 預計最短轉乘時間 (分鐘) 等於0或1, 有機率趕唔到第二程車")


def main():
    """Main application logic."""
    # Initialize session state
    if 'data' not in st.session_state:
        initial_table = build_route_comparison_table(ROUTE_PAIRS, ROUTE_API)
        st.session_state.data = {
            'table': initial_table,
            'last_update': datetime.now(HKT),
            'start_time': time.time(),
            'counter': 0
        }

    # Render header
    st.markdown("# 🕕 常悅道 出發 \n# 🚌 機場/香港口岸")

    # Render timer
    with st.container():
        countdown = calculate_countdown()
        render_timer(countdown)

    # Render legend
    render_legend()

    # Update data if needed
    if countdown == 0:
        update_data()

    # Display table
    with st.container():
        if st.session_state.data['table']:
            st.table(st.session_state.data['table'])
        else:
            st.warning("😞暫無巴士從 九龍灣常悅道 出發到 赤臘角機場 / 香港口岸😞")

    # Auto-refresh
    if countdown >= 0:
        time.sleep(0.1)
        st.rerun()


if __name__ == "__main__":
    main()