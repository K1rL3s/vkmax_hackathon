from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from maxhack.core.exceptions import EntityNotFound, InvalidValue, NotEnoughRights
from maxhack.logger import get_logger

logger = get_logger(__name__)


async def not_enough_rights_exception_handler(
    request: Request,
    exc: NotEnoughRights,
) -> JSONResponse:
    logger.warning("403_FORBIDDEN", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=jsonable_encoder({"reason": str(exc)}),
    )


async def entity_not_found_exception_handler(
    request: Request,
    exc: EntityNotFound,
) -> JSONResponse:
    logger.warning("404_NOT_FOUND", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"reason": str(exc)}),
    )


async def value_error_exception_handler(
    request: Request,
    exc: ValueError,
) -> JSONResponse:
    logger.warning("409_CONFLICT", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=jsonable_encoder({"reason": str(exc)}),
    )


async def invalid_value_exception_handler(
    request: Request,
    exc: ValueError | InvalidValue,
) -> JSONResponse:
    logger.warning("409_CONFLICT", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=jsonable_encoder({"reason": str(exc)}),
    )


def validation_exception_handler(request: Request, exc: RequestValidationError):
    messages = "\n\n".join(
        f'{error["loc"]}\n{error["msg"]}\n{error["type"]}' for error in exc.errors()
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"reason": messages}),
    )


def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"reason": exc.detail or "Something went wrong"}),
    )


async def unknown_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception("500_INTERNAL_SERVER_ERROR", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({"reason": "Internal Server Error"}),
    )


exception_handlers = {
    NotEnoughRights: not_enough_rights_exception_handler,
    EntityNotFound: entity_not_found_exception_handler,
    ValueError: value_error_exception_handler,
    InvalidValue: value_error_exception_handler,
    RequestValidationError: validation_exception_handler,
    StarletteHTTPException: http_exception_handler,
    Exception: unknown_exception_handler,
}
