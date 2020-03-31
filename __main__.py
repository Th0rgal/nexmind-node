import os
import authenticator
from aiohttp import web
from storage import atto

# CONSTANTS
SERVER_URL = "https://s1.nexmind.space/"

async def debug(request):
    return web.Response(body="It seems to be working")

async def login(request):
    data = await request.post()
    username = data["username"]
    password = data["password"]

    connected = False
    if authenticator.login(username, password) == None:
        connected = True
        token = ""

    return web.json_response({
        "connected" : connected
    })

async def request(request):
    pass

async def upload(request):
    pass

def main():
    authenticator.load()
    app = web.Application(client_max_size = 10*2**30) # 10GiB
    app.add_routes([web.get('/debug', debug),
                    web.post('/login', login),
                    web.post('/request', request),
                    web.post('/upload', upload)])
    web.run_app(app, port=8080)

if __name__ == '__main__':
    main()