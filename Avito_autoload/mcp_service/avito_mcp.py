#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import asyncio
from aiohttp import web
from typing import Dict, List, Optional
from loguru import logger
from datetime import datetime

# Импортируем функции для работы с XML
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from root_xml import create_root_xml, add_ad_element, save_xml
from utils import validate_xml

class AvitoMCPService:
    def __init__(self, host: str = '0.0.0.0', port: int = 8080):
        """
        Инициализация MCP сервиса
        
        Args:
            host (str): Хост для запуска сервера
            port (int): Порт для запуска сервера
        """
        self.host = host
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        
    def setup_routes(self):
        """Настройка маршрутов API"""
        self.app.router.add_post('/api/v1/create_ad', self.create_ad)
        self.app.router.add_post('/api/v1/create_bulk_ads', self.create_bulk_ads)
        self.app.router.add_get('/api/v1/health', self.health_check)
        
    async def create_ad(self, request: web.Request) -> web.Response:
        """
        Создание одного объявления
        
        POST /api/v1/create_ad
        {
            "title": "Название товара",
            "description": "Описание товара",
            "price": 1000,
            "category": "Электроника",
            "images": ["url1.jpg", "url2.jpg"],
            "params": {
                "Condition": "Новое",
                "Brand": "Example"
            }
        }
        """
        try:
            data = await request.json()
            
            # Валидация входных данных
            required_fields = ['title', 'description', 'price', 'category']
            for field in required_fields:
                if field not in data:
                    return web.json_response(
                        {'error': f'Missing required field: {field}'}, 
                        status=400
                    )
            
            # Создаем XML
            root = create_root_xml(data['category'])
            add_ad_element(
                root=root,
                title=data['title'],
                description=data['description'],
                price=data['price'],
                images=data.get('images', []),
                params=data.get('params', {})
            )
            
            # Сохраняем XML
            filename = f'avito_ad_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml'
            filepath = save_xml(root, filename)
            
            return web.json_response({
                'status': 'success',
                'message': 'Ad created successfully',
                'file': filepath
            })
            
        except Exception as e:
            logger.error(f"Error creating ad: {str(e)}")
            return web.json_response(
                {'error': str(e)}, 
                status=500
            )
            
    async def create_bulk_ads(self, request: web.Request) -> web.Response:
        """
        Создание нескольких объявлений
        
        POST /api/v1/create_bulk_ads
        {
            "category": "Электроника",
            "ads": [
                {
                    "title": "Товар 1",
                    "description": "Описание 1",
                    "price": 1000,
                    "images": ["url1.jpg"],
                    "params": {"Condition": "Новое"}
                },
                {
                    "title": "Товар 2",
                    "description": "Описание 2",
                    "price": 2000,
                    "images": ["url2.jpg"],
                    "params": {"Condition": "Б/у"}
                }
            ]
        }
        """
        try:
            data = await request.json()
            
            if 'category' not in data or 'ads' not in data:
                return web.json_response(
                    {'error': 'Missing required fields: category, ads'}, 
                    status=400
                )
            
            # Создаем XML
            root = create_root_xml(data['category'])
            
            # Добавляем объявления
            for ad_data in data['ads']:
                add_ad_element(
                    root=root,
                    title=ad_data['title'],
                    description=ad_data['description'],
                    price=ad_data['price'],
                    images=ad_data.get('images', []),
                    params=ad_data.get('params', {})
                )
            
            # Сохраняем XML
            filename = f'avito_bulk_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml'
            filepath = save_xml(root, filename)
            
            return web.json_response({
                'status': 'success',
                'message': f'Created {len(data["ads"])} ads successfully',
                'file': filepath
            })
            
        except Exception as e:
            logger.error(f"Error creating bulk ads: {str(e)}")
            return web.json_response(
                {'error': str(e)}, 
                status=500
            )
            
    async def health_check(self, request: web.Request) -> web.Response:
        """
        Проверка работоспособности сервиса
        
        GET /api/v1/health
        """
        return web.json_response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        })
        
    def run(self):
        """Запуск сервера"""
        web.run_app(self.app, host=self.host, port=self.port)

if __name__ == '__main__':
    # Настройка логирования
    logger.add(
        "logs/avito_mcp.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
    
    # Запуск сервиса
    service = AvitoMCPService()
    service.run() 