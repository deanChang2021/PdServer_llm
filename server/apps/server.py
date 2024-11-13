import uvicorn
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from server.handler.exceptions import APPBaseException, ErrorCode


def init_app():
    _app = FastAPI(title="pdServer API")

    register_blueprints(_app)
    exc_handler(_app)
    return _app


def exc_handler(_app):

    @_app.exception_handler(RequestValidationError)
    def validation_exception_handler(_, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "code": ErrorCode.REQUEST_PARAMS_ERROR.value,
                "message": f"request params error: {exc.body}"
            },
        )

    @_app.exception_handler(APPBaseException)
    def validation_exception_handler(_, exc: APPBaseException):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": exc.code.value,
                "message": exc.message
            },
        )


def register_blueprints(_app):
    from server.apps import sys_app
    from server.apps import document_app

    """你可以对不同的路由类型写入不同的文件，但一定要在此完成注册"""
    _app.include_router(sys_app.router, prefix="/v1/api/trigger")
    _app.include_router(document_app.router, prefix="/v1/api/trigger")

def run(host, port):
    _app = init_app()
    uvicorn.run(_app, port=port, host=host)
