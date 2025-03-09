# Примеры использования Avito MCP сервиса в n8n

## 1. Создание одного объявления

### HTTP Request
- Method: POST
- URL: http://localhost:8080/api/v1/create_ad
- Headers: 
  ```json
  {
    "Content-Type": "application/json"
  }
  ```
- Body:
  ```json
  {
    "title": "{{$node.previous.json.title}}",
    "description": "{{$node.previous.json.description}}",
    "price": {{$node.previous.json.price}},
    "category": "{{$node.previous.json.category}}",
    "images": {{$node.previous.json.images}},
    "params": {{$node.previous.json.params}}
  }
  ```

### Пример workflow:
1. Trigger Node (HTTP Trigger или Schedule)
2. Function Node для подготовки данных:
   ```javascript
   return {
     json: {
       title: "iPhone 15 Pro",
       description: "Новый iPhone 15 Pro, 256GB",
       price: 150000,
       category: "Электроника",
       images: ["https://example.com/iphone1.jpg"],
       params: {
         "Condition": "Новое",
         "Brand": "Apple",
         "Model": "iPhone 15 Pro"
       }
     }
   };
   ```
3. HTTP Request Node для отправки запроса к MCP сервису
4. IF Node для проверки успешности операции

## 2. Массовое создание объявлений

### HTTP Request
- Method: POST
- URL: http://localhost:8080/api/v1/create_bulk_ads
- Headers:
  ```json
  {
    "Content-Type": "application/json"
  }
  ```
- Body:
  ```json
  {
    "category": "{{$node.previous.json.category}}",
    "ads": {{$node.previous.json.ads}}
  }
  ```

### Пример workflow:
1. Trigger Node (например, при получении CSV файла)
2. CSV Node для чтения данных
3. Function Node для преобразования данных:
   ```javascript
   const ads = $input.all().map(item => ({
     title: item.json.title,
     description: item.json.description,
     price: parseInt(item.json.price),
     images: item.json.image_url.split(','),
     params: {
       Condition: item.json.condition,
       Brand: item.json.brand
     }
   }));

   return {
     json: {
       category: "Электроника",
       ads: ads
     }
   };
   ```
4. HTTP Request Node для отправки запроса к MCP сервису
5. IF Node для проверки успешности операции

## 3. Мониторинг здоровья сервиса

### HTTP Request
- Method: GET
- URL: http://localhost:8080/api/v1/health

### Пример workflow:
1. Schedule Trigger (каждые 5 минут)
2. HTTP Request Node для проверки здоровья
3. IF Node для проверки статуса
4. Send Email Node для уведомления при проблемах

## Интеграция с другими сервисами

### Пример: Интеграция с Google Sheets
1. Google Sheets Node для чтения данных
2. Function Node для преобразования данных
3. HTTP Request Node для отправки в MCP сервис
4. Google Sheets Node для обновления статуса

### Пример: Интеграция с Telegram
1. Telegram Trigger Node для получения команд
2. Switch Node для разных команд
3. HTTP Request Node для работы с MCP сервисом
4. Telegram Node для отправки результатов

## Советы по использованию
1. Всегда проверяйте ответ сервиса
2. Используйте try-catch в Function Node
3. Добавляйте логирование важных операций
4. Настройте уведомления об ошибках
5. Регулярно проверяйте здоровье сервиса 