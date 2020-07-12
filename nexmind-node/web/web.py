import jwt
import exceptions
import aiohttp_cors

from aiohttp import web
from .queries import Queries


class Web:
    def __init__(self, auth_database, args):
        self.args = args
        self.queries = Queries(auth_database)
        self.app = web.Application(
            middlewares=[self.error_middleware, self.auth_middleware],
            client_max_size=10 * 2 ** 30,
        )  # 10GiB
        self.app.add_routes(
            [
                web.get("/debug", self.queries.debug),
                web.post("/login", self.queries.login),
                web.post("/logout", self.queries.logout),
                web.post("/search", self.queries.search),
                web.post("/download", self.queries.download),
                web.post("/delete", self.queries.delete),
                web.post("/upload", self.queries.upload),
            ]
        )
        cors = aiohttp_cors.setup(
            self.app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True, expose_headers="*", allow_headers="*",
                )
            },
        )
        for route in list(self.app.router.routes()):
            cors.add(route)

    def start(self):
        web.run_app(self.app, path=self.args.path, port=self.args.port)

    @web.middleware
    async def error_middleware(self, request, handler):
        try:
            response = await handler(request)
            if response.status < 400:  # if no error coccured
                return response
            message = response.message
            status = response.status

        except exceptions.UserError as exception:
            message = exception.args[0]
            status = exception.code

        except web.HTTPException as exception:
            message = exception.reason
            status = 500

        # except Exception as exception:
        #   message = exception.args[0]
        #   status = 500
        print(message)

        return web.json_response({"error": message}, status=status)

    async def auth_middleware(self, app, handler):
        async def middleware(request):
            request.username = None
            jwt_token = request.headers.get("authorization", None)
            if jwt_token:
                try:
                    if jwt_token in self.queries.EXPIRED_TOKENS:
                        raise exceptions.UserError("blacklisted token")
                    payload = jwt.decode(
                        jwt_token,
                        self.queries.JWT_SECRET,
                        algorithms=[self.queries.JWT_ALGORITHM],
                    )
                    request.username = payload["name"]
                except (jwt.DecodeError, jwt.ExpiredSignatureError):
                    pass

            return await handler(request)

        return middleware
