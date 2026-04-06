from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.deps import get_current_user
from app.db.session import get_db
from app.models.skill import Skill
from app.models.user import User
from app.models.user_skill import UserSkill
from app.security import verify_password, hash_password
from app.schemas.domain import UserSkillUpsert
from app.schemas.users import ChangePasswordRequest, UserProfile, UserPublic

router = APIRouter(prefix="/users")


@router.get("/", response_model=list[UserPublic])
def list_users(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)) -> list[UserPublic]:
    # Пагинация списка пользователей:
    # - limit: сколько вернуть
    # - offset: с какой позиции
    limit = min(max(limit, 1), 200)
    stmt = select(User).offset(offset).limit(limit)
    users = db.execute(stmt).scalars().all()
    return [
        UserPublic(id=u.id, email=u.email, full_name=u.full_name, created_at=u.created_at) for u in users
    ]


@router.get("/me", response_model=UserPublic)
def get_me(current_user: User = Depends(get_current_user)) -> UserPublic:
    # Возвращаем данные текущего пользователя, полученного из JWT.
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
    )


@router.get("/me/profile", response_model=UserProfile)
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> UserProfile:
    stmt = (
        select(User)
        .options(selectinload(User.user_skills).selectinload(UserSkill.skill))
        .where(User.id == current_user.id)
    )
    user = db.execute(stmt).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserProfile.model_validate(user)


@router.put("/me/skills", status_code=status.HTTP_200_OK)
def upsert_my_skill(
    payload: UserSkillUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    skill = db.execute(select(Skill).where(Skill.id == payload.skill_id)).scalars().first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    user_skill = db.execute(
        select(UserSkill).where(UserSkill.user_id == current_user.id, UserSkill.skill_id == payload.skill_id)
    ).scalars().first()

    if user_skill:
        user_skill.proficiency = payload.proficiency
        action = "updated"
    else:
        user_skill = UserSkill(user_id=current_user.id, skill_id=payload.skill_id, proficiency=payload.proficiency)
        db.add(user_skill)
        action = "created"

    db.commit()
    return {"detail": f"User skill {action}"}


@router.delete("/me/skills/{skill_id}", status_code=status.HTTP_200_OK)
def delete_my_skill(skill_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    user_skill = db.execute(
        select(UserSkill).where(UserSkill.user_id == current_user.id, UserSkill.skill_id == skill_id)
    ).scalars().first()
    if not user_skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User skill not found")

    db.delete(user_skill)
    db.commit()
    return {"detail": "User skill deleted"}


@router.post("/me/change-password", status_code=status.HTTP_200_OK)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    # Смена пароля:
    # - проверяем текущий пароль
    # - обновляем hashed_password
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    current_user.hashed_password = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()

    return {"detail": "Password changed successfully"}

