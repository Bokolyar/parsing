import requests
import json
from pprint import pprint

user = 'AvokrichA'
url = f'https://api.github.com/users/{user}/repos'

response = requests.get(url)
data = response.json()
with open('les1.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

for el in data:
    print(el.get('name'))



