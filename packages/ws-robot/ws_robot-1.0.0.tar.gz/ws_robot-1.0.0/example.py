"""
WS-Robot 使用示例
"""

from ws_robot import (
    WebSocketRobotClient, 
    WebSocketRobotManager,
    WebSocketRobotUse,
    RobotAPIBody
)


def basic_example():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 创建客户端
    client = WebSocketRobotClient(
        ws_url="ws://your-server.com/ws",
        username="your_username",
        password="your_password"
    )
    
    # 连接到服务器
    if client.connect():
        print("Connected to WebSocket server")
        
        # 创建管理器
        manager = WebSocketRobotManager(client)
        api_body = RobotAPIBody()
        
        # 创建机器人
        robot_data = api_body.gen_create_data(
            appId="your_app_id",
            cname="test_channel",
            user="test_user",
            uid=12345,
            url="http://example.com/video.mp4",
            width=640,
            height=360,
            fps=30,
            bitrate=800,
            activeTime=120
        )
        
        try:
            robot = manager.add_robot(robot_data)
            print(f"Robot created: {robot.robot_id}")
            
            # 执行操作
            robot.muteVideo()
            print("Video muted")
            
            # 停止机器人
            manager.stop_robot(robot)
            print("Robot stopped")
            
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            # 断开连接
            client.disconnect()
            print("Disconnected")


def context_manager_example():
    """使用上下文管理器示例"""
    print("\n=== 上下文管理器示例 ===")
    
    with WebSocketRobotClient(
        ws_url="ws://your-server.com/ws",
        username="your_username",
        password="your_password"
    ) as client:
        with WebSocketRobotManager(client) as manager:
            api_body = RobotAPIBody()
            
            robot_data = api_body.gen_create_data(
                appId="your_app_id",
                cname="test_channel",
                user="test_user",
                uid=12345,
                url="http://example.com/video.mp4",
                activeTime=120
            )
            
            try:
                robot = manager.add_robot(robot_data)
                print(f"Robot created: {robot.robot_id}")
                
                # 执行操作
                robot.muteVideo()
                robot.unmuteAudio()
                
                # 上下文管理器会自动清理资源
                
            except Exception as e:
                print(f"Error: {e}")


def batch_create_example():
    """批量创建机器人示例"""
    print("\n=== 批量创建示例 ===")
    
    client = WebSocketRobotClient(
        ws_url="ws://your-server.com/ws",
        username="your_username",
        password="your_password"
    )
    
    if client.connect():
        manager = WebSocketRobotManager(client)
        api_body = RobotAPIBody()
        
        try:
            # 示例1: 基础预分配（默认使用docker类型）
            manager.preallocate_resources(robot_count=5, user="test_user")
            print("Resources preallocated for 5 robots (default docker type)")
            
            # 示例2: 指定robot类型
            # manager.preallocate_resources(robot_count=5, user="test_user", type="stress")
            # print("Resources preallocated for 5 robots (stress type)")
            
            # 示例3: 指定单个IP
            # manager.preallocate_resources(robot_count=5, user="test_user", ip="23.236.121.43")
            # print("Resources preallocated on specific IP")
            
            # 示例4: 指定IP列表
            # manager.preallocate_resources(
            #     robot_count=5, 
            #     user="test_user", 
            #     ip=["23.236.121.43", "23.236.121.44"]
            # )
            # print("Resources preallocated on specific IPs")
            
            # 示例5: 同时指定type和ip（会验证类型匹配）
            # manager.preallocate_resources(
            #     robot_count=5, 
            #     user="test_user", 
            #     type="stress",
            #     ip=["23.236.121.43"]
            # )
            # print("Resources preallocated with type verification")
            
            # 批量创建
            robot_data_list = [
                api_body.gen_create_data(
                    appId="your_app_id",
                    cname=f"channel_{i}",
                    user="test_user",
                    uid=10000 + i,
                    url="http://example.com/video.mp4",
                    activeTime=120
                )
                for i in range(5)
            ]
            
            robots = manager.create_multiple_robots(robot_data_list)
            print(f"Created {len(robots)} robots")
            
            # 批量操作
            manager.mute_all_videos()
            print("All videos muted")
            
            # 停止所有机器人
            count = manager.stop_all_robots()
            print(f"Stopped {count} robots")
            
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            client.disconnect()


def preallocate_with_options_example():
    """预分配资源高级选项示例"""
    print("\n=== 预分配资源高级选项示例 ===")
    
    client = WebSocketRobotClient(
        ws_url="ws://your-server.com/ws",
        username="your_username",
        password="your_password"
    )
    
    if client.connect():
        manager = WebSocketRobotManager(client)
        robot_use = WebSocketRobotUse(manager)
        
        try:
            print("\n1. 基础预分配并创建（默认docker类型）")
            robots = robot_use.preallocate_and_create_robots(
                cname="test_channel",
                appId="your_app_id",
                count=3,
                user="test_user"
            )
            print(f"Created {len(robots)} robots with default settings")
            
            print("\n2. 指定robot类型")
            # robots = robot_use.preallocate_and_create_robots(
            #     cname="stress_test_channel",
            #     appId="your_app_id",
            #     count=5,
            #     user="test_user",
            #     type="stress"
            # )
            # print(f"Created {len(robots)} robots with stress type")
            
            print("\n3. 指定单个IP地址")
            # robots = robot_use.preallocate_and_create_robots(
            #     cname="specific_ip_channel",
            #     appId="your_app_id",
            #     count=3,
            #     user="test_user",
            #     ip="23.236.121.43"
            # )
            # print(f"Created {len(robots)} robots on specific IP")
            
            print("\n4. 指定多个IP地址")
            # robots = robot_use.preallocate_and_create_robots(
            #     cname="multi_ip_channel",
            #     appId="your_app_id",
            #     count=10,
            #     user="test_user",
            #     ip=["23.236.121.43", "23.236.121.44", "23.236.121.45"]
            # )
            # print(f"Created {len(robots)} robots across multiple IPs")
            
            print("\n5. 同时指定type和ip（类型验证）")
            # robots = robot_use.preallocate_and_create_robots(
            #     cname="verified_channel",
            #     appId="your_app_id",
            #     count=5,
            #     user="test_user",
            #     type="stress",
            #     ip=["23.236.121.43"]
            # )
            # print(f"Created {len(robots)} robots with type verification")
            
            # 停止所有机器人
            manager.stop_all_robots()
            print("\nAll robots stopped")
            
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            client.disconnect()


def session_management_example():
    """会话管理示例"""
    print("\n=== 会话管理示例 ===")
    
    client = WebSocketRobotClient(
        ws_url="ws://your-server.com/ws",
        username="your_username",
        password="your_password"
    )
    
    if client.connect():
        try:
            # 查询机器人
            robots = client.query_robots()
            print(f"Active robots: {len(robots)}")
            
            # 查询会话
            sessions = client.query_sessions()
            print(f"Active sessions: {len(sessions)}")
            
            # 获取系统状态
            status = client.get_status()
            print(f"System status: {status}")
            
            # 清理会话
            if client.cleanup_session():
                print("Session cleaned up")
            
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            client.disconnect()


def main():
    """主函数"""
    print("WS-Robot 使用示例\n")
    print("注意: 请先修改示例中的服务器地址、用户名、密码等配置信息")
    print("=" * 60)
    
    # 运行示例（根据需要注释/取消注释）
    # basic_example()
    # context_manager_example()
    # batch_create_example()
    # preallocate_with_options_example()  # 新增：预分配资源高级选项示例
    # session_management_example()
    
    print("\n请取消注释相应的示例函数来运行示例")


if __name__ == "__main__":
    main()

