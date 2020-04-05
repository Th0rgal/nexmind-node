class UserError(Exception):
    code = 400

class Unauthorized(Exception):
    code = 401

class NotFound(Exception):
    code = 404