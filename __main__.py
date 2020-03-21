import os
from aiohttp import web
from storage import atto

# CONSTANTS
SERVER_URL = "https://s1.nexmind.space/"

db = atto.Database("yolo")
example_data = ( 18773893988, set(["abc", "def", "ghi"]) )
db.add_data(example_data)

print(db.inter("abc"))
print(db.sum("def"))