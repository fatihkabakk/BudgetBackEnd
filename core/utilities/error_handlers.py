from flask import Flask
from core.validation.responses import ErrorResponse
from werkzeug.exceptions import MethodNotAllowed


class ErrorHandler:
    def __init__(self, app: Flask) -> None:
        @app.errorhandler(404)
        def page_not_found(e):
            return ErrorResponse('Page not found.'), 404

        @app.errorhandler(400)
        def bad_request(e):
            return ErrorResponse('Bad request.'), 400

        @app.errorhandler(500)
        def internal_server_error(e):
            return ErrorResponse('Internal server error.'), 500

        @app.errorhandler(MethodNotAllowed)
        def method_not_allowed(e):
            return ErrorResponse('Method not allowed.'), 405
