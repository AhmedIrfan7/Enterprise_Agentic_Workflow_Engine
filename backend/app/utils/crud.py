from typing import Any, Generic, Type, TypeVar, Sequence
from sqlalchemy import select, update as sa_update, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class CRUDBase(Generic[ModelT]):
    def __init__(self, model: Type[ModelT]) -> None:
        self.model = model

    async def get(self, db: AsyncSession, record_id: str) -> ModelT | None:
        result = await db.execute(select(self.model).where(self.model.id == record_id))
        return result.scalars().first()

    async def list(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> Sequence[ModelT]:
        stmt = select(self.model)
        if filters:
            for field, value in filters.items():
                stmt = stmt.where(getattr(self.model, field) == value)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> ModelT:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, record_id: str, obj_in: dict[str, Any]) -> ModelT | None:
        await db.execute(
            sa_update(self.model).where(self.model.id == record_id).values(**obj_in)
        )
        await db.commit()
        return await self.get(db, record_id)

    async def delete(self, db: AsyncSession, *, record_id: str) -> bool:
        result = await db.execute(
            sa_delete(self.model).where(self.model.id == record_id)
        )
        await db.commit()
        return result.rowcount > 0
