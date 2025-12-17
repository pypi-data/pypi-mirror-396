from ..crud.crud_model import CRUDModel
from .connection import DatabaseManager


class CommonModel(CRUDModel):
    """公共模型"""

    @classmethod
    async def _fetch_all(cls, sql: str, params: dict = None):
        cls._database = DatabaseManager.get_adapter()
        return await cls._database.fetch_all(sql, params or {})

    @classmethod
    async def _execute(cls, sql: str, params):
        cls._database = DatabaseManager.get_adapter()
        if type(params) == list:
            await cls._database.execute_many(sql, params or {})
            return len(params)
        return await cls._database.execute(sql, params or {})
