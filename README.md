## Бот для поиска студенческих материалов

##### Установка проекта
``` bash 
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

##### Запуск тестов
``` bash
python3 -m unittest discover tests
```

##### Запуск Telegram бота
``` bash
python3 tg_bot/main.py
```

Приложение может быть запущено как несколько отдельных ботов, (отдельно Telegram, Vk)