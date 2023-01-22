from httpx import AsyncClient


async def test_ping(client: AsyncClient):
    """Этот тест срабатывает, потом происходит ROLLBACK, он запускается еще раз и падает
       Не могу понять что тут не так."""
    response = await client.get('/db/ping')
    assert response.status_code == 200
    assert response.json() == {'status_db': 1}


async def test_save_url(client: AsyncClient):
    params = {
      'url': 'https://google.com',
      'name': 'google'
    }
    response = await client.post('/url', json=params)
    assert response.status_code == 201
    assert response.json().get('url') == 'https://google.com'
    assert response.json().get('name') == 'google'


async def test_redirect_url(client: AsyncClient, test_url):
    response = await client.get('/url/1')
    assert response.status_code == 307


async def test_status_url(client: AsyncClient, test_url):
    response = await client.get('/url/1/status')
    assert response.status_code == 200
    assert response.json().get('url') == 'http://google.com'
    assert response.json().get('name') == 'google'


async def test_delete_url(client: AsyncClient, test_url):
    response = await client.delete('/url/1')
    assert response.status_code == 202
