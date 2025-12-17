#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
更新操作 Mixin

提供 MyBatis-Plus 风格的 update、updateById 等方法
对齐 Java MyBatis-Plus 的 IService 接口
"""

from typing import List, TYPE_CHECKING, TypeVar
from ..base.base_model import BaseModel
from ..wrapper.query_wrapper import UpdateWrapper

if TYPE_CHECKING:
    pass

T = TypeVar("T", bound=BaseModel)

class UpdateMixin:
    """UPDATE 操作相关的 Mixin 类
    
    提供 MyBatis-Plus 风格的更新的方法：
    - update_by_id: 根据主键更新
    - update_by_wrapper: 根据条件更新
    - update_batch: 批量更新
    """

    # ==================== UPDATE 相关方法 ====================

    @classmethod
    async def update_by_id(cls: type[T], entity: T) -> bool:
        """根据主键更新记录
        
        对应 MyBatis-Plus 的 updateById(entity)
        
        Args:
            entity: 实体对象，必须包含主键值
            
        Returns:
            bool: 更新是否成功
            
        Example:
            ```python
            user = await User.get_by_id(1)
            user.username = "alice_updated"
            success = await User.update_by_id(user)
            ```
        """
        # 获取主键值
        primary_key_value = getattr(entity, cls._table_meta["primary_key"], None)
        if primary_key_value is None:
            raise ValueError(f"实体对象必须包含主键 {cls._table_meta['primary_key']} 的值")

        # 获取更新字段
        update_data = entity.to_dict(exclude_none=False, exclude_unset=False)

        # 移除主键字段
        update_data.pop(cls._table_meta["primary_key"], None)
        
        # 处理 auto_update 字段：强制刷新为 default_factory 值
        cls._apply_auto_update_fields(update_data)

        if not update_data:
            return True  # 没有需要更新的字段

        # 构建 UPDATE SQL
        set_clauses = []
        params = {}

        for field_name, value in update_data.items():
            column_name = cls._get_column_name(field_name)
            param_name = f"update_{field_name}"
            set_clauses.append(f"{column_name} = :{param_name}")
            params[param_name] = value

        primary_key_column = cls._get_column_name(cls._table_meta["primary_key"])
        sql = f"UPDATE {cls._table_meta['table_name']} SET {', '.join(set_clauses)} WHERE {primary_key_column} = :id"
        params["id"] = primary_key_value

        result = await cls._execute(sql, params)
        return result > 0


    @classmethod
    async def update_by_wrapper(cls: type[T], wrapper: UpdateWrapper) -> bool:
        """根据 UpdateWrapper 更新记录

        对应 MyBatis-Plus 的 update(wrapper)

        Args:
            wrapper: 更新条件构造器（UpdateWrapper）

        Returns:
            bool: 更新是否成功

        Example:
            ```python
            # 使用 UpdateWrapper
            wrapper = UpdateWrapper() \
                .eq('age', 30) \
                .set('status', 1) \
                .set('updated_at', datetime.now())
            success = await User.update_by_update_wrapper(wrapper)
            ```
        """
        # 构建 UPDATE SQL
        sql, params = wrapper.build_update_sql(cls)

        result = await cls._execute(sql, params)
        return result > 0

    @classmethod
    def _apply_auto_update_fields(cls: type[T], update_data: dict) -> None:
        """处理 auto_update 字段：强制刷新为 default_factory 值"""
        if getattr(cls, "_fields", None) is None:
            cls._fields = cls._get_fields()

        for field_name, field_info in cls._fields.items():
            if field_info.get("auto_update", False):
                # 获取 default_factory
                if "default_factory" in field_info:
                    update_data[field_name] = field_info["default_factory"]()