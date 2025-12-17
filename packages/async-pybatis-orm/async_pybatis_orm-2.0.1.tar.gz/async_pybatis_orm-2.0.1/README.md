# async-pybatis-orm

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/async-pybatis-orm.svg)](https://pypi.org/project/async-pybatis-orm/)

一个基于 MySQL 异步场景，对齐 MyBatis-Plus 语法风格的 Python ORM 框架。专注于易用性与可扩展性，为从 Java MyBatis-Plus 转过来的开发者提供熟悉的 API。

## ✨ 特性

- 🚀 **异步优先**: 基于 `asyncio` 和 `aiomysql`，支持高并发异步操作
- 🎯 **MyBatis-Plus 风格**: API 设计完全对齐 Java MyBatis-Plus，降低学习成本
- 🔧 **灵活配置**: 支持多种数据库配置方式和连接池管理
- 📦 **模块化设计**: 采用 Mixin 模式，按需组合功能
- 🛡️ **类型安全**: 完整的类型注解支持，IDE 友好
- 📄 **分页支持**: 内置分页查询，支持复杂条件查询
- 🔍 **条件构造器**: 链式条件拼接，支持复杂查询逻辑
- ⚡ **批量操作**: 支持批量插入、更新、删除操作

## 📦 安装

```bash
pip install async-pybatis-orm
```

## 🚀 快速集成 FastAPI

### 1. 安装依赖

```bash
pip install async-pybatis-orm fastapi uvicorn
```

### 2. 初始化数据库连接

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from async_pybatis_orm.base.connection import DatabaseManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    try:
        # 初始化数据库连接
        await DatabaseManager.initialize(
            database_url="mysql+aiomysql://root:123456@localhost/sakila"
        )
        yield
    finally:
        # 关闭数据库连接
        await DatabaseManager.close()

app = FastAPI(lifespan=lifespan)
```

### 3. 定义 ORM 模型

**注意**：在 FastAPI 应用中，推荐使用 `CommonModel`，它已经集成了数据库连接管理。

```python
from datetime import datetime
from typing import Optional
from async_pybatis_orm.base.common_model import CommonModel
from async_pybatis_orm.fields import Field, PrimaryKey

class Actor(CommonModel):
    """演员表模型（ORM模型，用于数据库操作）"""

    __table_meta__ = {"table_name": "actor", "primary_key": "actor_id"}

    actor_id: Optional[int] = PrimaryKey(
        column_name="actor_id", auto_increment=True, nullable=True
    )
    first_name: str = Field(column_name="first_name", nullable=False, max_length=45)
    last_name: str = Field(column_name="last_name", nullable=False, max_length=45)
    last_update: datetime = Field(
        column_name="last_update",
        default_factory=datetime.now,
        auto_update=True,
        nullable=False,
    )
```

**模型类型说明：**

- `CommonModel`: 推荐用于 FastAPI 等 Web 应用，自动使用 `DatabaseManager` 管理的数据库连接
- `CRUDModel`: 基础 CRUD 模型，需要手动实现 `_execute_query` 方法或设置数据库连接

### 4. 定义 Pydantic 模型（用于 API 请求/响应）

**重要**：ORM 模型（`CommonModel`）不能直接用于 FastAPI 的请求/响应验证，需要创建独立的 Pydantic 模型。

```python
from pydantic import BaseModel, ConfigDict

class ActorCreate(BaseModel):
    """创建演员请求模型"""
    first_name: str
    last_name: str

class ActorUpdate(BaseModel):
    """更新演员请求模型"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class ActorResponse(BaseModel):
    """演员响应模型"""
    model_config = ConfigDict(from_attributes=True)

    actor_id: int
    first_name: str
    last_name: str
    last_update: datetime
```

**为什么需要分离？**

- ORM 模型（`CommonModel`）继承自 `ABC`，不是 Pydantic 模型，无法用于 FastAPI 的自动验证
- Pydantic 模型用于 API 层的请求验证和响应序列化
- ORM 模型用于数据库操作，在业务逻辑层进行转换，ORM 模型支持 to_json（将模型转换为 json 字符串）, to_dict (将模型转换为 dict 字典)

### 5. 实现 CRUD 接口

```python
from fastapi import HTTPException, Query
from async_pybatis_orm.wrapper.query_wrapper import QueryWrapper
from async_pybatis_orm.pagination.page import Page

@app.post("/actors", status_code=201)
async def create_actor(actor_data: ActorCreate):
    """创建演员（新增）"""
    # 将 Pydantic 模型转换为 ORM 模型
    actor = Actor(**actor_data.model_dump())
    await Actor.save(actor)
    return actor.to_json()

@app.get("/actors")
async def list_actors(
    first_name: Optional[str] = Query(None, description="名字"),
    last_name: Optional[str] = Query(None, description="姓氏"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """查询演员列表（条件查询 + 分页）"""
    wrapper = QueryWrapper()

    if first_name:
        wrapper.like("first_name", first_name)
    if last_name:
        wrapper.like("last_name", last_name)

    # 分页查询
    page_obj = Page(current=page, size=size)
    page_result = await Actor.select_page(page_obj, wrapper)

    return page_result.records

@app.put("/actors/{actor_id}")
async def update_actor(actor_id: int, actor_data: ActorUpdate):
    """更新演员（根据ID更新）"""
    actor = await Actor.select_by_id(actor_id)
    if actor is None:
        raise HTTPException(status_code=404, detail="Actor not found")

    # 更新字段（只更新提供的字段）
    update_dict = actor_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(actor, key, value)

    await Actor.update_by_id(actor)
    return await Actor.select_by_id(actor_id)

@app.delete("/actors/{actor_id}", status_code=204)
async def delete_actor(actor_id: int):
    """删除演员（根据ID删除）"""
    affected_rows = await Actor.remove_by_id(actor_id)
    if affected_rows == 0:
        raise HTTPException(status_code=404, detail="Actor not found")
    return None
```

### 6. 事务支持示例

```python
from async_pybatis_orm.base.connection import DatabaseManager

@app.post("/actors/batch-transaction", status_code=201)
async def batch_create_actors_with_transaction(request: BatchCreateActorsRequest):
    """批量创建演员（事务示例 - 成功提交）"""
    database = DatabaseManager.get_adapter()
    created_actors = []

    try:
        # 开启事务
        async with database.transaction():
            # 在事务中执行多个操作
            for actor_data in request.actors:
                actor = Actor(**actor_data.model_dump())
                await Actor.save(actor)
                created_actors.append(actor)
            # 如果所有操作都成功，事务会自动提交
            # 如果发生异常，事务会自动回滚

        return {
            "message": "批量创建成功，事务已提交",
            "count": len(created_actors),
            "actors": [actor.to_dict() for actor in created_actors],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"批量创建失败，事务已回滚: {str(e)}",
        )
```

## 🔧 数据库配置

### FastAPI 应用中的数据库初始化

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from async_pybatis_orm.base.connection import DatabaseManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    try:
        # 初始化数据库连接
        await DatabaseManager.initialize(
            database_url="mysql+aiomysql://root:123456@localhost/sakila"
        )
        print("数据库连接初始化成功")
        yield
    finally:
        # 关闭数据库连接
        await DatabaseManager.close()
        print("数据库连接已关闭")

app = FastAPI(lifespan=lifespan)
```

### 数据库连接 URL 格式

```
mysql+aiomysql://用户名:密码@主机:端口/数据库名

示例：
mysql+aiomysql://root:123456@localhost:3306/sakila
mysql+aiomysql://user:pass@127.0.0.1:3306/test_db
```

## 📚 核心组件

### 字段类型

```python
from async_pybatis_orm import Field, PrimaryKey, String, Integer, Boolean, DateTime, Float

class Product(CRUDModel):
    id: int = PrimaryKey(auto_increment=True)
    name: str = String(max_length=100, nullable=False)
    price: float = Float(precision=10, scale=2)
    is_active: bool = Boolean(default=True)
    created_at: datetime = DateTime(auto_now_add=True)
    updated_at: datetime = DateTime(auto_now=True)
```

### 条件构造器

BaseWrapper 提供通用方法，QueryWrapper、UpdateWrapper 继承了 BaseWrapper

```python
from async_pybatis_orm import QueryWrapper

# 创建查询条件构造器（支持链式调用）
wrapper = QueryWrapper()

# ==================== 比较条件 ====================
wrapper.eq(Actor.status, 'active')           # 等于 (=)
wrapper.ne(Actor.status, 'inactive')         # 不等于 (!=)
wrapper.gt(Actor.age, 18)                    # 大于 (>)
wrapper.ge(Actor.age, 18)                    # 大于等于 (>=)
wrapper.lt(Actor.age, 65)                    # 小于 (<)
wrapper.le(Actor.age, 65)                    # 小于等于 (<=)

# ==================== 模糊查询 ====================
wrapper.like(Actor.name, 'admin')            # 模糊查询（包含，%admin%）
wrapper.not_like(Actor.name, 'test')         # 不包含模糊查询（NOT LIKE %test%）
wrapper.like_left(Actor.name, 'admin')       # 左模糊查询（%admin）
wrapper.like_right(Actor.name, 'admin')      # 右模糊查询（admin%）

# ==================== 范围查询 ====================
wrapper.in_list(Actor.id, [1, 2, 3])        # IN 查询
wrapper.not_in(Actor.id, [4, 5, 6])         # NOT IN 查询
wrapper.between(Actor.age, 18, 65)           # BETWEEN 查询
wrapper.not_between(Actor.age, 0, 17)        # NOT BETWEEN 查询

# ==================== NULL 查询 ====================
wrapper.is_null('deleted_at')            # IS NULL
wrapper.is_not_null('updated_at')        # IS NOT NULL

# ==================== 排序和分组 ====================
wrapper.order_by(Actor.created_at, desc=True)   # 降序排序
wrapper.order_by(Actor.id, desc=False)         # 升序排序
wrapper.group_by(Actor.status)                 # 分组

# ==================== 字段选择 ====================
wrapper.select('id', 'name', 'email')    # 指定查询字段（可多次调用追加）

# ==================== 原始 SQL 片段 ====================
wrapper.last('LIMIT 10 OFFSET 20')      # 直接拼接 SQL 片段（谨慎使用）

# ==================== 链式调用示例 ====================
wrapper = QueryWrapper() \
    .eq('status', 'active') \
    .like('name', 'admin') \
    .gt('created_at', '2023-01-01') \
    .in_list('id', [1, 2, 3]) \
    .order_by('created_at', desc=True) \
    .order_by('id', desc=False)

# 使用条件构造器查询
actors = await Actor.select_list(wrapper)
```

**UpdateWrapper 更新条件构造器：**

```python
from async_pybatis_orm.wrapper.query_wrapper import UpdateWrapper

# 创建更新条件构造器
update_wrapper = UpdateWrapper()

# 设置更新字段
update_wrapper.set(Actor.status, 'active')           # 设置字段值
update_wrapper.set_sql(Actor.age, 'age + 1')         # 使用 SQL 表达式
update_wrapper.set_sql(Actor.updated_at, 'NOW()')   # 使用 SQL 函数

# 添加更新条件
update_wrapper.eq('id', 1)                      # WHERE id = 1
update_wrapper.like('name', 'test')             # AND name LIKE '%test%'

# 执行更新
affected_rows = await Actor.update_by_wrapper(update_wrapper)
```

wrapper 支持字段名和模型字段名，如：wrapper.set('status', 'active') 和 wrapper.set(User.status, 'active') 效果相同，这样可以避免手动转换字段名。方便后面字段名修改重构。

### 分页组件

```python
from async_pybatis_orm import Page, PageResult, PageHelper

# 创建分页参数
page = Page(current=1, size=10)

# 执行分页查询
result: PageResult = await User.page_query(page, wrapper)

# 分页结果属性
print(f"总记录数: {result.total}")
print(f"当前页: {result.current}")
print(f"页大小: {result.size}")
print(f"总页数: {result.pages}")
print(f"是否有下一页: {result.has_next}")
print(f"是否有上一页: {result.has_prev}")
print(f"记录列表: {result.records}")
```

## 🎯 支持的 CRUD 方法

### 基础 CRUD 方法

| 方法名                 | 说明         | MyBatis-Plus 对应    |
| ---------------------- | ------------ | -------------------- |
| `save(entity)`         | 保存实体     | `save(entity)`       |
| `get_by_id(id)`        | 根据 ID 查询 | `getById(id)`        |
| `update_by_id(entity)` | 根据 ID 更新 | `updateById(entity)` |
| `remove_by_id(id)`     | 根据 ID 删除 | `removeById(id)`     |
| `list_all()`           | 查询所有     | `list()`             |

### 条件查询方法

| 方法名                       | 说明         | MyBatis-Plus 对应     |
| ---------------------------- | ------------ | --------------------- |
| `select_by_id(id)`           | 根据 ID 查询 | `getById(id)`         |
| `select_one(wrapper)`        | 查询单个     | `getOne(wrapper)`     |
| `select_list(wrapper)`       | 条件查询列表 | `list(wrapper)`       |
| `select_count(wrapper)`      | 条件查询总数 | `count(wrapper)`      |
| `select_page(page, wrapper)` | 分页查询     | `page(page, wrapper)` |

### 批量操作方法

| 方法名                       | 说明             | MyBatis-Plus 对应           |
| ---------------------------- | ---------------- | --------------------------- |
| `batch_save(entities)`       | 批量保存         | `saveBatch(entities)`       |
| `batch_update(entities)`     | 批量更新         | `updateBatchById(entities)` |
| `remove_by_ids(ids)`         | 根据 ID 批量删除 | `removeByIds(ids)`          |
| `remove_by_wrapper(wrapper)` | 根据条件批量删除 | `remove(wrapper)`           |

## 🔍 高级特性

### 1. 模型序列化

```python
# 转换为字典
user_dict = user.to_dict(exclude_none=True)

# 转换为JSON
user_json = user.to_json(exclude_none=True, indent=2)

# 从字典创建
user = User.from_dict({"username": "alice", "email": "alice@example.com"})

# 从JSON创建
user = User.from_json('{"username": "alice", "email": "alice@example.com"}')
```

### 3. 事务支持

```python
from async_pybatis_orm.base.connection import DatabaseManager

async def transaction_example():
    """事务示例"""
    database = DatabaseManager.get_adapter()

    try:
        async with database.transaction():
            # 在事务中执行多个操作
            actor1 = Actor(first_name="John", last_name="Doe")
            await Actor.save(actor1)

            actor2 = Actor(first_name="Jane", last_name="Smith")
            await Actor.save(actor2)

            # 如果所有操作都成功，事务会自动提交
            # 如果发生异常，事务会自动回滚
    except Exception as e:
        print(f"事务失败，已回滚: {e}")
```

**事务回滚示例：**

```python
@app.post("/actors/batch-transaction-rollback")
async def batch_create_with_rollback(request: BatchCreateActorsRequest):
    """演示事务回滚"""
    database = DatabaseManager.get_adapter()

    try:
        async with database.transaction():
            for i, actor_data in enumerate(request.actors):
                actor = Actor(**actor_data.model_dump())
                await Actor.save(actor)

                # 故意在第二个演员后触发错误
                if i == 1:
                    raise ValueError("模拟业务错误，事务将回滚")
    except ValueError as e:
        # 此时事务已经自动回滚，所有操作都被撤销
        raise HTTPException(
            status_code=400,
            detail={"message": "事务已回滚", "error": str(e)}
        )
```

## 📋 完整 FastAPI 示例

完整示例代码请查看 `examples/fastapi_app.py`，包含：

1. **数据库连接管理** - 使用 `lifespan` 管理应用生命周期
2. **ORM 模型定义** - 使用 `CommonModel` 定义数据库模型
3. **Pydantic 模型** - 分离请求/响应模型用于 API 验证
4. **完整 CRUD 接口** - 创建、查询、更新、删除操作
5. **条件查询和分页** - 使用 `QueryWrapper` 和 `Page`
6. **事务示例** - 包含成功提交和回滚演示

### 运行示例

```bash
# 1. 安装依赖
pip install async-pybatis-orm fastapi uvicorn

# 2. 确保数据库已创建并配置连接信息
# 编辑 examples/fastapi_app.py 中的数据库连接 URL

# 3. 运行应用
cd examples
python fastapi_app.py

# 4. 访问 API 文档
# Swagger UI: http://127.0.0.1:8000/docs
# ReDoc: http://127.0.0.1:8000/redoc
```

### 示例接口列表

- `POST /actors` - 创建演员
- `GET /actors` - 查询演员列表（支持条件查询和分页）
- `PUT /actors/{actor_id}` - 更新演员
- `DELETE /actors/{actor_id}` - 删除演员
- `DELETE /actors/batch` - 批量删除演员
- `POST /actors/batch-transaction` - 批量创建（事务示例）
- `POST /actors/batch-transaction-rollback` - 批量创建（回滚演示）
- `POST /actors/transfer-transaction` - 名字交换（事务示例）

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢 [MyBatis-Plus](https://baomidou.com/) 提供的设计灵感
- 感谢 [SQLAlchemy](https://www.sqlalchemy.org/) 和 [Tortoise ORM](https://tortoise-orm.readthedocs.io/) 的参考

## 🏗️ 项目结构

```
async_pybatis_orm/
├── base/                    # 基础层
│   ├── base_model.py       # 基础模型类
│   ├── abstracts.py        # 抽象接口
│   ├── global_config.py    # 全局配置
│   └── database_manager.py # 数据库管理器
├── crud/                   # CRUD 功能层
│   ├── base_crud.py        # 基础 CRUD
│   ├── select_mixin.py     # 查询 Mixin
│   ├── insert_mixin.py     # 插入 Mixin
│   ├── update_mixin.py     # 更新 Mixin
│   └── delete_mixin.py     # 删除 Mixin
├── wrapper/                # 条件构造器
│   ├── base_wrapper.py     # 基础包装器
│   └── query_wrapper.py    # 查询包装器
├── pagination/             # 分页组件
│   ├── page.py            # 分页模型
│   ├── page_result.py     # 分页结果
│   └── page_helper.py     # 分页助手
├── fields.py              # 字段定义
├── exceptions.py          # 异常定义
└── utils/                 # 工具类
```

发布 PYPI 流程:

1. 修改 pyproject.toml 中的 version 号
2. windows cmd 运行 .\scripts\publish.bat

## 📞 支持

如果您在使用过程中遇到问题，请：

1. 查看 [文档](https://async-pybatis-orm.readthedocs.io)
2. 搜索 [Issues](https://github.com/zhonglunsheng/async-pybatis-orm/issues)
3. 创建新的 Issue

## 🤝 贡献者

感谢所有为这个项目做出贡献的开发者！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢 [MyBatis-Plus](https://baomidou.com/) 提供的设计灵感
- 感谢 [SQLAlchemy](https://www.sqlalchemy.org/) 和 [Tortoise ORM](https://tortoise-orm.readthedocs.io/) 的参考

---

**async-pybatis-orm** - 让 Python 异步 ORM 开发更简单！ 🚀

[![Star History Chart](https://api.star-history.com/svg?repos=zhonglunsheng/async-pybatis-orm&type=Date)](https://star-history.com/#zhonglunsheng/async-pybatis-orm&Date)
