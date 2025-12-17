"""
WebSocket机器人实例 - 同步版本
基于websocket-client的同步WebSocket机器人实例实现
"""

import uuid
from typing import Dict, Any
from .ws_message import WebSocketMessage, WebSocketOperation
from .robot_api_body import RobotAPIBody


class WebSocketRobotInstance:
    """WebSocket机器人实例 - 同步版本"""
    
    def __init__(self, client, robot_id: str, robot_data: Dict[str, Any]):
        """
        初始化机器人实例
        
        Args:
            client: WebSocket客户端
            robot_id: 机器人ID
            robot_data: 机器人数据
        """
        self.client = client
        self.robot_id = robot_id
        self.robot_data = robot_data
        self.api_body = RobotAPIBody()
        # 从robot_data中提取uid
        self.uid = robot_data.get('uid', robot_id)
    
    def update(self, robot_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新机器人
        
        Args:
            robot_data: 更新的机器人数据
            
        Returns:
            Dict: 更新结果
        """
        requestId = f"update_{uuid.uuid4().hex[:8]}"
        message = WebSocketMessage.create_request(
            WebSocketOperation.UPDATE_ROBOT,
            requestId,
            robot_data
        )
        
        response = self.client._send_message(message)
        if response.is_success():
            return response.response
        else:
            raise Exception(f"Robot update failed: {response.error}")
    
    def delete(self) -> bool:
        """
        删除机器人
        
        Returns:
            bool: 删除是否成功
        """
        requestId = f"delete_{uuid.uuid4().hex[:8]}"
        data = self.api_body.gen_other_data(robotId=self.robot_id, user=self.client.username)
        message = WebSocketMessage.create_request(
            WebSocketOperation.DELETE_ROBOT,
            requestId,
            data
        )
        
        response = self.client._send_message(message)
        success = response.is_success()
        
        # 从客户端中移除机器人实例
        if success:
            self.client.remove_robot(self.robot_id)
        
        return success
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取机器人状态
        
        Returns:
            Dict: 机器人状态信息
        """
        requestId = f"status_{uuid.uuid4().hex[:8]}"
        data = self.api_body.gen_other_data(robotId=self.robot_id, user=self.client.username)
        message = WebSocketMessage.create_request(
            WebSocketOperation.GET_STATUS,
            requestId,
            data
        )
        
        response = self.client._send_message(message)
        if response.is_success():
            return response.response
        else:
            raise Exception(f"Get robot status failed: {response.error}")
    
    # ========== 便捷方法 ==========
    
    def muteVideo(self) -> Dict[str, Any]:
        """静音视频"""
        data = self.api_body.gen_update_data(
            muteVideo=True, 
            robotId=self.robot_id, 
            user=self.client.username
        )
        return self.update(data)
    
    def unmuteVideo(self) -> Dict[str, Any]:
        """取消静音视频"""
        data = self.api_body.gen_update_data(
            muteVideo=False, 
            robotId=self.robot_id, 
            user=self.client.username
        )
        return self.update(data)
    
    def muteAudio(self) -> Dict[str, Any]:
        """静音音频"""
        data = self.api_body.gen_update_data(
            muteAudio=True, 
            robotId=self.robot_id, 
            user=self.client.username
        )
        return self.update(data)
    
    def unmuteAudio(self) -> Dict[str, Any]:
        """取消静音音频"""
        data = self.api_body.gen_update_data(
            muteAudio=False, 
            robotId=self.robot_id, 
            user=self.client.username
        )
        return self.update(data)
    
    def changeHostAudience(self, clientRole: int) -> Dict[str, Any]:
        """
        切换主播/观众角色
        
        Args:
            clientRole: 客户端角色 (1=主播, 0=观众)
        """
        data = self.api_body.gen_update_data(
            clientRole=clientRole, 
            robotId=self.robot_id, 
            user=self.client.username
        )
        return self.update(data)
    
    def getDatastreamMessage(self) -> Dict[str, Any]:
        """获取数据流消息"""
        datastream_config = self.api_body.gen_datastream_config(
            version=1, 
            mode=3, 
            ts=100
        )
        data = self.api_body.gen_update_data(
            dataStreamConfig=datastream_config,
            robotId=self.robot_id, 
            user=self.client.username
        )
        return self.update(data)
    
    def setVideoParams(self, width: int = None, height: int = None, 
                        fps: int = None, bitrate: int = None) -> Dict[str, Any]:
        """
        设置视频参数
        
        Args:
            width: 视频宽度
            height: 视频高度
            fps: 帧率
            bitrate: 码率
        """
        data = self.api_body.gen_update_data(
            width=width,
            height=height,
            fps=fps,
            bitrate=bitrate,
            robotId=self.robot_id,
            user=self.client.username
        )
        return self.update(data)
    
    def setCodecType(self, codec_type: int) -> Dict[str, Any]:
        """
        设置编解码类型
        
        Args:
            codec_type: 编解码类型
        """
        data = self.api_body.gen_update_data(
            codecType=codec_type,
            robotId=self.robot_id,
            user=self.client.username
        )
        return self.update(data)
    
    def setDatastreamConfig(self, mode: int = None, msg: str = None, 
                             msg_prefix: str = None, ts: int = None, 
                             version: int = None) -> Dict[str, Any]:
        """
        设置数据流配置
        
        Args:
            mode: 数据流模式
            msg: 数据流消息
            msg_prefix: 消息前缀
            ts: 时间间隔
            version: 版本号
        """
        datastream_config = self.api_body.gen_datastream_config(
            mode=mode,
            msg=msg,
            msgPrefix=msg_prefix,
            ts=ts,
            version=version
        )
        data = self.api_body.gen_update_data(
            dataStreamConfig=datastream_config,
            robotId=self.robot_id,
            user=self.client.username
        )
        return self.update(data)
    
    # ========== 属性访问 ==========
    
    @property
    def id(self) -> str:
        """获取机器人ID"""
        return self.robot_id
    
    @property
    def data(self) -> Dict[str, Any]:
        """获取机器人数据"""
        return self.robot_data.copy()
    
    def is_valid(self) -> bool:
        """检查机器人是否有效"""
        return (self.robot_id is not None and 
                self.robot_id != "" and 
                self.client.is_connected())
    
    def __str__(self) -> str:
        return f"WebSocketRobotInstance(id={self.robot_id}, valid={self.is_valid()})"
    
    def __repr__(self) -> str:
        return self.__str__()
