import requests
import csv

"""
FPBase API documentation: https://www.fpbase.org/api/
Requests Module documentation: https://requests.readthedocs.io/en/
"""

url = "https://www.fpbase.org/api/proteins/"

payload = {}   # "field__lookup":"value"

field = "name"
lookup = "icontains"
value = "green"
payload[field + "__" + lookup] = value

r = requests.get(url, params=payload)
print("\nStatus:", r.status_code)
print("Lookup url:", r.url, "\n")

csv_file = open("csv_buffer.csv", "w")
csv_file.write(r.text)
csv_file.close()

csv_file = open("csv_buffer.csv", "r")
reader = csv.DictReader(csv_file)
for row in reader:
    for key in row.keys():
        print(key)

csv_file.close()
