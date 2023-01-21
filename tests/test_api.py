import pytest
from _pytest import monkeypatch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.urls import UrlModel


@pytest.mark.anyio()
async def test_ping(client: AsyncClient):
    """Этот тест срабатывает, потом происходит ROLLBACK, он запускается еще раз и падает
       Не могу понять что тут не так."""
    response = await client.get('/ping')
    assert response.status_code == 200
    assert response.json() == {'status_db': 'success'}


@pytest.mark.anyio()
async def test_save_url(client: AsyncClient):
    """Аналогичная ситуация, тесты прогоняются первый раз успешно, потом почему-то запускаются еще раз
       и падают с ошибкой RuntimeError: There is no current event loop in thread 'MainThread'."""
    params = {
      'url': 'https://google.com',
      'name': 'google'
    }
    response = await client.post('/', json=params)
    assert response.status_code == 201
    assert response.json().get('url') == 'https://google.com'
    assert response.json().get('name') == 'google'
