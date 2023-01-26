# TODO LIST BACK-END
## Дипломный проект BACK-END часть для планировщика задач

В данном проекте используются следующие модули:
* Django
* Postgresql


### Установка
### 1. Создать виртуальное окружение
```
python3 -m venv venv
```
#### Установить Poetry
```
# Установка
pip install poetry
```
```
# Установка зависимостей 
poetry install
```

### 2. Создать .env файл в корне проекта
```
SECRET_KEY = 'todolist'
DEBUG = True
DB_ENGINE = django.db.backends.postgresql
DB_NAME = todolist
DB_USER = postgres
DB_PASSWORD = postgres
DB_HOST = localhost
DB_PORT = 5432
```
### 2. Подключить DB PostgreSQL

```
# Запуск образа Docker
docker-compose up --build -d 
```
```
# Выполнить миграции
./manage.py migrate
```

### 2. Запустить сервер
```
./manage.py runserver
```



