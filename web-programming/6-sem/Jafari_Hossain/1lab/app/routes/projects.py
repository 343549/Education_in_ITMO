from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.deps import get_current_user
from app.models.project import Project
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.schemas.domain import ProjectCreate, ProjectDetail, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects")


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    # Владелец проекта берётся из JWT (текущий пользователь), а не из тела запроса.
    project = Project(
        title=payload.title,
        description=payload.description,
        deadline=payload.deadline,
        owner_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectRead.model_validate(project)


@router.get("/", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)) -> list[ProjectRead]:
    projects = db.execute(select(Project).order_by(Project.created_at.desc())).scalars().all()
    return [ProjectRead.model_validate(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectDetail:
    # Загружаем проект сразу с вложенными связями:
    # teams -> memberships -> user и teams -> tasks.
    # Это нужно для корректного nested-ответа и чтобы избежать N+1 запросов.
    stmt = (
        select(Project)
        .options(
            selectinload(Project.teams)
            .selectinload(Team.memberships)
            .selectinload(TeamMembership.user),
            selectinload(Project.teams).selectinload(Team.tasks),
        )
        .where(Project.id == project_id)
    )
    project = db.execute(stmt).scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectDetail.model_validate(project)


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    project = db.execute(select(Project).where(Project.id == project_id)).scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != current_user.id:
        # Ограничение бизнес-логики: редактировать проект может только создатель.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can update project")

    project.title = payload.title
    project.description = payload.description
    project.deadline = payload.deadline
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectRead.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    project = db.execute(select(Project).where(Project.id == project_id)).scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != current_user.id:
        # Аналогично update: удаление доступно только владельцу.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can delete project")

    db.delete(project)
    db.commit()
    return {"detail": "Project deleted"}

