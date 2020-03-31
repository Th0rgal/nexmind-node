import os
import exceptions
import authenticator
from aiohttp import web
from storage import atto

# CONSTANTS
SERVER_URL = "https://s1.nexmind.space/"

@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        if response.status < 400: # if no error coccured
            return response
        message = response.message
        status = responses.status

    except exceptions.UserError as exception:
        message = exception.args[0]
        status = exception.code

    except web.HTTPException as exception:
        message = exception.reason
        status = 500

    except Exception as exception:
        message = exception.args[0]
        status = 500

    return web.json_response({'error': message})

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
    app = web.Application(middlewares = [error_middleware], client_max_size = 10*2**30) # 10GiB
    app.add_routes([web.get('/debug', debug),
                    web.post('/login', login),
                    web.post('/request', request),
                    web.post('/upload', upload)])
    web.run_app(app, port=8080)

if __name__ == '__main__':
    main()