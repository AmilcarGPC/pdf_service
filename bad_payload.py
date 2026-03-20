import json
import urllib.error
import urllib.request

with open("payload.json", "r", encoding="utf-8") as f:
    bad_data = json.load(f)

# Intentionally exceed max_length for nombre_cliente
bad_data["nombre_cliente"] = "a" * 200

url = "http://localhost:8080/generate"
api_key = "604ba969e68d7cb1b5942b3f976b656ab06926b6de620e01b80546ff22dabd92"

req = urllib.request.Request(url, data=json.dumps(bad_data).encode("utf-8"))
req.add_header("Content-Type", "application/json")
req.add_header("X-API-Key", api_key)

try:
    with urllib.request.urlopen(req) as response:
        pass
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print(e.read().decode("utf-8"))
