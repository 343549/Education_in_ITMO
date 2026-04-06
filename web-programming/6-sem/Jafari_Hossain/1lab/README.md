# Team Finder API (FastAPI)

Серверная часть для веб-платформы поиска людей/команд: регистрация, JWT-аутентификация и дополнительные API по пользователям.

## Быстрый старт (PostgreSQL + Alembic)

1. Установить зависимости
   - `py -m venv .venv`
   - `.venv\Scripts\pip.exe install -r requirements.txt`
2. Подними PostgreSQL (вариант через Docker Compose)
   - `docker compose up -d`
3. Настрой переменные окружения
   - скопируй `.env.example` в `.env`
   - поменяй `SECRET_KEY`
   - при необходимости измени `DATABASE_URL`
4. Примени миграции
   - `.venv\Scripts\alembic.exe upgrade head`
5. Запусти сервер
   - `.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000`

API-документация:
- `http://127.0.0.1:8000/docs`

Остановить PostgreSQL-контейнер:
- `docker compose down`

## Основные эндпоинты

- `POST /auth/register` — регистрация
- `POST /auth/login` — получение JWT
- `GET /users/me` — текущий пользователь (требуется `Authorization: Bearer ...`)
- `GET /users/` — список пользователей
- `POST /users/me/change-password` — смена пароля
- `GET /users/me/profile` — профиль с вложенными навыками
- `PUT /users/me/skills` / `DELETE /users/me/skills/{skill_id}` — управление навыками пользователя

CRUD по сущностям:
- `skills`: `POST/GET/GET by id/PUT/DELETE`
- `projects`: `POST/GET/GET by id(with nested teams+members+tasks)/PUT/DELETE`
- `teams`: `POST/GET/GET by id(with nested members+tasks)/PUT/DELETE`
- `tasks`: `POST/GET/GET by id/PUT/DELETE`
- `teams/{team_id}/members`: добавление/изменение роли/удаление участника команды

## Модель данных (ORM)

Реализованы таблицы и связи:
- 7 таблиц: `users`, `skills`, `projects`, `teams`, `project_tasks`, `user_skills`, `team_memberships`
- many-to-many через ассоциативные сущности:
  - `user_skills` с полем `proficiency`
  - `team_memberships` с полем `role`
- one-to-many:
  - `users -> projects`
  - `projects -> teams`
  - `teams -> project_tasks`

Диаграмма ER (Mermaid): `ERD.md`

## Миграции

- Конфиг Alembic: `alembic.ini`
- Окружение миграций: `alembic/env.py`
- Первая миграция: `alembic/versions/20260403_0001_initial_schema.py`

