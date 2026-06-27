from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Sequence
import uuid

from sqlalchemy import delete, select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

class BaseRepository(ABC):
    @abstractmethod
    def list(self):
        pass
    
    @abstractmethod
    def create(self, **kwargs):
        pass

    @abstractmethod
    def remove(self, *args):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass


class SqlAlchemyRepository(BaseRepository, Generic[T]):
    def __init__(self, session: AsyncSession, model: T):
        self.session = session
        self.model = model
    
    async def get_first(self, **kwargs) -> T:
        stmt = select(self.model).filter_by(**kwargs)
        return (await self.session.execute(stmt)).scalars().first()
    
    async def list(self, **kwargs) -> Sequence[T]:
        stmt = select(self.model).filter_by(**kwargs)
        return (await self.session.execute(stmt)).scalars().all()

    async def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance
    
    async def update(self, model_id: uuid.UUID, update_data: dict[str | Any]) -> Result[uuid.UUID]:
        return await self.session.execute(
            update(self.model).where(self.model.id == model_id).values(**update_data).returning(self.model.id)
        )
    
    async def remove(self, model_id: uuid.UUID) -> Result[uuid.UUID]:
        return await self.session.execute(
            delete(self.model).where(self.model.id == model_id).returning(self.model.id)
        )


def get_repository(session, model):
    return SqlAlchemyRepository(session, model)
