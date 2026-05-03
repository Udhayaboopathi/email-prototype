from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from models.task import Task
from schemas.task import TaskCreate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse)
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = Task(user_id=user.id, title=payload.title, description=payload.description, due_at=payload.due_at)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return TaskResponse(id=row.id, user_id=row.user_id, title=row.title, description=row.description, due_at=row.due_at, completed=row.completed)


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await db.scalars(select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc()))
    return [TaskResponse(id=row.id, user_id=row.user_id, title=row.title, description=row.description, due_at=row.due_at, completed=row.completed) for row in rows]
