"""
WebSocket机器人管理器 - 同步版本
基于websocket-client的同步WebSocket机器人管理器实现
"""

from typing import Dict, List, Optional, Any
from .ws_robot_client import WebSocketRobotClient
from .ws_robot_instance import WebSocketRobotInstance
from .robot_api_body import RobotAPIBody


class WebSocketRobotManager:
    """WebSocket机器人管理器 - 同步版本"""
    
    def __init__(self, client: WebSocketRobotClient):
        """
        初始化机器人管理器
        
        Args:
            client: WebSocket客户端
        """
        self.client = client
        self.robots = {}  # robot_id -> WebSocketRobotInstance
        self.api_body = RobotAPIBody()
    
    def add_robot(self, robot_data: Dict[str, Any]) -> WebSocketRobotInstance:
        """
        添加机器人
        
        Args:
            robot_data: 机器人数据
            
        Returns:
            WebSocketRobotInstance: 机器人实例
        """
        robot = self.client.create_robot(robot_data)
        self.robots[robot.robot_id] = robot
        return robot
    
    def stop_robot(self, robot: WebSocketRobotInstance) -> bool:
        """
        停止机器人
        
        Args:
            robot: 机器人实例
            
        Returns:
            bool: 停止是否成功
        """
        try:
            success = robot.delete()
            if success and robot.robot_id in self.robots:
                del self.robots[robot.robot_id]
            return success
        except Exception as e:
            self.client.logger.error(f"Error stopping robot {robot.robot_id}: {e}")
            return False
    
    def stop_robot_by_id(self, robot_id: str) -> bool:
        """
        通过ID停止机器人
        
        Args:
            robot_id: 机器人ID
            
        Returns:
            bool: 停止是否成功
        """
        robot = self.robots.get(robot_id)
        if robot:
            return self.stop_robot(robot)
        else:
            self.client.logger.warning(f"Robot {robot_id} not found in manager")
            return False
    
    def stop_all_robots(self) -> int:
        """
        停止所有机器人
        
        Returns:
            int: 成功停止的机器人数量
        """
        robots_to_stop = list(self.robots.values())
        self.robots.clear()
        
        success_count = 0
        for robot in robots_to_stop:
            try:
                if robot.delete():
                    success_count += 1
            except Exception as e:
                self.client.logger.error(f"Error stopping robot {robot.robot_id}: {e}")
        
        return success_count
    
    def list_robots(self, user: str = None) -> List[Dict[str, Any]]:
        """
        列出所有机器人
        
        Args:
            user: 用户过滤（可选）
            
        Returns:
            List[Dict]: 机器人列表
        """
        return self.client.query_robots()
    
    def get_robot(self, robot_id: str) -> Optional[WebSocketRobotInstance]:
        """
        获取机器人实例
        
        Args:
            robot_id: 机器人ID
            
        Returns:
            Optional[WebSocketRobotInstance]: 机器人实例
        """
        return self.robots.get(robot_id)
    
    def get_all_robots(self) -> List[WebSocketRobotInstance]:
        """
        获取所有机器人实例
        
        Returns:
            List[WebSocketRobotInstance]: 机器人实例列表
        """
        return list(self.robots.values())
    
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
            
        使用规则：
            - 不指定type和ip：默认使用docker类型的IP进行分配
            - 只指定type：只使用指定类型的IP进行分配
            - 只指定ip：使用指定的IP进行分配（可以是单个IP或IP列表）
            - 同时指定type和ip：系统会验证每个IP的类型是否与指定的type匹配
            
        示例：
            # 基础预分配（默认使用docker类型）
            manager.preallocate_resources(5, "test_user")
            
            # 指定robot类型
            manager.preallocate_resources(10, "test_user", type="stress")
            
            # 指定单个IP
            manager.preallocate_resources(5, "test_user", ip="23.236.121.43")
            
            # 指定IP列表
            manager.preallocate_resources(10, "test_user", ip=["23.236.121.43", "23.236.121.44"])
            
            # 同时指定type和ip（会验证类型匹配）
            manager.preallocate_resources(5, "test_user", type="stress", ip=["23.236.121.43"])
        """
        return self.client.preallocate_resources(robot_count, user, type, ip)
    
    def cleanup_session(self, session_key: str = None) -> bool:
        """
        清理会话
        
        Args:
            session_key: 会话键（可选）
            
        Returns:
            bool: 清理是否成功
        """
        return self.client.cleanup_session(session_key)
    
    def force_cleanup(self, session_key: str = None) -> bool:
        """
        强制清理
        
        Args:
            session_key: 会话键（可选）
            
        Returns:
            bool: 清理是否成功
        """
        return self.client.force_cleanup(session_key)
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取系统状态
        
        Returns:
            Dict: 系统状态
        """
        return self.client.get_status()
    
    # ========== 批量操作 ==========
    
    def create_multiple_robots(self, robot_data_list: List[Dict[str, Any]]) -> List[WebSocketRobotInstance]:
        """
        批量创建机器人
        
        Args:
            robot_data_list: 机器人数据列表
            
        Returns:
            List[WebSocketRobotInstance]: 机器人实例列表
        """
        robots = []
        for robot_data in robot_data_list:
            try:
                robot = self.add_robot(robot_data)
                robots.append(robot)
            except Exception as e:
                self.client.logger.error(f"Failed to create robot: {e}")
        
        return robots
    
    def stop_multiple_robots(self, robot_ids: List[str]) -> int:
        """
        批量停止机器人
        
        Args:
            robot_ids: 机器人ID列表
            
        Returns:
            int: 成功停止的机器人数量
        """
        success_count = 0
        for robot_id in robot_ids:
            try:
                if self.stop_robot_by_id(robot_id):
                    success_count += 1
            except Exception as e:
                self.client.logger.error(f"Failed to stop robot {robot_id}: {e}")
        
        return success_count
    
    # ========== 统计信息 ==========
    
    def get_robot_count(self) -> int:
        """获取机器人数量"""
        return len(self.robots)
    
    def get_robot_ids(self) -> List[str]:
        """获取所有机器人ID"""
        return list(self.robots.keys())
    
    def is_empty(self) -> bool:
        """检查是否为空"""
        return len(self.robots) == 0
    
    def has_robot(self, robot_id: str) -> bool:
        """检查是否有指定机器人"""
        return robot_id in self.robots
    
    # ========== 便捷方法 ==========
    
    def mute_all_videos(self) -> int:
        """静音所有机器人的视频"""
        success_count = 0
        for robot in self.robots.values():
            try:
                robot.mute_video()
                success_count += 1
            except Exception as e:
                self.client.logger.error(f"Failed to mute video for robot {robot.robot_id}: {e}")
        
        return success_count
    
    def unmute_all_videos(self) -> int:
        """取消静音所有机器人的视频"""
        success_count = 0
        for robot in self.robots.values():
            try:
                robot.unmute_video()
                success_count += 1
            except Exception as e:
                self.client.logger.error(f"Failed to unmute video for robot {robot.robot_id}: {e}")
        
        return success_count
    
    def mute_all_audios(self) -> int:
        """静音所有机器人的音频"""
        success_count = 0
        for robot in self.robots.values():
            try:
                robot.mute_audio()
                success_count += 1
            except Exception as e:
                self.client.logger.error(f"Failed to mute audio for robot {robot.robot_id}: {e}")
        
        return success_count
    
    def unmute_all_audios(self) -> int:
        """取消静音所有机器人的音频"""
        success_count = 0
        for robot in self.robots.values():
            try:
                robot.unmute_audio()
                success_count += 1
            except Exception as e:
                self.client.logger.error(f"Failed to unmute audio for robot {robot.robot_id}: {e}")
        
        return success_count
    
    # ========== 上下文管理 ==========
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop_all_robots()
    
    def __str__(self) -> str:
        return f"WebSocketRobotManager(robots={len(self.robots)})"
    
    def __repr__(self) -> str:
        return self.__str__()
