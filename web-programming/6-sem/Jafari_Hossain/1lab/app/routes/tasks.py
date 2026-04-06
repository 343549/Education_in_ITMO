from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.task import ProjectTask
from app.models.team import Team
from app.schemas.domain import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks")


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskRead:
    # Нельзя создать задачу без существующей команды.
    team = db.execute(select(Team).where(Team.id == payload.team_id)).scalars().first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    task = ProjectTask(
        title=payload.title,
        status=payload.status,
        due_date=payload.due_date,
        team_id=payload.team_id,
        sort_order=payload.sort_order,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskRead.model_validate(task)


@router.get("/", response_model=list[TaskRead])
def list_tasks(team_id: int | None = None, db: Session = Depends(get_db)) -> list[TaskRead]:
    # Если передан team_id — возвращаем задачи только этой команды.
    stmt = select(ProjectTask).order_by(ProjectTask.created_at.desc())
    if team_id is not None:
        stmt = stmt.where(ProjectTask.team_id == team_id)
    tasks = db.execute(stmt).scalars().all()
    return [TaskRead.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)) -> TaskRead:
    task = db.execute(select(ProjectTask).where(ProjectTask.id == task_id)).scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskRead.model_validate(task)


@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> TaskRead:
    task = db.execute(select(ProjectTask).where(ProjectTask.id == task_id)).scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Полное обновление полей задачи (семантика PUT).
    task.title = payload.title
    task.status = payload.status
    task.due_date = payload.due_date
    task.sort_order = payload.sort_order
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> dict:
    task = db.execute(select(ProjectTask).where(ProjectTask.id == task_id)).scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}

