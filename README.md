## Бот для поиска студенческих материалов

##### Установка проекта
``` bash 
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```
##### Запуск docker контейнера впервые:
``` bash
docker run --name es02 --net elastic -p 9200:9200 -p 9300:9300 -it docker.elastic.co/elasticsearch/elasticsearch:8.3.2
```

##### Запуск остановленного docker контейнера:
``` bash
docker start es02
docker attach es02
```


##### Запуск тестов
``` bash
python3 -m unittest discover tests
```