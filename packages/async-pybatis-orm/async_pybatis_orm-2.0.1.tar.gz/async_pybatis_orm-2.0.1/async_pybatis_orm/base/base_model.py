#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础模型类

提供表元数据管理、数据库连接注入、字段映射等核心功能
对齐 MyBatis-Plus 的 BaseEntity 设计理念
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime, date, time
from decimal import Decimal
from typing import (
    get_type_hints,
    get_origin,
    get_args,
    Any,
    Optional,
    Dict,
    Union,
    Type,
    List,
    TypeVar,
    TYPE_CHECKING,
)

from .abstracts import AbstractDatabase
from .global_config import GlobalConfig

if TYPE_CHECKING:
    from ..wrapper.query_wrapper import QueryWrapper

T = TypeVar("T", bound="BaseModel")


class BaseModel(ABC):
    """基础模型类，依赖注入数据库连接

    提供 MyBatis-Plus 风格的模型基类，支持：
    - 自动字段映射（字段名转列名）
    - 数据库连接注入
    - 类型转换和序列化
    - 表元数据管理
    """

    # 类级别配置
    _table_meta: Dict[str, Any] = {"table_name": "", "primary_key": "id"}
    _database: Optional[AbstractDatabase] = None
    _fields: Dict[str, Any] = {}  # 缓存字段信息

    def __init_subclass__(cls, **kwargs):
        """子类初始化时自动设置字段和表元数据"""
        super().__init_subclass__(**kwargs)

        # 获取字段信息
        cls._fields = cls._get_fields()
        cls._table_meta = cls._get_table_meta()

        # 自动设置数据库连接（如果全局配置存在）
        if cls._database is None and GlobalConfig.is_configured():
            from .database_manager import DatabaseManager

            cls._database = DatabaseManager.get_database()

    def __init__(self, **kwargs):
        """初始化模型对象，自动设置默认值"""
        # 保障 _fields 存在且为字典
        cls = self.__class__
        if getattr(cls, "_fields", None) is None:
            cls._fields = cls._get_fields()

        # 遍历所有字段，设置默认值或用户提供的值
        for field_name, field_info in cls._fields.items():
            if field_name in kwargs:
                # 用户提供了值，使用用户的值
                value = kwargs[field_name]
                # 反序列化值
                setattr(
                    self,
                    field_name,
                    self._deserialize_value(value, field_info["type"], field_name),
                )
            else:
                # 用户没有提供值，使用默认值
                default_value = self._get_default_value(field_info)
                setattr(self, field_name, default_value)

    @classmethod
    def _get_fields(cls) -> Dict[str, Any]:
        """获取模型字段信息"""
        fields = {}

        # 1. 获取类型注解
        annotations = get_type_hints(cls)

        # 2. 获取字段默认值
        defaults = {}
        for name in annotations.keys():
            if hasattr(cls, name):
                defaults[name] = getattr(cls, name)

        # 3. 构建字段信息
        for name, annotation in annotations.items():
            field_info = cls._build_field_info(name, annotation, defaults.get(name))
            fields[name] = field_info

        # 剔除掉无用字段
        fields.pop("_table_meta", None)
        fields.pop("_database", None)
        fields.pop("_fields", None)
        return fields

    @classmethod
    def _build_field_info(
        cls, name: str, annotation: Any, default_value: Any
    ) -> Dict[str, Any]:
        """构建字段信息"""
        field_info = {
            "name": name,
            "type": annotation,
            "default": default_value,
            "is_optional": False,
            "is_primary_key": False,
            "is_auto_increment": False,
            "column_name": name,
            "nullable": True,
            "auto_update": False,
        }

        # 处理 Optional 类型
        if get_origin(annotation) is Union:
            args = get_args(annotation)
            if len(args) == 2 and type(None) in args:
                field_info["is_optional"] = True
                field_info["nullable"] = True
                # 获取非 None 的类型
                non_none_type = next(t for t in args if t is not type(None))
                field_info["type"] = non_none_type

        # default_value 为自定义字段
        if default_value is not None:
            # 正常情况下 每一个字段必须设置列名
            if not hasattr(default_value, "column_name"):
                # 如果没有设置列名，使用字段名
                field_info["column_name"] = field_info.get("column_name")
                field_info["auto_update"] = getattr(default_value, "auto_update", False)
            elif hasattr(default_value, "field_type"):
                # 自定义字段类型
                field_info["field_type"] = default_value.field_type
                field_info["column_name"] = getattr(default_value, "column_name", name)
                field_info["is_primary_key"] = (
                    getattr(default_value, "field_type", None).value == "primary_key"
                )
                field_info["is_auto_increment"] = getattr(
                    default_value, "auto_increment", False
                )
                field_info["default_factory"] = getattr(
                    default_value, "default_factory", None
                )
                field_info["nullable"] = getattr(default_value, "nullable", True)
                # 重要：保存原始字段对象的 default 值
                field_info["field_default"] = getattr(default_value, "default", None)
                field_info["auto_update"] = getattr(default_value, "auto_update", False)
            else:
                field_info["default"] = default_value

        return field_info

    @classmethod
    def _get_table_meta(cls) -> Dict[str, Any]:
        """获取表元数据"""
        return getattr(cls, "__table_meta__", {})

    @classmethod
    def set_database(cls, database: AbstractDatabase):
        """设置数据库连接（类级别）"""
        cls._database = database

    @classmethod
    def get_database(cls) -> AbstractDatabase:
        """获取数据库连接，确保已初始化"""
        if cls._database is None:
            raise RuntimeError("数据库连接未初始化，请先调用 set_database()")
        return cls._database

    @classmethod
    def get_table_name(cls) -> str:
        """获取表名"""
        return cls._table_meta["table_name"]

    @classmethod
    def get_primary_key(cls) -> str:
        """获取主键字段名"""
        return cls._table_meta["primary_key"]

    @classmethod
    def _get_column_name(cls, field_name: str) -> str:
        """获取字段对应的数据库列名"""
        if getattr(cls, "_fields", None) is None:
            cls._fields = cls._get_fields()
        field_info = cls._fields.get(field_name)
        if field_info and "column_name" in field_info and field_info["column_name"]:
            return field_info["column_name"]
        return field_name

    @classmethod
    def _get_model_fields(cls) -> List[str]:
        """获取模型字段列表"""
        if getattr(cls, "_fields", None) is None:
            cls._fields = cls._get_fields()
        return list(cls._fields.keys())

    @classmethod
    def _get_default_value(cls, field_info: Dict[str, Any]) -> Any:
        """获取字段的默认值"""
        # 1. 使用 default_factory
        if "default_factory" in field_info and field_info["default_factory"]:
            return field_info["default_factory"]()

        # 2. 优先使用字段对象的 default 值（如 PrimaryKey 的 default）
        if "field_default" in field_info:
            return field_info["field_default"]

        # 3. 返回 None
        return None

    @classmethod
    def _build_where_sql(cls: Type[T], wrapper: Optional["QueryWrapper"]) -> tuple:
        """构建 WHERE 语句与参数

        委托给 QueryWrapper.build_where_clause，按模型字段到列名的映射生成 SQL 及绑定参数。
        """
        if not wrapper:
            return "", {}
        return wrapper.build_where_clause(cls)

    def to_dict(
        self, exclude_none: bool = False, exclude_unset: bool = False
    ) -> Dict[str, Any]:
        """将模型对象转换为字典

        Args:
            exclude_none: 是否排除 None 值
            exclude_unset: 是否排除未设置的字段（使用默认值的字段）

        Returns:
            Dict[str, Any]: 字典格式的数据
        """
        result = {}

        cls = self.__class__
        fields = getattr(cls, "_fields", None) or {}

        for field_name, field_info in fields.items():
            # 获取字段值
            value = getattr(self, field_name, None)

            # 处理排除逻辑
            if exclude_none and value is None:
                continue

            if exclude_unset and value == field_info.get("default"):
                continue

            result[field_name] = value

        return result

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any], from_db: bool = False) -> T:
        """从字典创建模型对象

        Args:
            data: 字典数据
            from_db: 数据是否来自数据库（键为列名）。为 True 时做列名→字段名转换；默认 False 不转换。

        Returns:
            BaseModel: 模型实例
        """
        # 确保字段缓存已就绪
        if getattr(cls, "_fields", None) is None:
            cls._fields = cls._get_fields()

        # 创建实例
        instance = cls.__new__(cls)

        # 如来自数据库，先将列名映射为字段名
        if from_db:
            col_to_field = {}
            for fname, finfo in cls._fields.items():
                col_to_field[finfo.get("column_name", fname)] = fname
            mapped = {}
            if not type(data) is dict:
                data = dict(data)
            for k, v in data.items():
                mapped[col_to_field.get(k, k)] = v
            data = mapped

        # 处理字段数据
        processed_data = {}
        for field_name, field_info in cls._fields.items():
            if field_name in data:
                # 数据中提供了该字段
                value = data[field_name]
                # 反序列化值
                processed_data[field_name] = cls._deserialize_value(
                    value, field_info["type"], field_name
                )
            else:
                # 数据中没有提供该字段，使用默认值
                processed_data[field_name] = cls._get_default_value(field_info)

        # 设置属性
        for field_name, value in processed_data.items():
            setattr(instance, field_name, value)

        return instance  # type: ignore[return-value]

    @classmethod
    def _deserialize_value(cls, value: Any, field_type: Any, field_name: str) -> Any:
        """反序列化字段值"""
        if value is None:
            return None

        # 处理 Optional 类型
        if get_origin(field_type) is Union:
            args = get_args(field_type)
            if len(args) == 2 and type(None) in args:
                non_none_type = next(t for t in args if t is not type(None))
                return cls._deserialize_value(value, non_none_type, field_name)

        # 处理 datetime 类型
        if field_type == datetime:
            if isinstance(value, str):
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            return value

        # 处理 date 类型
        if field_type == date:
            if isinstance(value, str):
                return date.fromisoformat(value)
            return value

        # 处理 time 类型
        if field_type == time:
            if isinstance(value, str):
                return time.fromisoformat(value)
            return value

        # 处理 Decimal 类型
        if field_type == Decimal:
            return Decimal(str(value))

        # 处理基本类型
        if field_type in (int, float, str, bool):
            try:
                return field_type(value)
            except (ValueError, TypeError):
                return value

        return value

    def to_json(
        self,
        exclude_none: bool = False,
        exclude_unset: bool = False,
        ensure_ascii: bool = False,
        indent: Optional[int] = None,
    ) -> str:
        """将模型对象转换为 JSON 字符串"""
        data = self.to_dict(exclude_none=exclude_none, exclude_unset=exclude_unset)

        # 自定义序列化函数
        def custom_serializer(obj):
            if isinstance(obj, datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(obj, date):
                return obj.strftime("%Y-%m-%d")
            elif isinstance(obj, time):
                return obj.strftime("%H:%M:%S")
            elif isinstance(obj, Decimal):
                return float(obj)
            else:
                return str(obj)

        return json.dumps(
            data, ensure_ascii=ensure_ascii, indent=indent, default=custom_serializer
        )

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """从 JSON 字符串创建模型对象"""
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")

    @abstractmethod
    async def _fetch_all(
        cls: Type[T], sql: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """执行查询语句（对应数据库驱动的 fetch_all）"""
        pass

    @abstractmethod
    async def _execute(
        cls: Type[T],
        sql: str,
        params: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None,
    ) -> int:
        """执行变更语句（对应数据库驱动的 execute），返回受影响行数"""
        pass
