## Бот для поиска студенческих материалов

##### Установка проекта
``` bash 
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```
##### Запуск docker контейнера с Elasticsearch впервые:
``` bash
docker run --name es02 --net elastic -p 9200:9200 -p 9300:9300 -it docker.elastic.co/elasticsearch/elasticsearch:8.3.2
```

##### Запуск остановленного docker контейнера Elasticsearch:
``` bash
docker start es02
docker attach es02
```

##### Запуск тестов
``` bash
python3 -m unittest discover tests
```
Тесты для Elasticsearch проверяют работу с подключением к базе данных, поэтому для их работы необходимо предварительно запустить контейнер с Elasticsearch

##### Запуск Telegram бота
``` bash
python3 tg_bot/main.py
```

#### Запуск базы данных
``` bash
cd databases
docker-compose up
```
После данной операции база данных будет запущена в docker контейре.
Для просмотра данных в базе данных удобно использовать Visual Studio Code. 
Инструкция https://www.youtube.com/watch?v=2vwwwA4AEyk&t=641s

#### Для создания базы данных запустите
``` bash
python3 src/pg/pg_utils.py
```



