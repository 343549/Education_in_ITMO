# Лабораторная работа №1  
**Тема:** Разработка серверной части веб-платформы для поиска людей в команду (FastAPI)

## 1. Цель работы
Реализовать полноценное серверное приложение на FastAPI с:
- регистрацией и авторизацией пользователей;
- JWT-аутентификацией;
- хэшированием паролей;
- CRUD-операциями для предметной области;
- PostgreSQL + ORM;
- миграциями Alembic;
- аннотацией типов и структурированной файловой архитектурой.

## 2. Используемые технологии
- **Python 3.12**
- **FastAPI**
- **SQLAlchemy 2.0**
- **PostgreSQL** (через `psycopg`)
- **Alembic**
- **JWT** (`python-jose`)
- **bcrypt**
- **Docker Compose** (для локального запуска PostgreSQL)

## 3. Предметная область
Платформа предназначена для поиска партнеров в команды и совместной работы над проектами:
- пользователи создают профиль;
- указывают навыки;
- создают проекты и команды;
- управляют участниками и задачами.

## 4. Структура проекта
```text
1lab/
  app/
    db/
    models/
    routes/
    schemas/
    config.py
    deps.py
    main.py
    security.py
  alembic/
    versions/
  alembic.ini
  docker-compose.yml
  ERD.md
  README.md
  requirements.txt
```

## 5. Модель данных (ER)
Реализовано **7 таблиц**:
- `users`
- `skills`
- `projects`
- `teams`
- `project_tasks`
- `user_skills` (ассоциативная)
- `team_memberships` (ассоциативная)

### Связи
- **one-to-many**:
  - `users -> projects`
  - `projects -> teams`
  - `teams -> project_tasks`
- **many-to-many**:
  - `users <-> skills` через `user_skills` с полем `proficiency`
  - `teams <-> users` через `team_memberships` с полем `role`

ER-диаграмма: `ERD.md`

## 6. Реализованный API

### 6.1 Аутентификация и пользователь
- `POST /auth/register` — регистрация
- `POST /auth/login` — получение JWT
- `GET /users/` — список пользователей
- `GET /users/me` — текущий пользователь по токену
- `GET /users/me/profile` — профиль с вложенными навыками
- `PUT /users/me/skills` — добавить/обновить навык пользователя
- `DELETE /users/me/skills/{skill_id}` — удалить навык пользователя
- `POST /users/me/change-password` — смена пароля

### 6.2 CRUD предметной области
- `skills`: `POST/GET/GET by id/PUT/DELETE`
- `projects`: `POST/GET/GET by id/PUT/DELETE`
- `teams`: `POST/GET/GET by id/PUT/DELETE`
- `tasks`: `POST/GET/GET by id/PUT/DELETE`
- `teams/{team_id}/members`: добавление/обновление роли/удаление участника

### 6.3 Вложенные ответы
- `GET /projects/{project_id}` возвращает проект с вложенными:
  - командами,
  - участниками команд,
  - задачами.
- `GET /teams/{team_id}` возвращает команду с вложенными:
  - участниками,
  - задачами.

## 7. Безопасность
- Пароли хранятся в виде bcrypt-хэшей.
- JWT-токен выдаётся при логине и используется в `Authorization: Bearer <token>`.
- Проверка токена и получение текущего пользователя реализованы через dependency `get_current_user`.

## 8. Миграции базы данных
- Конфиг: `alembic.ini`
- Окружение: `alembic/env.py`
- Первая миграция: `alembic/versions/20260403_0001_initial_schema.py`

Применение миграций:
```bash
.venv\Scripts\alembic.exe upgrade head
```

## 9. Инструкция запуска
1. Установить зависимости:
```bash
py -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
```
2. Поднять PostgreSQL:
```bash
docker compose up -d
```
3. Настроить `.env` (по примеру `.env.example`).
4. Применить миграции:
```bash
.venv\Scripts\alembic.exe upgrade head
```
5. Запустить API:
```bash
.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```
6. Swagger:
```text
http://127.0.0.1:8000/docs
```

## 10. Сценарий демонстрации на защите
1. Регистрация пользователя (`/auth/register`)
2. Логин и получение JWT (`/auth/login`)
3. Авторизация в Swagger через `Bearer token`
4. Создание навыка (`/skills`)
5. Добавление навыка текущему пользователю (`/users/me/skills`)
6. Создание проекта (`/projects`)
7. Создание команды (`/teams`)
8. Создание задачи (`/tasks`)
9. Показ вложенного ответа (`/projects/{id}`)
10. Смена пароля (`/users/me/change-password`)

## 11. Соответствие требованиям ЛР
- FastAPI сервер: **выполнено**
- ORM + PostgreSQL: **выполнено**
- CRUD API: **выполнено**
- Вложенные модели в GET: **выполнено**
- Миграции Alembic: **выполнено**
- Аннотация типов: **выполнено**
- Разделение кода по слоям/папкам: **выполнено**
- Комментарии к сложным частям: **выполнено**

## 12. Вывод
В ходе работы реализовано серверное приложение на FastAPI с аутентификацией, безопасной работой с паролями, реляционной моделью данных с требуемыми связями, набором CRUD-методов и миграциями. Проект готов к демонстрации и дальнейшему расширению функционала платформы.

