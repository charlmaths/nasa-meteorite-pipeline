import requests
import json

# request variable using .get() method - also adding "?$limit=1000" to limit the number of records to 1000 for testing purposes
var_url = "https://data.nasa.gov/docs/legacy/meteorite_landings/gh4g-9sfh.json?$limit=1000"

# defining file path:
file_path = "data/nasa-json-api/meteor_data.json"

def api_ingestor(url):
    try:
        r = requests.get(url,timeout=40)
        # stat_code = r.status_code
        # print(f"status code success: {stat_code}")
    except requests.exceptions.ConnectTimeout:
        print("Timed out")
        # print(f"status code error: {stat_code}")
        return None
    stat_code = r.status_code
    if stat_code != 200:
        print(f"status code error: {stat_code}")
    else:
        print(f"status code: {stat_code}")
    #     # print(type(r.text))
    #     # print(r.json())
    return json.dumps(r.json())


with open(file_path, "w") as file:
    data = api_ingestor(var_url)
    if data is None:
        print("Ingestion failed, exiting...")
    else:
        records = json.loads(data) # converting the returned string into a python list
        file.write(data)
        print(f"'{file_path}' has been created")
        print(f"number of records: {len(records)}")


