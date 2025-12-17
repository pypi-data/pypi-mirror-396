"""
WebSocket消息模型 - 同步版本
基于数据模型设计文档的WebSocket消息格式
"""

import time
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class WebSocketOperation(Enum):
    """WebSocket操作类型枚举"""
    PREALLOCATE = "PREALLOCATE"           # 预分配资源
    CREATE_ROBOT = "CREATE_ROBOT"         # 创建机器人
    UPDATE_ROBOT = "UPDATE_ROBOT"         # 更新机器人
    DELETE_ROBOT = "DELETE_ROBOT"         # 删除机器人
    QUERY_SESSIONS = "QUERY_SESSIONS"     # 查询会话
    QUERY_ROBOTS = "QUERY_ROBOTS"         # 查询机器人
    CLEANUP_SESSION = "CLEANUP_SESSION"   # 清理会话
    FORCE_CLEANUP = "FORCE_CLEANUP"       # 强制清理
    GET_STATUS = "GET_STATUS"             # 获取状态
    RECONNECT = "RECONNECT"               # 重连


@dataclass
class WebSocketMessage:
    """WebSocket消息模型"""
    operation: str
    requestId: str  # 使用服务器期望的字段名
    data: Optional[Dict[str, Any]] = None
    statusCode: Optional[int] = None  # 使用服务器期望的字段名
    response: Optional[Any] = None
    error: Optional[str] = None
    timestamp: Optional[int] = None
    sessionKey: Optional[str] = None  # 使用服务器期望的字段名
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = int(time.time() * 1000)
    
    @classmethod
    def create_request(cls, operation: WebSocketOperation, requestId: str, data: Dict[str, Any] = None):
        """创建请求消息"""
        return cls(
            operation=operation.value,
            requestId=requestId,
            data=data or {}
        )
    
    @classmethod
    def create_response(cls, operation: WebSocketOperation, requestId: str, statusCode: int, response: Any = None):
        """创建响应消息"""
        return cls(
            operation=operation.value,
            requestId=requestId,
            statusCode=statusCode,
            response=response
        )
    
    @classmethod
    def create_error(cls, operation: WebSocketOperation, requestId: str, error: str, statusCode: int = 400):
        """创建错误消息"""
        return cls(
            operation=operation.value,
            requestId=requestId,
            statusCode=statusCode,
            error=error
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "operation": self.operation,
            "requestId": self.requestId,
            "data": self.data,
            "statusCode": self.statusCode,
            "response": self.response,
            "error": self.error,
            "timestamp": self.timestamp,
            "sessionKey": self.sessionKey
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketMessage':
        """从字典创建消息"""
        return cls(**data)
    
    def is_success(self) -> bool:
        """判断是否为成功响应"""
        return self.statusCode == 200
    
    def is_error(self) -> bool:
        """判断是否为错误响应"""
        return self.statusCode is not None and self.statusCode != 200


class WebSocketConstants:
    """WebSocket常量配置"""
    
    # 机器人操作相关常量
    ROBOT_API_PATH = "/v2/app/robots"
    
    # 默认请求头
    DEFAULT_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Basic bmlraTp0ZXN0"
    }
    
    # 查询过滤条件键名
    FILTER_USER = "user"
    FILTER_SESSION_KEY = "sessionKey"
    FILTER_STATUS = "status"
    FILTER_ROBOT_ID = "robotId"
    
    # 管理操作数据键名
    DATA_SESSION_KEY = "sessionKey"
    DATA_FORCE_CLEANUP = "forceCleanup"
    
    # 响应相关常量
    SUCCESS_CODE = 200
    ERROR_CODE = 400
    SUCCESS_STATUS = "success"
    ERROR_STATUS = "error"
    
    # 超时配置
    DEFAULT_TIMEOUT = 30  # 默认超时时间（秒）
    DEFAULT_RECONNECT_WINDOW = 300  # 默认重连时间窗口（秒）
