# Telegram bot - автокликер для отметок Genshin Impact

## Описание

* Бот автоматически собирает награды раз в сутки.

Бот запускается раз в сутки + 1-2 часа для создания случайной активности.
В случае запроса отметки в ручную, следующий запуск через 12-14 часов.

Бот хранит сессию локально в папке **sessions** серилизуя ее в бинарный файл с помощью pickle. 

## Стек
1. Selenium
2. Aiogram
3. Apscheduler

## Запуск Бота:

### Ручной запуск
создать .env по шаблону **.env.example** и добавить токен в **.env**
```bash
python -m src.cli
```

### Docker
 - добавить токен в .env по шаблону .env.example
 - Установить Docker
 ```bash
docker build -t genshin_parser .

docker run -d --name genshin_parser --restart always \
  -e TZ=Asia/Almaty \ # Укажи свою time zone 
  --env-file .env \
  -v sessions_value:/code/sessions \
  genshin_parser python src/cli.py 
 ```