import uuid
from datetime import datetime, timezone
from typing import Generic, Optional
from typing import TypeVar

from pydantic import BaseModel, Field, ConfigDict

from xll_kit.schemas.common import ListData

T = TypeVar("T")


# =============================
# Meta
# =============================
class ResponseMeta(BaseModel):
    """附加元信息，可扩展 trace_id、timestamp 等"""
    trace_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="请求追踪 ID"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="响应时间"
    )


# =============================
# StandardResponse[T]
# =============================
class StandardResponse(BaseModel, Generic[T]):
    """通用响应结构"""
    code: int = Field(0, description="业务状态码，0 表示成功")
    message: str = Field("success", description="提示信息")
    data: Optional[T] = Field(None, description="业务数据体")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="元信息")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    # 成功返回（带数据）
    @staticmethod
    def ok(data: Optional[T] = None, message: str = "success"):
        return StandardResponse(code=0, message=message, data=data)

    # 成功返回（列表类）
    @staticmethod
    def ok_list(items, total: int, page: int, size: int):
        return StandardResponse(
            data=ListData(
                items=items,
                total=total,
                page=page,
                size=size,
            )
        )

    # 错误返回
    @staticmethod
    def error(message: str, code: int = 1):
        return StandardResponse(code=code, message=message, data=None)


# =============================
# Pagination
# =============================
class Pagination(BaseModel):
    total: int
    page: int
    size: int


# =============================
# Token Response
# =============================
class TokenResponse(BaseModel):
    """Token 响应模型"""
    access_token: str
    token_type: str
    expires_in: int


# =============================
# Message Response
# =============================
class MessageResponse(BaseModel):
    message: str


# =============================
# ErrorResponse
# =============================
class ErrorResponse(BaseModel):
    detail: str
