import jwt
import secrets
import storage
import hashlib
import exceptions
import authenticator
from aiohttp import web
from datetime import datetime, timedelta

# CONSTANTS
SERVER_URL = "https://s1.nexmind.space/"
JWT_ALGORITHM = 'HS256'
JWT_SECRET = secrets.token_bytes(16)
JWT_EXP_DELTA_SECONDS = 24*60*20 # 24 hours
EXPIRED_TOKENS = set()

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

    return web.json_response({'error': message})

async def auth_middleware(app, handler):
    async def middleware(request):
        request.username = None
        jwt_token = request.headers.get('authorization', None)
        if jwt_token:
            try:
                if jwt_token in EXPIRED_TOKENS:
                    raise exceptions.UserError("blacklisted token")
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

    """ EXAMPLE (curl)
    curl --data "username=thomas&password=yolo" localhost:8080/login
    """

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

async def logout(request):
    if request.username:
        EXPIRED_TOKENS.add(request.headers.get('authorization', None))
        return web.json_response({
            "disconnected" : True
        })
    else:
        raise exceptions.Unauthorized("no token to blacklist")

async def request(request):
    pass

async def upload(request):

    """ EXAMPLE (curl)
    curl -H "Authorization:auth" -F "hash=617Y7DY73y2" -F "chunk=0" 
    -F "spaces=['A','B']" -F "file=@./background.jpg" -X POST localhost:8080/upload
    """

    if request.username:
        database_name = hashlib.sha256(request.username.encode('utf-8')).hexdigest()
    else:
        raise exceptions.Unauthorized("a valid token is needed")

    reader = await request.multipart()

    # sha256
    field = await reader.next()
    assert field.name == "hash"
    hash = (await field.read()).decode("utf-8")

    # chunk index
    field = await reader.next()
    assert field.name == "chunk"
    chunk = int(await field.read())

    # spaces
    field = await reader.next()
    assert field.name == "spaces"
    spaces = (await field.read()).decode("utf-8").split()

    # file
    field = await reader.next()

    # cannot rely on Content-Length because of chunked transfer
    size = 0
    with open(storage.get_files_folder(hash), 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)

    storage.atto.Database(database_name).add_data( (hash, spaces) )
    return web.json_response({
        "stored" : True,
        "size" : size
    })

def main():
    authenticator.load()
    app = web.Application(middlewares = [error_middleware, auth_middleware], client_max_size = 10*2**30) # 10GiB
    app.add_routes([web.get('/debug', debug),
                    web.post('/login', login),
                    web.post('/logout', logout),
                    web.post('/request', request),
                    web.post('/upload', upload)])
    web.run_app(app, port=8080)

if __name__ == '__main__':
    main()