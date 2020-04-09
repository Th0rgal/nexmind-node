import jwt
import aiofiles
import exceptions
import aiohttp_cors

from aiohttp import web
from . import queries

def load():
    app = web.Application(middlewares = [error_middleware, auth_middleware], client_max_size = 10*2**30) # 10GiB
    app.add_routes([web.get('/debug', queries.debug),
                    web.post('/login', queries.login),
                    web.post('/logout', queries.logout),
                    web.post('/search', queries.search),
                    web.post('/download', queries.download),
                    web.post('/upload', queries.upload)])
    cors = aiohttp_cors.setup(app, defaults={ "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )})
    for route in list(app.router.routes()):
        cors.add(route)
    web.run_app(app, port=8080)


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
    print(message)

    return web.json_response({'error': message}, status=status)

async def auth_middleware(app, handler):
    async def middleware(request):
        request.username = None
        jwt_token = request.headers.get('authorization', None)
        if jwt_token:
            try:
                if jwt_token in queries.EXPIRED_TOKENS:
                    raise exceptions.UserError("blacklisted token")
                payload = jwt.decode(jwt_token, queries.JWT_SECRET,
                                     algorithms=[queries.JWT_ALGORITHM])
                request.username = payload['name']
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                pass

        return await handler(request)
    return middleware

async def file_sender(file_name=None):
    async with aiofiles.open(file_name, 'rb') as f:
        chunk = await f.read(64*1024)
        while chunk:
            yield chunk
            chunk = await f.read(64*1024)