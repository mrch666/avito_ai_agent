#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional
from utils import create_directory, validate_xml

def create_root_xml(category: str, params: Optional[Dict] = None) -> ET.Element:
    """
    Создает корневой элемент XML для объявления
    
    Args:
        category (str): Категория товара
        params (Dict): Дополнительные параметры
    
    Returns:
        ET.Element: Корневой элемент XML
    """
    root = ET.Element('Ads', formatVersion="3", target="Avito.ru")
    return root

def add_ad_element(
    root: ET.Element,
    title: str,
    description: str,
    price: int,
    images: List[str],
    params: Optional[Dict] = None
) -> ET.Element:
    """
    Добавляет элемент объявления в XML
    
    Args:
        root (ET.Element): Корневой элемент XML
        title (str): Заголовок объявления
        description (str): Описание объявления
        price (int): Цена
        images (List[str]): Список путей к изображениям
        params (Dict): Дополнительные параметры
    
    Returns:
        ET.Element: Элемент объявления
    """
    ad = ET.SubElement(root, 'Ad')
    
    # Основные параметры
    ET.SubElement(ad, 'Title').text = title
    ET.SubElement(ad, 'Description').text = description
    ET.SubElement(ad, 'Price').text = str(price)
    
    # Изображения
    images_element = ET.SubElement(ad, 'Images')
    for image in images:
        ET.SubElement(images_element, 'Image', url=image)
    
    # Дополнительные параметры
    if params:
        for key, value in params.items():
            ET.SubElement(ad, key).text = str(value)
    
    return ad

def save_xml(root: ET.Element, filename: str) -> str:
    """
    Сохраняет XML в файл
    
    Args:
        root (ET.Element): Корневой элемент XML
        filename (str): Имя файла
    
    Returns:
        str: Путь к сохраненному файлу
    """
    tree = ET.ElementTree(root)
    create_directory('out_xml')
    filepath = os.path.join('out_xml', filename)
    tree.write(filepath, encoding='utf-8', xml_declaration=True)
    return filepath

if __name__ == '__main__':
    # Пример использования
    root = create_root_xml('Электроника')
    add_ad_element(
        root=root,
        title='Тестовое объявление',
        description='Описание тестового объявления',
        price=1000,
        images=['test1.jpg', 'test2.jpg'],
        params={'Category': 'Электроника', 'Condition': 'Новое'}
    )
    save_xml(root, f'avito_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml')
