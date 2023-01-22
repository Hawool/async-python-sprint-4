import logging
from http import HTTPStatus
from logging.config import dictConfig

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from starlette.responses import Response

from src.api.v1.check_db import check_db_router
from src.api.v1.urls import urls_router
from src.core.config import app_settings
from src.core.constants import BLACK_LIST
from src.core.logger import LOGGING

dictConfig(LOGGING)
logger = logging.getLogger('root')

app = FastAPI(
    title=app_settings.APP_TITLE,
    default_response_class=ORJSONResponse,
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if request.client.host in BLACK_LIST:  # type: ignore
        return Response(status_code=HTTPStatus.IM_A_TEAPOT)
    return await call_next(request)

app.include_router(urls_router)
app.include_router(check_db_router)

if __name__ == '__main__':
    logger.info('Server started')
    uvicorn.run(
        'main:app',
        host=app_settings.HOST,
        port=app_settings.PORT,
    )
