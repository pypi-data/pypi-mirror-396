"""FastAPI应用主程序入口"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
from async_pybatis_orm.base.connection import DatabaseManager
from async_pybatis_orm.base.common_model import CommonModel
from async_pybatis_orm.fields import Field, PrimaryKey
from async_pybatis_orm.wrapper.query_wrapper import QueryWrapper
from async_pybatis_orm.pagination.page import Page


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行

    try:
        # 初始化数据库连接
        print("正在初始化数据库连接...")
        await DatabaseManager.initialize(
            database_url="mysql+aiomysql://root:123456@localhost/sakila"
        )
        print("数据库连接初始化成功")

        print(
            "Async PyBatis ORM Example启动成功，接口文档地址：http://127.0.0.1:8000/docs"
        )
        yield

    finally:
        # 关闭时执行
        print("正在关闭应用...")

        # 关闭数据库连接
        await DatabaseManager.close()
        print("应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="Async PyBatis ORM Example",
    version="1.0.0",
    lifespan=lifespan,
)


# ==================== ORM 模型（用于数据库操作）====================


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


# ==================== Pydantic 模型（用于 API 请求/响应）====================


class ActorCreate(BaseModel):
    """创建演员请求模型"""

    first_name: str
    last_name: str

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
            }
        }


class ActorUpdate(BaseModel):
    """更新演员请求模型"""

    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Smith",
            }
        }


class ActorResponse(BaseModel):
    """演员响应模型"""

    model_config = ConfigDict(from_attributes=True)

    actor_id: int
    first_name: str
    last_name: str
    last_update: datetime


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# ==================== Actor CRUD 接口 ====================


@app.post("/actors", status_code=201)
async def create_actor(actor_data: ActorCreate):
    """创建演员（新增）"""
    # 将 Pydantic 模型转换为 ORM 模型
    actor = Actor(**actor_data.model_dump())
    await Actor.save(actor)
    # 将 ORM 模型转换为响应模型
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

    # 将 ORM 模型列表转换为响应模型列表
    return page_result.records


@app.put("/actors/{actor_id}")
async def update_actor(actor_id: int, actor_data: ActorUpdate):
    """更新演员（根据ID更新）"""
    # 先查询现有数据
    actor = await Actor.select_by_id(actor_id)
    if actor is None:
        raise HTTPException(status_code=404, detail="Actor not found")

    # 更新字段（只更新提供的字段）
    update_dict = actor_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(actor, key, value)

    # 执行更新
    affected_rows = await Actor.update_by_id(actor)
    if affected_rows == 0:
        raise HTTPException(status_code=404, detail="Actor not found")

    # 返回更新后的数据
    updated_actor = await Actor.select_by_id(actor_id)
    return updated_actor.to_json()


@app.delete("/actors/{actor_id}", status_code=204)
async def delete_actor(actor_id: int):
    """删除演员（根据ID删除）"""
    affected_rows = await Actor.remove_by_id(actor_id)
    if affected_rows == 0:
        raise HTTPException(status_code=404, detail="Actor not found")
    return None


class DeleteActorsRequest(BaseModel):
    """批量删除请求模型"""

    actor_ids: List[int]


@app.delete("/actors/batch", status_code=204)
async def delete_actors_by_ids(request: DeleteActorsRequest):
    """批量删除演员（根据ID列表批量删除）"""
    affected_rows = await Actor.remove_by_ids(request.actor_ids)
    if affected_rows == 0:
        raise HTTPException(status_code=404, detail="No actors found")
    return None


# ==================== 事务示例 ====================


class BatchCreateActorsRequest(BaseModel):
    """批量创建演员请求模型"""

    actors: List[ActorCreate]

    class Config:
        json_schema_extra = {
            "example": {
                "actors": [
                    {"first_name": "John", "last_name": "Doe"},
                    {"first_name": "Jane", "last_name": "Smith"},
                ]
            }
        }


@app.post("/actors/batch-transaction", status_code=201)
async def batch_create_actors_with_transaction(request: BatchCreateActorsRequest):
    """
    批量创建演员（事务示例 - 成功提交）

    在事务中批量创建多个演员，如果所有操作都成功，则提交事务。
    如果任何操作失败，则自动回滚所有操作。
    """
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
        # 这里捕获异常是为了返回友好的错误信息
        # 实际上事务已经在异常发生时自动回滚了
        raise HTTPException(
            status_code=500,
            detail=f"批量创建失败，事务已回滚: {str(e)}",
        )


@app.post("/actors/batch-transaction-rollback", status_code=201)
async def batch_create_actors_with_rollback(request: BatchCreateActorsRequest):
    """
    批量创建演员（事务示例 - 演示回滚）

    这个接口会故意触发一个错误来演示事务回滚。
    即使部分操作成功，当发生错误时，所有操作都会被回滚。
    """
    database = DatabaseManager.get_adapter()
    created_actors = []

    try:
        # 开启事务
        async with database.transaction():
            # 在事务中执行多个操作
            for i, actor_data in enumerate(request.actors):
                actor = Actor(**actor_data.model_dump())
                await Actor.save(actor)
                created_actors.append(actor)

                # 故意在第二个演员后触发错误，演示回滚
                if i == 1:
                    raise ValueError(
                        "模拟业务错误：第二个演员创建后触发异常，事务将回滚"
                    )

            # 如果执行到这里，说明所有操作都成功，事务会自动提交

        return {
            "message": "批量创建成功",
            "count": len(created_actors),
            "actors": [actor.to_dict() for actor in created_actors],
        }
    except ValueError as e:
        # 捕获我们故意抛出的错误
        # 此时事务已经自动回滚，所有操作都被撤销
        raise HTTPException(
            status_code=400,
            detail={
                "message": "事务已回滚",
                "error": str(e),
                "rollback_count": len(created_actors),
                "note": "即使已创建了部分演员，由于事务回滚，所有操作都已撤销",
            },
        )
    except Exception as e:
        # 捕获其他异常
        raise HTTPException(
            status_code=500,
            detail=f"批量创建失败，事务已回滚: {str(e)}",
        )


@app.post("/actors/transfer-transaction")
async def transfer_actor_name(
    source_id: int = Query(..., description="源演员ID"),
    target_id: int = Query(..., description="目标演员ID"),
    rollback: bool = Query(False, description="是否触发回滚（用于演示）"),
):
    """
    事务示例：转移演员名字

    在一个事务中执行多个操作：
    1. 读取源演员的名字
    2. 更新目标演员的名字
    3. 更新源演员的名字

    如果 rollback=True，会在操作后故意触发错误来演示回滚。
    """
    database = DatabaseManager.get_adapter()

    # 先检查演员是否存在（在事务外）
    source_actor = await Actor.select_by_id(source_id)
    if source_actor is None:
        raise HTTPException(status_code=404, detail="源演员不存在")

    target_actor = await Actor.select_by_id(target_id)
    if target_actor is None:
        raise HTTPException(status_code=404, detail="目标演员不存在")

    try:
        async with database.transaction():
            # 保存原始值（用于返回）
            original_source_name = source_actor.first_name
            original_target_name = target_actor.first_name

            # 交换名字
            temp_name = source_actor.first_name
            source_actor.first_name = target_actor.first_name
            target_actor.first_name = temp_name

            # 更新数据库
            await Actor.update_by_id(source_actor)
            await Actor.update_by_id(target_actor)

            # 如果设置了 rollback，故意触发错误
            if rollback:
                raise ValueError("演示回滚：所有更新操作将被撤销")

            # 如果执行到这里，事务会自动提交

        return {
            "message": "名字转移成功，事务已提交",
            "source_actor": {
                "id": source_actor.actor_id,
                "original_name": original_source_name,
                "new_name": source_actor.first_name,
            },
            "target_actor": {
                "id": target_actor.actor_id,
                "original_name": original_target_name,
                "new_name": target_actor.first_name,
            },
        }
    except ValueError as e:
        # 捕获我们故意抛出的错误
        raise HTTPException(
            status_code=400,
            detail={
                "message": "事务已回滚",
                "error": str(e),
                "note": "所有更新操作已被撤销，数据库状态未改变",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"操作失败，事务已回滚: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "fastapi_app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
