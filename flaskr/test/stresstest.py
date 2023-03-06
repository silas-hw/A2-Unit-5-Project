import requests
import time

URL = 'http://127.0.0.1:5000'
count = 0

while True:
    requests.get(URL)
    count += 1
    print(count)
