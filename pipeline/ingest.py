import requests

r = requests.get("https://data.nasa.gov/docs/legacy/meteorite_landings/gh4g-9sfh.json", timeout=15)

print(r.status_code)
# print(r.text)
print(r.json()[0])