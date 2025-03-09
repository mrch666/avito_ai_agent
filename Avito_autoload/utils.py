#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import xml.etree.ElementTree as ET
from typing import Optional
from loguru import logger

def create_directory(path: str) -> None:
    """
    Создает директорию, если она не существует
    
    Args:
        path (str): Путь к директории
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info(f"Created directory: {path}")
    except Exception as e:
        logger.error(f"Error creating directory {path}: {str(e)}")
        raise

def validate_xml(root: ET.Element) -> bool:
    """
    Проверяет корректность XML
    
    Args:
        root (ET.Element): Корневой элемент XML
    
    Returns:
        bool: True если XML корректен, False в противном случае
    """
    try:
        # Проверка наличия обязательных атрибутов
        if root.tag != 'Ads':
            logger.error("Root element must be 'Ads'")
            return False
            
        if 'formatVersion' not in root.attrib:
            logger.error("Missing 'formatVersion' attribute")
            return False
            
        if 'target' not in root.attrib:
            logger.error("Missing 'target' attribute")
            return False
            
        # Проверка объявлений
        for ad in root.findall('Ad'):
            if not validate_ad(ad):
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"Error validating XML: {str(e)}")
        return False

def validate_ad(ad: ET.Element) -> bool:
    """
    Проверяет корректность элемента объявления
    
    Args:
        ad (ET.Element): Элемент объявления
    
    Returns:
        bool: True если объявление корректно, False в противном случае
    """
    required_fields = ['Title', 'Description', 'Price']
    
    for field in required_fields:
        element = ad.find(field)
        if element is None or not element.text:
            logger.error(f"Missing required field: {field}")
            return False
            
    return True 