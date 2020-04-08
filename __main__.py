import os
import jwt
import json
import secrets
import storage
import hashlib
import aiofiles
import exceptions
import authenticator

import aiohttp_cors
from aiohttp import web, streamer
from datetime import datetime, timedelta

# CONSTANTS
SERVER_URL = "https://s1.nexmind.space/"
JWT_ALGORITHM = 'HS256'
JWT_SECRET = "0"#secrets.token_bytes(16)
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
    print(message)

    return web.json_response({'error': message}, status=status)

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
    if "username" not in data or "password" not in data:
        raise exceptions.UserError("username and password fields expected")

    username = data["username"]
    password = data["password"]
    authenticator.login(username, password)
    payload = {
        'name': username,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    return web.json_response({ "token" : token.decode('utf-8') })

async def logout(request):
    if request.username:
        EXPIRED_TOKENS.add(request.headers.get('authorization', None))
        return web.json_response({
            "disconnected" : True
        })
    else:
        raise exceptions.Unauthorized("No token to blacklist")

async def file_sender(file_name=None):
    async with aiofiles.open(file_name, 'rb') as f:
        chunk = await f.read(64*1024)
        while chunk:
            yield chunk
            chunk = await f.read(64*1024)

async def download(request):

    if request.username:
        database_name = hashlib.sha256(request.username.encode('utf-8')).hexdigest()
    else:
        raise exceptions.Unauthorized("A valid token is needed")

    data = await request.post()
    hash = data["hash"]

    headers = {
        "Content-disposition": "attachment; filename={}".format(hash)
    }

    file_path = storage.get_file(hash)
    if not os.path.exists(file_path):
        raise exceptions.NotFound("file <{}> does not exist".format(hash))

    return web.Response(
        body=file_sender(file_path),
        headers=headers
    )

async def upload(request):

    """ EXAMPLE (curl)
    curl -H "Authorization:auth" -F "name=Awesome Background" -F "type=image" -F "desc=A cool image" -F "hash=617Y7DY73y2" -F "chunk=0" 
    -F "spaces=['A','B']" -F "file=@./background.jpg" -X POST localhost:8080/upload
    """

    if request.username:
        database_name = hashlib.sha256(request.username.encode('utf-8')).hexdigest()
    else:
        raise exceptions.Unauthorized("A valid token is needed")

    reader = await request.multipart()


    # infos

    field = await reader.next()
    assert field.name == "name"
    name = (await field.read()).decode("utf-8")

    field = await reader.next()
    assert field.name == "type"
    content_type = (await field.read()).decode("utf-8")

    field = await reader.next()
    assert field.name == "desc"
    description = (await field.read()).decode("utf-8")


    # sha256
    field = await reader.next()
    assert field.name == "hash"
    hash = (await field.read()).decode("utf-8")

    # chunk index
    field = await reader.next()
    assert field.name == "chunk"

    # spaces
    field = await reader.next()
    assert field.name == "spaces"
    spaces = (await field.read()).decode("utf-8").split()

    # file
    field = await reader.next()

    # cannot rely on Content-Length because of chunked transfer
    size = 0
    with open(storage.get_file(hash), 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)

    # save file infos
    with open(storage.get_file("." + hash), 'w') as dotfile:
        json.dump({ "name" : name, "type" : content_type, "desc" : description }, dotfile)

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
                    web.post('/download', download),
                    web.post('/upload', upload)])
    cors = aiohttp_cors.setup(app, defaults={ "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )})
    for route in list(app.router.routes()):
        cors.add(route)
    web.run_app(app, port=8080)

if __name__ == '__main__':
    main()