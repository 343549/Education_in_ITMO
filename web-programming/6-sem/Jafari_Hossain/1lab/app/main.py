from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.projects import router as projects_router
from app.routes.skills import router as skills_router
from app.routes.tasks import router as tasks_router
from app.routes.teams import router as teams_router
from app.routes.users import router as users_router


def create_app() -> FastAPI:
    # Создаём приложение как “фабрику”, чтобы удобно тестировать и переиспользовать.
    app = FastAPI(title="Team Finder API")

    # Разрешаем CORS, чтобы фронтенд приложение мог обращаться к API.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", tags=["system"], summary="Health check") 
    def root() -> dict:
        # Чтобы при открытии главной страницы в браузере не было 404.
        return {"status": "ok", "service": "Team Finder API", "docs": "/docs"}

    # Подключаем роуты с префиксами.
    app.include_router(auth_router, tags=["auth"])
    app.include_router(users_router, tags=["users"])
    app.include_router(skills_router, tags=["skills"])
    app.include_router(projects_router, tags=["projects"])
    app.include_router(teams_router, tags=["teams"])
    app.include_router(tasks_router, tags=["tasks"])
    return app


app = create_app()

