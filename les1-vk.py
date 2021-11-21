import requests
import json
from pprint import pprint


token = '***'
url = f'https://api.vk.com/method/groups.get?v=5.81&access_token={token}'

response = requests.get(url)
data = response.json()

with open('les1-vk.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

