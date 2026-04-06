from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.deps import get_current_user
from app.models.project import Project
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.schemas.domain import (
    TeamCreate,
    TeamDetail,
    TeamMembershipCreate,
    TeamMembershipUpdate,
    TeamRead,
    TeamUpdate,
)

router = APIRouter(prefix="/teams")


@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(payload: TeamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TeamRead:
    # Команда должна быть привязана к существующему проекту.
    project = db.execute(select(Project).where(Project.id == payload.project_id)).scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    team = Team(name=payload.name, project_id=payload.project_id)
    db.add(team)
    db.commit()
    db.refresh(team)

    # Создатель автоматически становится owner-команды.
    membership = TeamMembership(team_id=team.id, user_id=current_user.id, role="owner")
    db.add(membership)
    db.commit()
    return TeamRead.model_validate(team)


@router.get("/", response_model=list[TeamRead])
def list_teams(project_id: int | None = None, db: Session = Depends(get_db)) -> list[TeamRead]:
    # Поддерживаем фильтрацию по project_id для удобного просмотра команд проекта.
    stmt = select(Team).order_by(Team.created_at.desc())
    if project_id is not None:
        stmt = stmt.where(Team.project_id == project_id)
    teams = db.execute(stmt).scalars().all()
    return [TeamRead.model_validate(team) for team in teams]


@router.get("/{team_id}", response_model=TeamDetail)
def get_team(team_id: int, db: Session = Depends(get_db)) -> TeamDetail:
    # Возвращаем команду с вложенными участниками и задачами.
    stmt = (
        select(Team)
        .options(
            selectinload(Team.memberships).selectinload(TeamMembership.user),
            selectinload(Team.tasks),
        )
        .where(Team.id == team_id)
    )
    team = db.execute(stmt).scalars().first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return TeamDetail.model_validate(team)


@router.put("/{team_id}", response_model=TeamRead)
def update_team(team_id: int, payload: TeamUpdate, db: Session = Depends(get_db)) -> TeamRead:
    team = db.execute(select(Team).where(Team.id == team_id)).scalars().first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    team.name = payload.name
    db.add(team)
    db.commit()
    db.refresh(team)
    return TeamRead.model_validate(team)


@router.delete("/{team_id}", status_code=status.HTTP_200_OK)
def delete_team(team_id: int, db: Session = Depends(get_db)) -> dict:
    team = db.execute(select(Team).where(Team.id == team_id)).scalars().first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    db.delete(team)
    db.commit()
    return {"detail": "Team deleted"}


@router.post("/{team_id}/members", status_code=status.HTTP_201_CREATED)
def add_team_member(team_id: int, payload: TeamMembershipCreate, db: Session = Depends(get_db)) -> dict:
    team = db.execute(select(Team).where(Team.id == team_id)).scalars().first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    user = db.execute(select(User).where(User.id == payload.user_id)).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = db.execute(
        select(TeamMembership).where(TeamMembership.team_id == team_id, TeamMembership.user_id == payload.user_id)
    ).scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already in team")

    membership = TeamMembership(team_id=team_id, user_id=payload.user_id, role=payload.role)
    db.add(membership)
    db.commit()
    return {"detail": "Member added"}


@router.patch("/{team_id}/members/{user_id}", status_code=status.HTTP_200_OK)
def update_team_member_role(
    team_id: int,
    user_id: int,
    payload: TeamMembershipUpdate,
    db: Session = Depends(get_db),
) -> dict:
    # Изменяем роль участника в ассоциативной сущности TeamMembership.
    membership = db.execute(
        select(TeamMembership).where(TeamMembership.team_id == team_id, TeamMembership.user_id == user_id)
    ).scalars().first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")

    membership.role = payload.role
    db.add(membership)
    db.commit()
    return {"detail": "Member role updated"}


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_200_OK)
def remove_team_member(team_id: int, user_id: int, db: Session = Depends(get_db)) -> dict:
    membership = db.execute(
        select(TeamMembership).where(TeamMembership.team_id == team_id, TeamMembership.user_id == user_id)
    ).scalars().first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    db.delete(membership)
    db.commit()
    return {"detail": "Member removed"}

