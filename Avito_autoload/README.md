# Avito Autoload

Модуль для автоматической генерации XML-файлов для массовой загрузки объявлений на Avito.ru.

## Возможности

- Создание XML-файлов для массовой загрузки
- Валидация XML перед отправкой
- Поддержка всех категорий Avito
- Работа с изображениями

## Использование

```python
from root_xml import create_root_xml, add_ad_element, save_xml

# Создаем корневой элемент
root = create_root_xml('Электроника')

# Добавляем объявление
add_ad_element(
    root=root,
    title='Название товара',
    description='Описание товара',
    price=1000,
    images=['image1.jpg', 'image2.jpg'],
    params={
        'Category': 'Электроника',
        'Condition': 'Новое'
    }
)

# Сохраняем XML
save_xml(root, 'avito_export.xml')
```

## Структура проекта

```
Avito_autoload/
├── root_xml.py     # Основной модуль для работы с XML
├── utils.py        # Вспомогательные функции
├── out_xml/        # Директория для сохранения XML
└── README.md       # Документация
```

## Требования

- Python 3.10+
- loguru
- xml.etree.ElementTree (встроенный модуль)

## Лицензия

MIT
