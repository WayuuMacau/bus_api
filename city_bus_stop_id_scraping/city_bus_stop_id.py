import requests
import csv

# Define the range of stop IDs
start_id = 1001
end_id = 3980

# Prepare the CSV file
with open('citybus_stops.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['stop', 'name_tc', 'name_en'])

    for stop_num in range(start_id, end_id + 1):
        stop_id = f"{stop_num:06d}"
        url = f"https://rt.data.gov.hk/v2/transport/citybus/stop/{stop_id}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get('data', {})
            stop = data.get('stop')
            name_tc = data.get('name_tc')
            name_en = data.get('name_en')
            if stop and name_tc and name_en:
                writer.writerow([stop, name_tc, name_en])