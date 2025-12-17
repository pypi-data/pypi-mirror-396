"""
WebSocket机器人同步模块
基于websocket-client的同步WebSocket机器人实现
"""

from .ws_message import WebSocketMessage, WebSocketOperation, WebSocketConstants
from .ws_robot_client import WebSocketRobotClient
from .ws_robot_manager import WebSocketRobotManager
from .ws_robot_instance import WebSocketRobotInstance
from .ws_robot_use import WebSocketRobotUse
from .robot_api_body import RobotAPIBody

__all__ = [
    'WebSocketMessage',
    'WebSocketOperation', 
    'WebSocketConstants',
    'WebSocketRobotClient',
    'WebSocketRobotManager',
    'WebSocketRobotInstance',
    'WebSocketRobotUse',
    'RobotAPIBody'
]

__version__ = '1.0.0'
