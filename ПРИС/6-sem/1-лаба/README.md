# EcoGuardian

Прототип веб-сервиса мониторинга экологической обстановки на базе Django.

## Запуск

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Сервис будет доступен по адресу `http://127.0.0.1:8000/`.
