import jwt
import secrets
import exceptions
import authenticator
from aiohttp import web
from storage import atto
from datetime import datetime, timedelta

# CONSTANTS
SERVER_URL = "https://s1.nexmind.space/"
JWT_ALGORITHM = 'HS256'
JWT_SECRET = secrets.token_bytes(16)
JWT_EXP_DELTA_SECONDS = 24*60*20 # 24 hours

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

async def auth_middleware(app, handler):
    async def middleware(request):
        request.username = None
        jwt_token = request.headers.get('authorization', None)
        print(jwt_token)
        if jwt_token:
            try:
                payload = jwt.decode(jwt_token, JWT_SECRET,
                                     algorithms=[JWT_ALGORITHM])
                request.username = payload['name']
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                pass

        return await handler(request)
    return middleware

async def debug(request):
    if request.username:
        return web.Response(body=("Connected and logged " + request.username))
    return web.Response(body="Connected, not logged")

async def login(request):
    data = await request.post()
    username = data["username"]
    password = data["password"]

    authenticator.login(username, password)
    payload = {
        'name': username,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    return web.json_response({
        "token" : token.decode('utf-8')
    })

async def request(request):
    pass

async def upload(request):
    pass

def main():
    authenticator.load()
    app = web.Application(middlewares = [error_middleware, auth_middleware], client_max_size = 10*2**30) # 10GiB
    app.add_routes([web.get('/debug', debug),
                    web.post('/login', login),
                    web.post('/request', request),
                    web.post('/upload', upload)])
    web.run_app(app, port=8080)

if __name__ == '__main__':
    main()