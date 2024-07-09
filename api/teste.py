import json
from api.config.paths import *


with open(OFICIAIS_MEMBROS_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(data)