import requests

# request variable using .get() method
var_url = "https://data.nasa.gov/docs/legacy/meteorite_landings/gh4g-9sfh.json$limit=1000"


def api_ingestor(url):
    r = requests.get(url,timeout=5)
    stat_code = r.status_code
    if stat_code != 200:
        print(f"status code error: {stat_code}")
    else:
        print(f"status code: {stat_code}")


api_ingestor(var_url)
# print(r.status_code)
# print(r.text)
# print(r.json()[0])