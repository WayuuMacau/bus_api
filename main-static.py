
import streamlit as st
import requests
from datetime import datetime, timezone, timedelta


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



def get_upcoming_etas(route, urls, max_results=None):
    """Return a list of upcoming ETAs for a route.

    Each entry is a tuple: (eta_hhmmss, etr_minutes, eta_datetime).
    Results are sorted by datetime ascending. If max_results is provided,
    only that many soonest ETAs are returned.
    """
    hkt = timezone(timedelta(hours=8))
    now = datetime.now(hkt)
    etas = []

    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            for item in data.get("data", []):
                if item.get("route") == route and item.get("eta"):
                    try:
                        eta_dt = datetime.fromisoformat(item["eta"].replace("Z", "+00:00"))
                        eta_dt = eta_dt.astimezone(hkt)
                    except Exception:
                        continue
                    if eta_dt > now:
                        eta_hhmmss = eta_dt.strftime("%H:%M:%S")
                        etr_minutes = int((eta_dt - now).total_seconds() // 60)
                        etas.append((eta_hhmmss, etr_minutes, eta_dt))
        except Exception:
            continue

    etas.sort(key=lambda x: x[2])
    if max_results is not None:
        etas = etas[:max_results]
    return etas



st.markdown("# 🕕 九龍灣常悅道 出發 \n# 🚌 赤臘角機場 / 香港口岸")
st.info("ETA: 預計到站時間 Estimated Time of Arrival")
st.info("ETR: 預計剩餘時間 (分鐘) Estimated Time Remaining (minutes)")
st.warning("Shortest ETR: 預計最短轉乘時間 (分鐘) 等於0或1, 有機率趕唔到第二程車")


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



def build_table(route_pairs, route_api):
    """Build the comparison table for all route pairs."""
    table = []
    for route1, route2, add_time, get_off in route_pairs:
        upcoming1 = get_upcoming_etas(route1, route_api[route1], max_results=5)
        upcoming2 = get_upcoming_etas(route2, route_api[route2], max_results=5)

        # create a row for every combination of upcoming ETAs between the two routes
        for eta1_hh, etr1, eta1_dt in upcoming1:
            for eta2_hh, etr2, eta2_dt in upcoming2:
                shortest_etr = etr2 - add_time - etr1
                if shortest_etr >= 0:
                    table.append({
                        "Route 1": route1,
                        "ETA to 常悅道": eta1_hh,
                        "ETR for 常悅道": etr1,
                        "Get Off": get_off,
                        "Route 2": route2,
                        "ETA to 2nd Route": eta2_hh,
                        "ETR for 2nd Route": etr2,
                        "Shortest ETR": shortest_etr,
                        "_eta2_dt": eta2_dt
                    })
    # Sort by the earliest ETA datetime for Route 2
    sorted_table = sorted(table, key=lambda row: row.get("_eta2_dt") or datetime.max)

    # Remove internal sort key before returning so it won't be displayed
    display_table = []
    for row in sorted_table:
        row_copy = {k: v for k, v in row.items() if k != "_eta2_dt"}
        display_table.append(row_copy)

    return display_table


table = build_table(ROUTE_PAIRS, ROUTE_API)
if table:
    st.table(table)
else:
    st.warning("😞暫無巴士從 九龍灣常悅道 出發到 赤臘角機場 / 香港口岸😞")