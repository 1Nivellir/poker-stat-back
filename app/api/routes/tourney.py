from typing import Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.models import TorneyCreate, TorneyRead, Torney, TorneyUpdate
from app.api.deps import SessionDep, CurrentUser
import app.crud as crud
from uuid import UUID
from sqlmodel import select
router = APIRouter(prefix="/tournaments", tags=["Турниры"])

@router.post("/", response_model=TorneyRead)
def create_tournament(tournament: TorneyCreate, db: SessionDep, current_user: CurrentUser):
    # Создаем турнир от имени текущего пользователя
    db_tournament = Torney.model_validate(tournament, update={"user_id": current_user.id})
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament

@router.put('/{tourney_id}', response_model=TorneyRead)
def update_tournament(
    tourney_id: UUID, 
    tournament: TorneyUpdate, 
    db: SessionDep,
    current_user: CurrentUser
):
    # Получаем турнир из базы
    db_tournament = db.get(Torney, tourney_id)
    if not db_tournament:
        raise HTTPException(status_code=404, detail="Турнир не найден")
    
    # Проверяем права доступа - можно редактировать только свои турниры
    if str(db_tournament.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Нет прав для редактирования этого турнира")
   
    # Получаем данные для обновления (исключая unset поля)
    update_data = tournament.model_dump(exclude_unset=True)
    db_tournament.sqlmodel_update(update_data)
    
    # Обновляем время изменения
    db_tournament.updated_at = datetime.now(timezone.utc)
    
    # Сохраняем изменения
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    
    return db_tournament

@router.delete("/{tourney_id}")
def remove_tournament(tourney_id: UUID, db: SessionDep, current_user: CurrentUser):
    tournament = db.get(Torney, tourney_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Турнир не найден")
    
    # Проверяем права доступа - можно удалять только свои турниры
    if str(tournament.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Нет прав для удаления этого турнира")
    
    db.delete(tournament)
    db.commit()
    
    return {"message": "Турнир успешно удален", "status_code": 200}

@router.get('/my_tourney/', response_model=list[TorneyRead])
def get_my_tournaments(
    db: SessionDep,
    current_user: CurrentUser,
    start_date: datetime | None = None,
    end_date: datetime | None = None
):
    """
    Получить турниры текущего пользователя.
    Если даты не указаны, возвращает турниры за сегодня.
    """
    # Базовый запрос - все турниры пользователя
    query = select(Torney).where(Torney.user_id == current_user.id)
    
    # Применяем фильтры по датам
    if start_date and end_date:
        # Фильтр по промежутку
        query = query.where(Torney.play_date >= start_date, Torney.play_date <= end_date)
    elif start_date:
        # Все турниры после start_date
        query = query.where(Torney.play_date >= start_date)
    elif end_date:
        # Все турниры до end_date включительно
        query = query.where(Torney.play_date <= end_date)
    else:
        # Если даты не указаны - возвращаем турниры за сегодня
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start.replace(hour=23, minute=59, second=59, microsecond=999999)
        query = query.where(Torney.play_date >= today_start, Torney.play_date <= today_end)
    
    # Выполняем запрос
    tournaments = db.exec(query).all()
    
    # Сортируем по дате проведения (новые сначала)
    tournaments.sort(key=lambda x: x.play_date if x.play_date else datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    
    return tournaments