"""
WebSocket机器人测试脚本 - 同步版本
用于验证WebSocket同步方案是否正常工作
"""

import logging
from . import WebSocketRobotClient, WebSocketRobotManager, WebSocketRobotUse


def test_websocket_robot():
    """测试WebSocket机器人功能 - 同步版本"""
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 创建WebSocket客户端
    client = WebSocketRobotClient(
        ws_url="ws://localhost:8080/ws",  # 请根据实际服务器地址修改
        username="niki",
        password="test",
        logger=logger
    )
    
    try:
        # 连接服务器
        logger.info("Connecting to WebSocket server...")
        if not client.connect():
            logger.error("Failed to connect to WebSocket server")
            return False
        
        logger.info("Connected successfully!")
        
        # 创建管理器和使用封装
        manager = WebSocketRobotManager(client)
        robot_use = WebSocketRobotUse(manager)
        
        # 预分配资源
        logger.info("Pre-allocating resources...")
        result = manager.preallocate_resources(robot_count=5, user="test_user")
        logger.info(f"Resources pre-allocated: {result}")
        
        # 创建机器人
        logger.info("Creating robot...")
        robot = robot_use.add_base_robot(
            cname="test_channel",
            appId="0c0b4b61adf94de1befd7cdd78a50444",
            activeTime=120
        )
        logger.info(f"Robot created: {robot.robot_id}")
        
        # 操作机器人
        logger.info("Muting robot video...")
        robot.muteVideo()
        
        logger.info("Muting robot audio...")
        robot.muteAudio()
        
        # 查询机器人列表
        logger.info("Querying robots...")
        robots = manager.list_robots()
        logger.info(f"Total robots: {len(robots)}")
        
        # 获取系统状态
        logger.info("Getting system status...")
        status = manager.get_status()
        logger.info(f"System status: {status}")
        
        # 停止机器人
        logger.info("Stopping robot...")
        manager.stop_robot(robot)
        logger.info("Robot stopped")
        
        logger.info("Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
        
    finally:
        # 清理资源
        try:
            manager.stop_all_robots()
            client.disconnect()
            logger.info("Resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def test_with_context_manager():
    """使用上下文管理器测试"""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    with WebSocketRobotClient("ws://localhost:8080/ws", logger=logger) as client:
        manager = WebSocketRobotManager(client)
        robot_use = WebSocketRobotUse(manager)
        
        # 预分配资源
        manager.preallocate_resources(5, "context_user")
        
        # 创建机器人
        robot = robot_use.add_base_robot(
            cname="context_channel",
            appId="0c0b4b61adf94de1befd7cdd78a50444"
        )
        
        # 操作机器人
        robot.muteVideo()
        
        # 自动清理（上下文管理器会自动处理）


if __name__ == "__main__":
    print("Starting WebSocket Robot Test...")
    success = test_websocket_robot()
    if success:
        print("✅ Test passed!")
    else:
        print("❌ Test failed!")
    
    print("\nTesting context manager...")
    test_with_context_manager()
    print("✅ Context manager test completed!")
