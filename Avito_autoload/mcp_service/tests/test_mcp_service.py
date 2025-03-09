import os
import json
import pytest
import xml.etree.ElementTree as ET
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from datetime import datetime
from avito_mcp import AvitoMCPService

@pytest.fixture
async def client():
    """Фикстура для создания тестового клиента"""
    service = AvitoMCPService()
    app = service.app
    async with TestClient(TestServer(app)) as client:
        yield client

async def test_health_check(client):
    """Тест endpoint'а проверки здоровья"""
    resp = await client.get('/api/v1/health')
    assert resp.status == 200
    
    data = await resp.json()
    assert 'status' in data
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

async def test_create_ad(client):
    """Тест создания одного объявления"""
    test_data = {
        "title": "Test iPhone",
        "description": "Test Description",
        "price": 100000,
        "category": "Электроника",
        "images": ["https://example.com/test.jpg"],
        "params": {
            "Condition": "Новое",
            "Brand": "Apple"
        }
    }
    
    resp = await client.post('/api/v1/create_ad', json=test_data)
    assert resp.status == 200
    
    data = await resp.json()
    assert data['status'] == 'success'
    assert 'file' in data
    
    # Проверяем созданный XML файл
    xml_path = data['file']
    assert os.path.exists(xml_path)
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    assert root.tag == 'Ads'
    assert root.attrib['formatVersion'] == '3'
    assert root.attrib['target'] == 'Avito.ru'
    
    ad = root.find('Ad')
    assert ad is not None
    assert ad.find('Title').text == test_data['title']
    assert ad.find('Description').text == test_data['description']
    assert ad.find('Price').text == str(test_data['price'])
    assert ad.find('Condition').text == test_data['params']['Condition']
    assert ad.find('Brand').text == test_data['params']['Brand']

async def test_create_bulk_ads(client):
    """Тест массового создания объявлений"""
    test_data = {
        "category": "Электроника",
        "ads": [
            {
                "title": "iPhone 1",
                "description": "Description 1",
                "price": 100000,
                "images": ["https://example.com/1.jpg"],
                "params": {"Condition": "Новое"}
            },
            {
                "title": "iPhone 2",
                "description": "Description 2",
                "price": 120000,
                "images": ["https://example.com/2.jpg"],
                "params": {"Condition": "Б/у"}
            }
        ]
    }
    
    resp = await client.post('/api/v1/create_bulk_ads', json=test_data)
    assert resp.status == 200
    
    data = await resp.json()
    assert data['status'] == 'success'
    assert 'file' in data
    
    # Проверяем созданный XML файл
    xml_path = data['file']
    assert os.path.exists(xml_path)
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    assert root.tag == 'Ads'
    assert root.attrib['formatVersion'] == '3'
    assert root.attrib['target'] == 'Avito.ru'
    
    ads = root.findall('Ad')
    assert len(ads) == 2
    
    for i, ad in enumerate(ads):
        test_ad = test_data['ads'][i]
        assert ad.find('Title').text == test_ad['title']
        assert ad.find('Description').text == test_ad['description']
        assert ad.find('Price').text == str(test_ad['price'])
        assert ad.find('Condition').text == test_ad['params']['Condition']

async def test_create_ad_missing_fields(client):
    """Тест создания объявления с отсутствующими полями"""
    test_data = {
        "title": "Test iPhone",
        # Отсутствует description
        "price": 100000,
        "category": "Электроника"
    }
    
    resp = await client.post('/api/v1/create_ad', json=test_data)
    assert resp.status == 400
    
    data = await resp.json()
    assert 'error' in data
    assert 'Missing required field: description' in data['error']

async def test_create_bulk_ads_missing_category(client):
    """Тест массового создания объявлений без категории"""
    test_data = {
        # Отсутствует category
        "ads": [
            {
                "title": "iPhone 1",
                "description": "Description 1",
                "price": 100000
            }
        ]
    }
    
    resp = await client.post('/api/v1/create_bulk_ads', json=test_data)
    assert resp.status == 400
    
    data = await resp.json()
    assert 'error' in data
    assert 'Missing required fields: category' in data['error'] 