# Объект router, в котором регистрируем обработчики
from _socket import gaierror

import asyncpg
from fastapi import APIRouter, HTTPException

from src.core.config import app_settings

check_db_router = APIRouter(prefix='/db', tags=['DB'])


@check_db_router.get('/ping')
async def ping_db():
    try:
        conn = await asyncpg.connect(dsn=app_settings.DATABASE_DSN.replace('+asyncpg', ''))
    except ConnectionRefusedError as e:
        raise HTTPException(status_code=404, detail=f'Database not found. {e}')
    except gaierror:
        raise HTTPException(status_code=404, detail=f'Credentials not correct.')
    else:
        result = await conn.fetchval('SELECT 1')
        await conn.close()
        return {'status_db': result}
