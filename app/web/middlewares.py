import logging
import typing

from aiohttp.web_middlewares import middleware


if typing.TYPE_CHECKING:
    from app.web.app import Application, Request

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
        return response
    except Exception as e:
        print(e)


def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_middleware)
