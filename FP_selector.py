import requests
import csv

r = requests.get("https://www.fpbase.org/api/proteins/?name__icontains=green&default_state__qy__gte=0.7")
print(r.status_code)
print(dir(r))

f = open("placeholder_csv.csv", "w")  # if dne, creates it, otherwise nothing
f.write(r.text)
f.close()

f = open("placeholder_csv.csv", "r")
reader = csv.DictReader(f)
for i in reader:
    print(i["name"])
