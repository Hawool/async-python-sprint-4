import logging
from http import HTTPStatus
from logging.config import dictConfig

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from starlette.responses import Response

from core.logger import LOGGING
from src.api.v1.urls import urls_router
from src.core.config import app_settings


dictConfig(LOGGING)
logger = logging.getLogger('root')

app = FastAPI(
    title=app_settings.APP_TITLE,
    default_response_class=ORJSONResponse,
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if request.client.host == '127.0.0.2':
        return Response(status_code=HTTPStatus.IM_A_TEAPOT)
    response = await call_next(request)
    return response

app.include_router(urls_router)

if __name__ == '__main__':
    logger.info('Server started')
    uvicorn.run(
        'main:app',
        host=app_settings.HOST,
        port=app_settings.PORT,
    )
