from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.skill import Skill
from app.schemas.domain import SkillCreate, SkillRead, SkillUpdate

router = APIRouter(prefix="/skills")


@router.post("/", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
def create_skill(payload: SkillCreate, db: Session = Depends(get_db)) -> SkillRead:
    existing = db.execute(select(Skill).where(Skill.name == payload.name)).scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Skill already exists")

    skill = Skill(name=payload.name)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return SkillRead.model_validate(skill)


@router.get("/", response_model=list[SkillRead])
def list_skills(db: Session = Depends(get_db)) -> list[SkillRead]:
    skills = db.execute(select(Skill).order_by(Skill.name)).scalars().all()
    return [SkillRead.model_validate(skill) for skill in skills]


@router.get("/{skill_id}", response_model=SkillRead)
def get_skill(skill_id: int, db: Session = Depends(get_db)) -> SkillRead:
    skill = db.execute(select(Skill).where(Skill.id == skill_id)).scalars().first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return SkillRead.model_validate(skill)


@router.put("/{skill_id}", response_model=SkillRead)
def update_skill(skill_id: int, payload: SkillUpdate, db: Session = Depends(get_db)) -> SkillRead:
    skill = db.execute(select(Skill).where(Skill.id == skill_id)).scalars().first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    skill.name = payload.name
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return SkillRead.model_validate(skill)


@router.delete("/{skill_id}", status_code=status.HTTP_200_OK)
def delete_skill(skill_id: int, db: Session = Depends(get_db)) -> dict:
    skill = db.execute(select(Skill).where(Skill.id == skill_id)).scalars().first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    db.delete(skill)
    db.commit()
    return {"detail": "Skill deleted"}

