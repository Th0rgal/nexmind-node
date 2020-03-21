import os
from aiohttp import web
from storage import atto

# CONSTANTS
SERVER_URL = "https://s1.nexmind.space/"

db = atto.Database("yolo")
example_data = ( 2, ["abc", "ghi"] )

print(db.inter("abc"))


print(db.sum("def", "ghi"))