from flask import Flask, request, Response, jsonify, send_from_directory, send_file
from flask_cors import CORS
from datetime import datetime, timezone
import os
import requests
 
app = Flask(__name__)
ip_addr = "0.0.0.0"
port = 5000
 
def single_bus_stop_data(bus_stop_code : int) -> dict :
 
    api_url = 'https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival'
    headers = {
        # API can be requested from https://datamall.lta.gov.sg/content/datamall/en/request-for-api.html
        'AccountKey': os.getenv("API_KEY"),
        'accept': 'application/json'
    }
    params = {
        'BusStopCode': bus_stop_code
    }
 
    response = requests.get(api_url, headers=headers, params=params)
 
    if response.status_code != 200:
        print(f"error fetching data for bus stop code {bus_stop_code}")
        return []
 
    now = datetime.now(timezone.utc)
    data = response.json()
    services = data['Services']
    out = []
 
    for service in services:
        service_info = {}
        service_info["ServiceNo"] = service["ServiceNo"]
 
        service_info["Timings"] = []
        for bus_info in ["NextBus", "NextBus2", "NextBus3"]:
            if not bus_info in service:
                service_info["Timings"].append("-")
                continue
            next_bus_time = service[bus_info]["EstimatedArrival"]
            if not next_bus_time:
                service_info["Timings"].append("-")
                continue
            next_bus_time = next_bus_time[:-6] + '+08:00'
            arrival_time = datetime.fromisoformat(next_bus_time)
            seconds_until_arrival = int((arrival_time - now).total_seconds())
            service_info["Timings"].append(seconds_until_arrival)
        out.append(service_info)
 
    return out
 
@app.route('/v2/singlebusdata/<bus_stop_id>', methods=['GET'])
def singlebusdata_v2(bus_stop_id):
    return jsonify(single_bus_stop_data(bus_stop_id))
 
@app.route('/bus', methods=['GET'])
def send_index():
    server_ip = request.host.split(':')[0]
    print(server_ip)
    print(request.environ['SERVER_NAME'])
    file_path = os.path.join(os.getcwd(), 'index.html')
 
    with open(file_path, 'r') as file:
        content = file.read()
 
    return Response(content, content_type='text/html')

if __name__ == '__main__':
    app.run(host=ip_addr, port=port, debug=True)
 
 
"""
Sample response from LTA endpoint
 
{
    "odata.metadata": "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival",
    "BusStopCode": "18279",
    "Services": [
        {
            "ServiceNo": "92",
            "Operator": "SBST",
            "NextBus": {
                "OriginCode": "11009",
                "DestinationCode": "11009",
                "EstimatedArrival": "2024-08-26T13:35:32+08:00",
                "Monitored": 1,
                "Latitude": "1.288382",
                "Longitude": "103.789906",
                "VisitNumber": "1",
                "Load": "SEA",
                "Feature": "WAB",
                "Type": "SD"
            },
            "NextBus2": {
                "OriginCode": "11009",
                "DestinationCode": "11009",
                "EstimatedArrival": "2024-08-26T13:47:50+08:00",
                "Monitored": 1,
                "Latitude": "1.3080753333333333",
                "Longitude": "103.79075733333333",
                "VisitNumber": "1",
                "Load": "SEA",
                "Feature": "WAB",
                "Type": "SD"
            },
            "NextBus3": {
                "OriginCode": "11009",
                "DestinationCode": "11009",
                "EstimatedArrival": "2024-08-26T13:55:38+08:00",
                "Monitored": 0,
                "Latitude": "0.0",
                "Longitude": "0.0",
                "VisitNumber": "1",
                "Load": "SEA",
                "Feature": "WAB",
                "Type": "SD"
            }
        }
    ]
}
"""