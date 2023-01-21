import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse

from src.core.config import app_settings
from src.core.constants import APIUrlAnswers
from src.db.db import get_session
from src.schemas import url as url_schemas
from src.services.url import url_crud

# Объект router, в котором регистрируем обработчики
urls_router = APIRouter()


@urls_router.get('/ping')
async def root():
    try:
        conn = await asyncpg.connect(dsn=app_settings.DATABASE_DSN.replace('+asyncpg', ''))
        await conn.close()
        return {'status_db': 'success'}
    except ConnectionRefusedError as e:
        raise HTTPException(status_code=404, detail=f'Database not found. {e}')


@urls_router.post('/', status_code=201, response_model=url_schemas.UrlInDB)
async def save_url(
        create_url: url_schemas.UrlCreate,
        db: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    return await url_crud.create(db=db, obj_in=create_url)


@urls_router.get('/{url_id}', status_code=307)
async def redirect_url(
        *,
        url_id: int,
        db: AsyncSession = Depends(get_session)
) -> RedirectResponse:
    url = await url_crud.get(db=db, id=url_id)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Url not found'
        )
    if url.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail=APIUrlAnswers.GONE
        )

    update_url_schema = url_schemas.UrlUpdate(number_of_transitions=url.number_of_transitions + 1)
    url = await url_crud.update(db=db, db_obj=url, obj_in=update_url_schema)

    return RedirectResponse(
        url=str(url.url),
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )


@urls_router.get('/{url_id}/status', status_code=200, response_model=url_schemas.UrlInDB)
async def status_url(
        *,
        url_id: int,
        db: AsyncSession = Depends(get_session)
) -> url_schemas.UrlInDB:
    url = await url_crud.get(db=db, id=url_id)
    if not url or url.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=APIUrlAnswers.NOT_FOUND
        )

    if url.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail=APIUrlAnswers.GONE
        )

    return url


@urls_router.delete('/{url_id}', status_code=202)
async def delete_url(
        *,
        url_id: int,
        db: AsyncSession = Depends(get_session)
):
    url = await url_crud.get(db=db, id=url_id)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Url not found'
        )

    update_url_schema = url_schemas.UrlUpdate(is_deleted=True)
    url = await url_crud.update(db=db, db_obj=url, obj_in=update_url_schema)
