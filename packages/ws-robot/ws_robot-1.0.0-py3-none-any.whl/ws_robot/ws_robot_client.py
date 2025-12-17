"""
WebSocket机器人客户端 - 同步版本
基于websocket-client的同步WebSocket客户端实现
"""

import json
import uuid
import time
import threading
import logging
from typing import Dict, List, Optional, Any, Callable
from websocket import WebSocketApp
from typing import TYPE_CHECKING

from .ws_message import WebSocketMessage, WebSocketOperation

if TYPE_CHECKING:
    from .ws_robot_instance import WebSocketRobotInstance


class WebSocketRobotClient:
    """WebSocket机器人客户端 - 同步版本"""
    
    def __init__(self, ws_url: str, username: str = "niki", password: str = "test", 
                 logger: Optional[logging.Logger] = None, timeout: int = 30,
                 auto_reconnect: bool = True, max_reconnect_attempts: int = 5, 
                 reconnect_interval: int = 5, reconnect_backoff_factor: float = 1.5):
        """
        初始化WebSocket客户端
        
        Args:
            ws_url: WebSocket服务器地址
            username: 用户名
            password: 密码
            logger: 日志记录器
            timeout: 请求超时时间（秒）
            auto_reconnect: 是否自动重连
            max_reconnect_attempts: 最大重连尝试次数
            reconnect_interval: 重连间隔（秒）
            reconnect_backoff_factor: 重连退避因子
        """
        self.ws_url = ws_url
        self.username = username
        self.password = password
        self.logger = logger or logging.getLogger(__name__)
        self.timeout = timeout
        
        # 重连配置
        self.auto_reconnect = auto_reconnect
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_interval = reconnect_interval
        self.reconnect_backoff_factor = reconnect_backoff_factor
        self._reconnect_attempts = 0
        self._reconnect_timer = None
        
        # 连接状态
        self.ws = None
        self.connected = False
        self.sessionKey = None
        self._last_connect_time = 0
        
        # 消息处理
        self.pending_requests = {}  # requestId -> (event, response)
        self.message_handlers = {}  # operation -> handler
        self._lock = threading.Lock()
        
        # 机器人管理
        self.robots = {}  # robot_id -> WebSocketRobotInstance
        
        # 线程管理
        self._ws_thread = None
        self._stop_event = threading.Event()
        self._reconnect_thread = None
    
    def connect(self, reconnect_window: int = 30) -> bool:
        """
        连接到WebSocket服务器
        
        Args:
            reconnect_window: 重连时间窗口（秒）
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 构建连接URL
            connect_url = f"{self.ws_url}?reconnectWindow={reconnect_window}"
            if self.sessionKey:
                connect_url += f"&sessionKey={self.sessionKey}"
            
            self.logger.info(f"Connecting to WebSocket server: {connect_url}")
            
            # 创建WebSocket连接
            self.ws = WebSocketApp(
                connect_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # 启动WebSocket线程
            self._stop_event.clear()
            self._ws_thread = threading.Thread(target=self._run_websocket, daemon=True)
            self._ws_thread.start()
            
            # 等待连接建立
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < self.timeout:
                time.sleep(0.1)
            
            if self.connected:
                self.logger.info(f"Connected to WebSocket server: {self.ws_url}")
                self._reconnect_attempts = 0  # 重置重连计数
                self._last_connect_time = time.time()
                return True
            else:
                self.logger.error("Failed to connect to WebSocket server: timeout")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket server: {e}")
            return False
    
    def disconnect(self):
        """断开WebSocket连接"""
        try:
            self.connected = False
            self.auto_reconnect = False  # 禁用自动重连
            self._stop_event.set()
            
            if self.ws:
                self.ws.close()
            
            if self._ws_thread and self._ws_thread.is_alive():
                self._ws_thread.join(timeout=5)
            
            if self._reconnect_thread and self._reconnect_thread.is_alive():
                self._reconnect_thread.join(timeout=2)
            
            # 清理待处理的请求
            with self._lock:
                for requestId, (event, response) in self.pending_requests.items():
                    event.set()
                self.pending_requests.clear()
            
            self.logger.info("Disconnected from WebSocket server")
            
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
    
    def _run_websocket(self):
        """运行WebSocket连接"""
        try:
            self.ws.run_forever()
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            self.connected = False
    
    def _on_open(self, ws):
        """WebSocket连接打开回调"""
        self.connected = True
        self.logger.info("WebSocket connection opened")
    
    def _on_message(self, ws, message):
        """WebSocket消息接收回调"""
        try:
            data = json.loads(message)
            self.logger.debug(f"Received message: {data}")
            msg = WebSocketMessage.from_dict(data)
            
            # 处理响应消息
            with self._lock:
                if msg.requestId in self.pending_requests:
                    self.logger.debug(f"Found pending request for {msg.requestId}, setting event")
                    event, response_container = self.pending_requests.pop(msg.requestId)
                    response_container[0] = msg
                    event.set()
                    return
                else:
                    self.logger.debug(f"No pending request found for {msg.requestId}")
            
            # 处理其他消息（如重连响应）
            if msg.operation == WebSocketOperation.RECONNECT.value:
                if msg.is_success():
                    self.sessionKey = msg.response.get('sessionKey')
                    self.logger.info(f"Reconnected successfully, sessionKey: {self.sessionKey}")
            
            # 调用注册的消息处理器
            if msg.operation in self.message_handlers:
                handler = self.message_handlers[msg.operation]
                try:
                    handler(msg)
                except Exception as e:
                    self.logger.error(f"Error in message handler for {msg.operation}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
    
    def _on_error(self, ws, error):
        """WebSocket错误回调"""
        self.logger.error(f"WebSocket error: {error}")
        self.connected = False
        self._trigger_reconnect()
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭回调"""
        self.logger.warning(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        self.connected = False
        self._trigger_reconnect()
    
    def _trigger_reconnect(self):
        """触发自动重连"""
        if not self.auto_reconnect or self._stop_event.is_set():
            return
        
        # 检查是否已经达到最大重连次数
        if self._reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached. Giving up.")
            return
        
        # 检查是否已经有重连线程在运行
        if self._reconnect_thread and self._reconnect_thread.is_alive():
            return
        
        # 启动重连线程
        self._reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True)
        self._reconnect_thread.start()
    
    def _reconnect_loop(self):
        """重连循环"""
        while (self.auto_reconnect and 
               not self._stop_event.is_set() and 
               self._reconnect_attempts < self.max_reconnect_attempts):
            
            self._reconnect_attempts += 1
            
            # 计算重连延迟（指数退避）
            delay = self.reconnect_interval * (self.reconnect_backoff_factor ** (self._reconnect_attempts - 1))
            
            self.logger.info(f"Attempting to reconnect ({self._reconnect_attempts}/{self.max_reconnect_attempts}) in {delay:.1f} seconds...")
            
            # 等待重连延迟
            if self._stop_event.wait(delay):
                break  # 如果收到停止信号，退出重连
            
            # 尝试重连
            if self._attempt_reconnect():
                self.logger.info("Reconnected successfully!")
                return
            else:
                time.sleep(1)
                self.logger.warning(f"Reconnection attempt {self._reconnect_attempts} failed")
        
        if self._reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.error("All reconnection attempts failed. Connection lost.")
    
    def _attempt_reconnect(self) -> bool:
        """尝试重连"""
        try:
            
            # 重新创建连接
            connect_url = f"{self.ws_url}?reconnectWindow=30"
            if self.sessionKey:
                connect_url += f"&sessionKey={self.sessionKey}"
            
            self.ws = WebSocketApp(
                connect_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # 启动新的WebSocket线程
            self._ws_thread = threading.Thread(target=self._run_websocket, daemon=True)
            self._ws_thread.start()
            
            # 等待连接建立
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < self.timeout:
                time.sleep(0.1)
            
            if self.connected:
                self._last_connect_time = time.time()
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Reconnection attempt failed: {e}")
            return False
    
    def _send_message(self, message: WebSocketMessage) -> WebSocketMessage:
        """发送消息并等待响应"""
        if not self.connected or not self.ws:
            raise ConnectionError("WebSocket not connected")
        
        # 创建事件和响应容器
        event = threading.Event()
        response_container = [None]
        
        with self._lock:
            self.pending_requests[message.requestId] = (event, response_container)
        
        try:
            # 发送消息
            message_dict = message.to_dict()
            self.logger.debug(f"Sending message: {message_dict}")
            self.ws.send(json.dumps(message_dict))
            
            # 等待响应
            self.logger.debug(f"Waiting for response to request {message.requestId}")
            if event.wait(timeout=self.timeout):
                self.logger.debug(f"Received response for request {message.requestId}")
                return response_container[0]
            else:
                self.logger.error(f"Timeout waiting for response to request {message.requestId}")
                raise TimeoutError(f"Request timeout after {self.timeout} seconds")
                
        except Exception as e:
            with self._lock:
                self.pending_requests.pop(message.requestId, None)
            raise e
    
    def register_message_handler(self, operation: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[operation] = handler
    
    # ========== 基础操作 ==========
    
    def preallocate_resources(self, robot_count: int, user: str, type: str = None, ip: any = None) -> Dict[str, Any]:
        """
        预分配资源
        
        Args:
            robot_count: 需要预分配的robot数量
            user: 用户标识
            type: robot类型（可选，如：docker、stress等）。如果不指定，默认使用docker类型
            ip: 指定的IP地址（可选），可以是单个IP字符串或IP数组。如果不指定，系统会自动选择可用IP
            
        Returns:
            Dict: 预分配结果，包含sessionKey等信息
            
        Raises:
            Exception: 如果预分配失败，抛出异常
            
        注意：
            - 不指定type和ip：默认使用docker类型的IP进行分配
            - 只指定type：只使用指定类型的IP进行分配
            - 只指定ip：使用指定的IP进行分配（可以是单个IP或IP列表）
            - 同时指定type和ip：系统会验证每个IP的类型是否与指定的type匹配
        """
        requestId = f"prealloc_{uuid.uuid4().hex[:8]}"
        
        # 构建请求数据
        data = {
            "robotCount": robot_count, 
            "user": user
        }
        
        # 添加可选参数
        if type is not None:
            data["type"] = type
            
        if ip is not None:
            data["ip"] = ip
        
        message = WebSocketMessage.create_request(
            WebSocketOperation.PREALLOCATE,
            requestId,
            data
        )
        
        response = self._send_message(message)
        if response.is_success():
            self.sessionKey = response.response.get('sessionKey')
            return response.response
        else:
            raise Exception(f"Preallocation failed: {response.error}")
    
    def create_robot(self, robot_data: Dict[str, Any]) -> 'WebSocketRobotInstance':
        """创建机器人"""
        requestId = f"create_{uuid.uuid4().hex[:8]}"
        message = WebSocketMessage.create_request(
            WebSocketOperation.CREATE_ROBOT,
            requestId,
            robot_data
        )
        
        response = self._send_message(message)
        if response.is_success():
            robot_id = response.response.get('robotId')
            from .ws_robot_instance import WebSocketRobotInstance
            robot = WebSocketRobotInstance(self, robot_id, robot_data)
            self.robots[robot_id] = robot
            return robot
        else:
            raise Exception(f"Robot creation failed: {response.error}")
    
    def query_robots(self, sessionKey: str = None) -> List[Dict[str, Any]]:
        """查询机器人列表"""
        requestId = f"query_robots_{uuid.uuid4().hex[:8]}"
        data = {"sessionKey": sessionKey} if sessionKey else {}
        message = WebSocketMessage.create_request(
            WebSocketOperation.QUERY_ROBOTS,
            requestId,
            data
        )
        
        response = self._send_message(message)
        if response.is_success():
            return response.response.get('data', [])
        else:
            raise Exception(f"Query robots failed: {response.error}")
    
    def query_sessions(self, sessionKey: str = None) -> List[Dict[str, Any]]:
        """查询会话列表"""
        requestId = f"query_sessions_{uuid.uuid4().hex[:8]}"
        data = {"sessionKey": sessionKey} if sessionKey else {}
        message = WebSocketMessage.create_request(
            WebSocketOperation.QUERY_SESSIONS,
            requestId,
            data
        )
        
        response = self._send_message(message)
        if response.is_success():
            return response.response.get('data', [])
        else:
            raise Exception(f"Query sessions failed: {response.error}")
    
    def cleanup_session(self, sessionKey: str = None) -> bool:
        """清理会话"""
        requestId = f"cleanup_{uuid.uuid4().hex[:8]}"
        data = {"sessionKey": sessionKey or self.sessionKey}
        message = WebSocketMessage.create_request(
            WebSocketOperation.CLEANUP_SESSION,
            requestId,
            data
        )
        
        response = self._send_message(message)
        return response.is_success()
    
    def force_cleanup(self, sessionKey: str = None) -> bool:
        """强制清理"""
        requestId = f"force_cleanup_{uuid.uuid4().hex[:8]}"
        data = {"sessionKey": sessionKey or self.sessionKey}
        message = WebSocketMessage.create_request(
            WebSocketOperation.FORCE_CLEANUP,
            requestId,
            data
        )
        
        response = self._send_message(message)
        return response.is_success()
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        requestId = f"status_{uuid.uuid4().hex[:8]}"
        message = WebSocketMessage.create_request(
            WebSocketOperation.GET_STATUS,
            requestId,
            {}
        )
        
        response = self._send_message(message)
        if response.is_success():
            return response.response
        else:
            raise Exception(f"Get status failed: {response.error}")
    
    def reconnect(self, sessionKey: str, reconnect_window: int = 30) -> bool:
        """重连到指定会话"""
        requestId = f"reconnect_{uuid.uuid4().hex[:8]}"
        message = WebSocketMessage.create_request(
            WebSocketOperation.RECONNECT,
            requestId,
            {"sessionKey": sessionKey, "reconnectWindow": reconnect_window}
        )
        
        response = self._send_message(message)
        if response.is_success():
            self.sessionKey = response.response.get('sessionKey')
            return True
        else:
            raise Exception(f"Reconnect failed: {response.error}")
    
    # ========== 便捷方法 ==========
    
    def get_robot(self, robot_id: str) -> Optional['WebSocketRobotInstance']:
        """获取机器人实例"""
        return self.robots.get(robot_id)
    
    def get_all_robots(self) -> List['WebSocketRobotInstance']:
        """获取所有机器人实例"""
        return list(self.robots.values())
    
    def remove_robot(self, robot_id: str) -> Optional['WebSocketRobotInstance']:
        """移除机器人实例"""
        return self.robots.pop(robot_id, None)
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.connected and self.ws is not None
    
    def get_sessionKey(self) -> Optional[str]:
        """获取会话键"""
        return self.sessionKey
    
    # ========== 重连管理方法 ==========
    
    def enable_auto_reconnect(self):
        """启用自动重连"""
        self.auto_reconnect = True
        self.logger.info("Auto-reconnect enabled")
    
    def disable_auto_reconnect(self):
        """禁用自动重连"""
        self.auto_reconnect = False
        self.logger.info("Auto-reconnect disabled")
    
    def reset_reconnect_attempts(self):
        """重置重连尝试次数"""
        self._reconnect_attempts = 0
        self.logger.info("Reconnect attempts reset")
    
    def get_reconnect_status(self) -> Dict[str, Any]:
        """获取重连状态信息"""
        return {
            "auto_reconnect": self.auto_reconnect,
            "reconnect_attempts": self._reconnect_attempts,
            "max_reconnect_attempts": self.max_reconnect_attempts,
            "reconnect_interval": self.reconnect_interval,
            "reconnect_backoff_factor": self.reconnect_backoff_factor,
            "last_connect_time": self._last_connect_time,
            "is_reconnecting": self._reconnect_thread and self._reconnect_thread.is_alive()
        }
    
    def force_reconnect(self) -> bool:
        """强制重连"""
        self.logger.info("Force reconnecting...")
        self.connected = False
        self.reset_reconnect_attempts()
        return self._attempt_reconnect()
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
