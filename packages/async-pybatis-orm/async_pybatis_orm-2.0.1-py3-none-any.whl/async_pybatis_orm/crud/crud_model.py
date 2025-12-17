#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRUD 模型集成

将所有的 Mixin 功能组合在一起，提供完整的 MyBatis-Plus 风格 CRUD 功能
"""

from ..base.base_model import BaseModel
from .select_mixin import SelectMixin
from .insert_mixin import InsertMixin
from .update_mixin import UpdateMixin
from .delete_mixin import DeleteMixin


class CRUDModel(BaseModel, SelectMixin, InsertMixin, UpdateMixin, DeleteMixin):
    """完整的 CRUD 模型类：包含完整的增删改查能力

    组合所有 Mixin 功能，提供 MyBatis-Plus 风格的完整 CRUD API

    功能包括：
    - 查询：select_by_id, select_one, select_list, select_page 等
    - 插入：save, insert, insert_batch 等
    - 更新：update_by_id, update_by_wrapper, update_batch_by_id 等
    - 删除：remove_by_id, remove_by_ids, remove_by_wrapper 等

    Example:
        ```python
        # 定义用户模型
        class User(CRUDModel):
            id: int = PrimaryKey(auto_increment=True)
            username: str = Field(column_name="user_name", max_length=50)
            email: Optional[str] = Field(nullable=True)
            created_at: datetime = Field(default_factory=datetime.now)

            __table_meta__ = {"table_name": "users", "primary_key": "id"}

            @classmethod
            async def _execute_query(cls, sql: str, params: dict = None, sql_type: str = "query"):
                # 实现具体的数据库执行逻辑
                database = cls.get_database()

                if sql_type == "query":
                    return await database.fetch_all(sql, params)
                elif sql_type == "count":
                    return await database.fetch_val(sql, params)
                elif sql_type in ["insert", "update", "delete"]:
                    return await database.execute(sql, params)
                else:
                    return await database.fetch_all(sql, params)

        # 使用示例
        async def user_crud_examples():
            # 保存（插入新实体）
            user = User(username="alice", email="alice@example.com")
            await User.save(user)

            # 查询
            user = await User.select_by_id(user.id)
            # 或者使用别名方法
            user = await User.get_by_id(user.id)

            # 更新
            user.username = "alice_updated"
            await User.update_by_id(user)

            # 条件查询
            wrapper = QueryWrapper().eq('username', 'alice').like('email', '@gmail.com')
            users = await User.select_list(wrapper)
            # 或者使用别名方法
            users = await User.list_by_condition(wrapper)

            # 分页查询
            page = Page(current=1, size=10)
            result = await User.select_page(page, wrapper)
            # 或者使用别名方法
            result = await User.page_query(page, wrapper)

            # 批量操作
            users = [
                User(username="user1", email="user1@example.com"),
                User(username="user2", email="user2@example.com")
            ]
            await User.insert_batch(users)

            # 批量更新
            for user in users:
                user.status = "active"
            await User.update_batch_by_id(users)

            # 删除
            await User.remove_by_id(1)
            await User.remove_by_ids([1, 2, 3])
        ```
    """

    pass
