# api_yamdb
# Описание проекта:

Yamdb - это онлайн-платформа, где пользователи могут делиться отзывами на различные произведения, такие как книги, фильмы и музыка. Произведения разделены на категории, такие как "Категории", "Фильмы" и "Музыка". Администратор имеет возможность добавлять новые категории.

Само содержимое произведений (например, фильмы или музыка) не хранится в Yamdb, поэтому нельзя прямо на платформе смотреть фильмы или слушать музыку. Вместо этого, произведения представлены в виде объектов с названием, годом выпуска и описанием. Каждое произведение может иметь жанр из предустановленного списка. Толко администратор имеет возможность добавлять новые жанры.

Пользователи могут оставлять текстовые отзывы и ставить произведению оценку от одного до десяти. Из этих оценок рассчитывается средняя оценка произведения (рейтинг). Каждый пользователь может оставить только один отзыв к произведению.

# Используемые технологии:

- Язык программирования: Python
- Фреймворк: Django
- Фреймворк для создания веб-API: Django REST Framework
- Библиотека для работы с JWT-токенами: djangorestframework-simplejwt


# Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/nicros22/api_yamdb
```
```
cd api_yamdb
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
```
source env/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
# Некоторые примеры запросов к API:

## Регистрация нового пользователя:

**POST**
```
http://127.0.0.1:8000/api/v1/auth/signup/
```

```
{
"email": "string",
"username": "string"
}
```
## Получение JWT-токена:

**POST**
```
http://127.0.0.1:8000/api/v1/auth/token/
```
```
{
"token": "string"
}
```
## Получение списка всех категорий:

**GET**
```
http://127.0.0.1:8000/api/v1/categories/
```
```
{
"count": 0,
"next": "string",
"previous": "string",
"results": [
{}
]
}
```
## Добавление новой категории:

**POST**
```
http://127.0.0.1:8000/api/v1/categories/
```
```
{
"name": "string",
"slug": "string"
}
```
## Получение списка всех жанров:

**GET**
```
http://127.0.0.1:8000/api/v1/genres/
```
```
{
"count": 0,
"next": "string",
"previous": "string",
"results": [
{}
]
}
```
## Добавление жанра:

**POST**
```
http://127.0.0.1:8000/api/v1/genres/
```
```
{
"name": "string",
"slug": "string"
}
```
## Добавление произведения:

**POST**
```
http://127.0.0.1:8000/api/v1/titles/
```
```
{
"name": "string",
"year": 0,
"description": "string",
"genre": [
"string"
],
"category": "string"
}
```
## Частичное обновление отзыва по id:

**PATCH**
```
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/
```
```
{
"text": "string",
"score": 1
}
```
## Получение списка всех комментариев к отзыву:

**GET**
```
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/
```
```
{
"count": 0,
"next": "string",
"previous": "string",
"results": [
{}
]
}
```
## Добавление комментария к отзыву:

**POST**
```
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/
```
```
{
"text": "string"
}
```
## Получение данных своей учетной записи:

**GET**
```
http://127.0.0.1:8000/api/v1/users/me/
```
```
{
"username": "string",
"email": "user@example.com",
"first_name": "string",
"last_name": "string",
"bio": "string",
"role": "user"
}
```
## Изменение данных своей учетной записи:

**PATCH**
```
http://127.0.0.1:8000/api/v1/users/me/
```
```
{
"username": "string",
"email": "user@example.com",
"first_name": "string",
"last_name": "string",
"bio": "string"
}v
```
# Авторы:
- Иванов Дмитрий
- Паженцева Таисия
- Пономаренко Никита