# Foodgram
[![Main Kittygram workflow](https://github.com/Daniil-Mikolaychuk/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/Daniil-Mikolaychuk/kittygram_final/actions/workflows/main.yml)
## Описание
Проект Foodgram  служит интернет-площадкой для любителей рецептов и хорошо поесть. Чтобы люди могли делиться с другими своими изыскаными блюдами, добавлять их фотографиями и хавстаться их вкусовыми особенностями. Благодаря данному ресурсу кулинары могут создать список своих любимых блюд, а также добавлять чужие рецепты себе в избранное или даже скачать файлом. 

## Содержание
- [Стек использованных технологий](#технологии)
- [Начало работы](#начало-работы)
- [Переменные окружения](#переменные-окружения)
- [Примеры запросов и ответов](#запросы-и-ответы)
- [Команда проекта](#команда-проекта)
- [Источники](#источники)

## Стек использованных технологий
- Python 3.9.10
- Django==3.2
- djangorestframework==3.12.4
- psycopg2-binary==2.9.3
- Postgresql
- Gunicorn
- Nginx


## Начало работы
### Как запустить Kittygram на сервере
Для запуска приложения необходим сервер, рассмотрим на примере сервера под управлением ОС Linux.
Создать директорию kittygram на сервере.
```
mkdir foodgram
cd foodgram
```

Установить Docker Compose на сервер
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin 
```

Перенести docker-compose.production.yml и .env на сервер
```
scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/foodgram/docker-compose.production.yml
```

Запустить докер
```
sudo docker compose -f docker-compose.production.yml up -d
```

Выполнить миграции
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
### Переменные окружения
Для того чтоб проект работал, а секретные данные не попали в GitHub, необходимо их "спрятать" в .env
#### Локально в файле .env
- ALLOWED_HOSTS - разрешенные хосты
- DEBUG - статус разработки
- SECRET_KEY - ключ доступа
- DATABASES - смена базы данных на sqlite3
##### Данные для работы Postgresql
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DBo
- DB_HOST
- DB_PORT
#### Для работы на своем сервере добавьте секреты в GitHub Actions
- DOCKER_PASSWORD - пароль от аккаунта DockerHub
- DOCKER_USERNAME - логин DockerHub
- HOST - IP адресс сервера
- USER - логин на сервере
- SSH_KEY - SSH ключ
- SSH_PASSPHRASE - пароль от сервера
## Основные эндпоинты API

- ```/api/users/``` - пользователи
- ```/api/tags/``` - теги
- ```/api/ingredients/``` - ингредиенты
- ```/api/recipes/``` - рецепты
#### Примеры запросов и ответов
В результате GET запросов к api, будем получать данные в формате application/json.
- Получение ингредиента: GET http://127.0.0.1:8000/api/ingredients/4/
```
{
    "id": 4,
    "name": "абрикосовый сок",
    "measurement_unit": "мл"
}
```
- Получение списка рецептов: GET http://127.0.0.1:8000/api/recipes/
```
Список рецептов вида:
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 36,
            "tags": [
                {
                    "id": 3,
                    "name": "Bread",
                    "slug": "bread"
                },
                {
                    "id": 5,
                    "name": "Vegans",
                    "slug": "vegans"
                }
            ],
            "author": {
                "email": "user3@user.ru",
                "id": 10,
                "username": "user3",
                "avatar": "http://127.0.0.1:8000/media/users/3f3e8389-9fb1-489a-8459-c3563be9f7ea.jpg",
                "first_name": "user3",
                "last_name": "user3",
                "is_subscribed": false
            },
            "ingredients": [
                {
                    "id": 898,
                    "name": "мадера",
                    "measurement_unit": "г",
                    "amount": 22
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false,
            "image": "http://127.0.0.1:8000/media/recipes/images/cb686483-8676-40c6-8689-5315b524a386.jpg",
            "name": "пвапа",
            "text": "22",
            "published_date": "2025-06-25T18:02:03.113602Z",
            "cooking_time": 22
        },
```
- Добавление пользователя нового Post: http://127.0.0.1:8000/api/users/
```
запрос:
    {
        "username": "user4",
        "email": "user4@user.ru",
        "first_name": "user4",
        "last_name": "user4",
        "user4": "milk",
        "password": "newpasu4"
    }
```
```
ответ:
    {
        "username": "user4",
        "email": "user4@user.ru",
        "first_name": "user4",
        "last_name": "user4",
        "id": 11
    }
```
-  Админка сайта http://127.0.0.1:8000/admin/
```
Страница админки сайта.
```

## Команда проекта
Разработкой занимались:
- [Даниил Миколайчук](https://github.com/Daniil-Mikolaychuk) — Backend Engineer

## Источники
Учебный проект Яндекс-практикум.