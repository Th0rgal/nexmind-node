class UserError(Exception):
    code = 400


class Unauthorized(UserError):
    code = 401


class NotFound(UserError):
    code = 404
