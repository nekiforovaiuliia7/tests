import pytest
from app import app, load_data, save_data
import json
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_data():
    test_data = {
        "history": {"test_user": ["Москва"]},
        "stats": {"Москва": 1}
    }
    save_data(test_data)
    yield test_data
    if os.path.exists('data.json'):
        os.remove('data.json')

def test_index_page(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert 'Прогноз погоды' in resp.text

def test_weather_search(client):
    resp = client.post('/', data={'city': 'Москва'})
    assert resp.status_code == 200
    assert 'Погода в городе Москва' in resp.text
    assert 'Температура' in resp.text

def test_invalid_city(client):
    resp = client.post('/', data={'city': 'НесуществующийГород123'})
    assert resp.status_code == 200
    assert 'Город не найден' in resp.text

def test_stats_api(client, test_data):
    resp = client.get('/api/stats')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'Москва' in data
    assert data['Москва'] == 1 