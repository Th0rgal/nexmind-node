import os
from aiohttp import web
from storage import atto

# CONSTANTS
SERVER_URL = "https://s1.nexmind.space/"

async def login(request):
    print(request)
    pass

async def request(request):
    pass

async def upload(request):
    pass

def main():
    app = web.Application(client_max_size = 10*2**30) # 10GiB
    app.add_routes([web.post('/login', login),
                    web.get('/request', request),
                    web.get('/upload', upload)])
    web.run_app(app, port=8080)

if __name__ == '__main__':
    main()