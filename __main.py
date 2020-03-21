import os
from aiohttp import web
from storage import atto

def get_path(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)

# CONSTANTS
SERVER_URL = "https://s1.nexmind.space/"