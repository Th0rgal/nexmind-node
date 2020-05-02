import os
import jwt
import json
import urllib
import hashlib
import storage
import aiofiles
import exceptions

from pathlib import Path
from aiohttp import web, MultipartWriter
from datetime import datetime, timedelta


class Queries:
    def __init__(self, auth_database):
        self.auth_database = auth_database

        # todo: read from config
        self.JWT_ALGORITHM = "HS256"
        self.JWT_SECRET = "0"  # secrets.token_bytes(16)
        self.JWT_EXP_DELTA_SECONDS = 24 * 60 * 20  # 24 hours
        self.EXPIRED_TOKENS = set()

    async def debug(self, request):
        if request.username:
            return web.Response(body=("Connected and logged " + request.username))
        return web.Response(body="Connected, not logged")

    async def login(self, request):

        """ EXAMPLE (curl)
        curl --data "username=thomas&password=yolo" localhost:8080/login
        """
        data = await request.post()
        if "username" not in data or "password" not in data:
            raise exceptions.UserError("username and password fields expected")

        username = data["username"]
        password = data["password"]
        self.auth_database.login(username, password)
        payload = {
            "name": username,
            "exp": datetime.utcnow() + timedelta(seconds=self.JWT_EXP_DELTA_SECONDS),
        }
        token = jwt.encode(payload, self.JWT_SECRET, self.JWT_ALGORITHM)
        return web.json_response({"token": token.decode("utf-8")})

    async def logout(self, request):
        if request.username:
            self.EXPIRED_TOKENS.add(request.headers.get("authorization", None))
            return web.json_response({"disconnected": True})
        else:
            raise exceptions.Unauthorized("No token to blacklist")

    async def search(self, request):

        if request.username:
            database_name = hashlib.sha256(request.username.encode("utf-8")).hexdigest()
        else:
            raise exceptions.Unauthorized("A valid token is needed")

        data = await request.post()
        if "spaces" not in data:
            raise exceptions.UserError("you must specify spaces")

        results = storage.atto.Database(database_name).inter(data["spaces"].split())

        output = {}
        for result in results:
            with open(storage.get_file("." + result[0])) as json_file:
                dotfile_content = json.load(json_file)[database_name]
                dotfile_content["spaces"] = list(result[1])
                output[result[0]] = dotfile_content

        return web.json_response({"results": output})

    async def download(self, request):

        if request.username:
            database_name = hashlib.sha256(request.username.encode("utf-8")).hexdigest()
        else:
            raise exceptions.Unauthorized("A valid token is needed")

        data = await request.post()
        hash = data["hash"]

        file_path = storage.get_file(hash)
        dotfile_path = storage.get_file("." + hash)
        if not os.path.exists(file_path) or not os.path.exists(dotfile_path):
            raise exceptions.NotFound("file <{}> does not exist".format(hash))
        with open(dotfile_path) as dotfile:
            dotfile_content = json.load(dotfile)[database_name]
            name = dotfile_content["name"]

        response = web.StreamResponse()
        response.headers["Content-Type"] = "application/octet-stream"
        response.headers[
            "Content-Disposition"
        ] = "attachment; filename*=UTF-8''{}".format(
            urllib.parse.quote(name, safe="")  # replace with the filename
        )
        response.enable_chunked_encoding()
        await response.prepare(request)

        with open(file_path, "rb") as fd:  # replace with the path
            for chunk in iter(lambda: fd.read(1024), b""):
                await response.write(chunk)
        await response.write_eof()

        return response

    async def upload(self, request):

        """ EXAMPLE (curl)
        curl -H "Authorization:auth" -F "name=Awesome Background" -F "type=image" -F "desc=A cool image" -F "hash=617Y7DY73y2" -F "chunk=0" 
        -F "spaces=['A','B']" -F "file=@./background.jpg" -X POST localhost:8080/upload
        """

        if request.username:
            database_name = hashlib.sha256(request.username.encode("utf-8")).hexdigest()
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

        # create files folder if not created
        Path(storage.get_folder()).mkdir(parents=True, exist_ok=True)

        # cannot rely on Content-Length because of chunked transfer
        size = 0
        with open(storage.get_file(hash), "wb") as f:
            while True:
                chunk = await field.read_chunk()  # 8192 bytes by default.
                if not chunk:
                    break
                size += len(chunk)
                f.write(chunk)

        # save file infos
        dotfile_path = storage.get_file("." + hash)
        if os.path.exists(dotfile_path):
            with open(dotfile_path, "r") as dotfile:
                data = json.load(dotfile)
        else:
            data = {}
        with open(dotfile_path, "w") as dotfile:
            data[database_name] = {
                "name": name,
                "type": content_type,
                "desc": description,
            }
            json.dump(data, dotfile)

        storage.atto.Database(database_name).add_data((hash, spaces))
        return web.json_response({"stored": True, "size": size})

    async def _file_sender(self, file_name=None):
        async with aiofiles.open(file_name, "rb") as f:
            chunk = await f.read(64 * 1024)
            while chunk:
                yield chunk
                chunk = await f.read(64 * 1024)
