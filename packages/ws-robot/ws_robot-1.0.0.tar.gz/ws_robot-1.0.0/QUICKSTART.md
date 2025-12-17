# WS-Robot 快速开始指南

本指南将帮助你快速开始使用 ws-robot 包。

## 目录

1. [安装](#安装)
2. [基本使用](#基本使用)
3. [常见场景](#常见场景)
4. [故障排查](#故障排查)

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install ws-robot
```

### 从源码安装

```bash
git clone https://github.com/yourusername/ws-robot.git
cd ws-robot
pip install -e .
```

### 验证安装

```bash
python verify_package.py
```

或者：

```python
python -c "from ws_robot import WebSocketRobotClient; print('Success!')"
```

## 基本使用

### 1. 最简单的示例

```python
from ws_robot import WebSocketRobotClient, WebSocketRobotManager, RobotAPIBody

# 1. 创建客户端并连接
client = WebSocketRobotClient(
    ws_url="ws://your-server.com/ws",
    username="your_username",
    password="your_password"
)
client.connect()

# 2. 创建管理器和 API 工具
manager = WebSocketRobotManager(client)
api_body = RobotAPIBody()

# 3. 创建机器人
robot_data = api_body.gen_create_data(
    appId="your_app_id",
    cname="test_channel",
    user="test_user",
    uid=12345,
    url="http://example.com/video.mp4",
    activeTime=120
)
robot = manager.add_robot(robot_data)
print(f"Robot created: {robot.robot_id}")

# 4. 清理
manager.stop_robot(robot)
client.disconnect()
```

### 2. 使用上下文管理器（推荐）

```python
from ws_robot import WebSocketRobotClient, WebSocketRobotManager, RobotAPIBody

with WebSocketRobotClient("ws://your-server.com/ws", "user", "pass") as client:
    with WebSocketRobotManager(client) as manager:
        api_body = RobotAPIBody()
        
        # 创建机器人
        robot_data = api_body.gen_create_data(
            appId="your_app_id",
            cname="test_channel",
            user="test_user",
            uid=12345,
            activeTime=120
        )
        robot = manager.add_robot(robot_data)
        
        # 执行操作
        robot.muteVideo()
        
        # 自动清理
```

## 常见场景

### 场景 1: 创建单个机器人

```python
from ws_robot import WebSocketRobotClient, WebSocketRobotManager, RobotAPIBody

client = WebSocketRobotClient("ws://server.com/ws", "user", "pass")
client.connect()

manager = WebSocketRobotManager(client)
api_body = RobotAPIBody()

# 创建机器人
robot_data = api_body.gen_create_data(
    appId="your_app_id",
    cname="my_channel",
    user="alice",
    uid=12345,
    url="http://example.com/video.mp4",
    width=1280,
    height=720,
    fps=30,
    bitrate=1500,
    activeTime=300  # 5分钟
)

robot = manager.add_robot(robot_data)
print(f"Robot {robot.robot_id} created in channel 'my_channel'")

# 操作机器人
robot.muteVideo()      # 静音视频
robot.unmuteAudio()    # 取消静音音频

# 清理
manager.stop_robot(robot)
client.disconnect()
```

### 场景 2: 批量创建机器人

```python
from ws_robot import WebSocketRobotClient, WebSocketRobotManager, RobotAPIBody

client = WebSocketRobotClient("ws://server.com/ws", "user", "pass")
client.connect()

manager = WebSocketRobotManager(client)
api_body = RobotAPIBody()

# 预分配资源（可选，但推荐）
manager.preallocate_resources(robot_count=10, user="alice")

# 批量创建
robots = []
for i in range(10):
    robot_data = api_body.gen_create_data(
        appId="your_app_id",
        cname=f"channel_{i}",
        user="alice",
        uid=10000 + i,
        activeTime=300
    )
    robot = manager.add_robot(robot_data)
    robots.append(robot)
    print(f"Created robot {i+1}/10: {robot.robot_id}")

print(f"Total robots created: {len(robots)}")

# 批量停止
stopped = manager.stop_all_robots()
print(f"Stopped {stopped} robots")

client.disconnect()
```

### 场景 3: 机器人控制

```python
from ws_robot import WebSocketRobotClient, WebSocketRobotManager, RobotAPIBody

client = WebSocketRobotClient("ws://server.com/ws", "user", "pass")
client.connect()

manager = WebSocketRobotManager(client)
api_body = RobotAPIBody()

# 创建机器人
robot_data = api_body.gen_create_data(
    appId="your_app_id",
    cname="control_channel",
    user="bob",
    uid=20000,
    activeTime=600
)
robot = manager.add_robot(robot_data)

# 视频控制
robot.muteVideo()      # 静音视频
robot.unmuteVideo()    # 取消静音视频

# 音频控制
robot.muteAudio()      # 静音音频
robot.unmuteAudio()    # 取消静音音频

# 角色切换
robot.changeHostAudience(clientRole=1)  # 切换为主播
robot.changeHostAudience(clientRole=0)  # 切换为观众

# 视频参数调整
robot.setVideoParams(width=1920, height=1080, fps=60, bitrate=3000)

# 获取状态
status = robot.get_status()
print(f"Robot status: {status}")

# 删除机器人
robot.delete()
client.disconnect()
```

### 场景 4: 会话管理

```python
from ws_robot import WebSocketRobotClient

client = WebSocketRobotClient("ws://server.com/ws", "user", "pass")
client.connect()

# 查询机器人
robots = client.query_robots()
print(f"Active robots: {len(robots)}")
for r in robots:
    print(f"  - Robot {r.get('robotId')}: {r.get('cname')}")

# 查询会话
sessions = client.query_sessions()
print(f"Active sessions: {len(sessions)}")

# 获取系统状态
status = client.get_status()
print(f"System status: {status}")

# 清理会话
client.cleanup_session()
print("Session cleaned up")

client.disconnect()
```

### 场景 5: 自动重连

```python
from ws_robot import WebSocketRobotClient
import time

# 配置自动重连
client = WebSocketRobotClient(
    ws_url="ws://server.com/ws",
    username="user",
    password="pass",
    auto_reconnect=True,              # 启用自动重连
    max_reconnect_attempts=5,         # 最大重连次数
    reconnect_interval=5,             # 重连间隔（秒）
    reconnect_backoff_factor=1.5      # 退避因子
)

client.connect()

# 检查连接状态
while True:
    if client.is_connected():
        print("Connected")
        
        # 获取重连状态
        status = client.get_reconnect_status()
        print(f"Reconnect status: {status}")
        
        # 执行操作...
        
    else:
        print("Disconnected, waiting for reconnection...")
    
    time.sleep(10)
```

### 场景 6: 加密机器人

```python
from ws_robot import WebSocketRobotClient, WebSocketRobotManager, RobotAPIBody

client = WebSocketRobotClient("ws://server.com/ws", "user", "pass")
client.connect()

manager = WebSocketRobotManager(client)
api_body = RobotAPIBody()

# 生成加密配置
encryption_config = api_body.gen_encryption_config(
    encryptionMode="aes-128-gcm2",
    encryptionKey="your_encryption_key",
    encryptionKdfSalt="your_salt",
    datastreamEncryptionEnabled=True
)

# 创建加密机器人
robot_data = api_body.gen_create_data(
    appId="your_app_id",
    cname="secure_channel",
    user="charlie",
    uid=30000,
    activeTime=300,
    encryptionConfig=encryption_config
)

robot = manager.add_robot(robot_data)
print(f"Encrypted robot created: {robot.robot_id}")

# 清理
manager.stop_robot(robot)
client.disconnect()
```

## 故障排查

### 问题 1: 导入错误

**错误:**
```
ModuleNotFoundError: No module named 'ws_robot'
```

**解决:**
```bash
pip install ws-robot
# 或者
pip install --upgrade ws-robot
```

### 问题 2: 连接超时

**错误:**
```
TimeoutError: Request timeout after 30 seconds
```

**解决:**
```python
# 增加超时时间
client = WebSocketRobotClient(
    ws_url="ws://server.com/ws",
    username="user",
    password="pass",
    timeout=60  # 增加到 60 秒
)
```

### 问题 3: 依赖缺失

**错误:**
```
ModuleNotFoundError: No module named 'websocket'
```

**解决:**
```bash
pip install websocket-client
```

### 问题 4: 机器人创建失败

**错误:**
```
Exception: Robot creation failed: Invalid parameters
```

**解决:**
- 检查 `appId` 是否正确
- 检查 `cname` 是否有效
- 确保 `uid` 唯一（如果指定）
- 检查视频 URL 是否可访问

### 问题 5: 连接断开

**解决:**
```python
# 启用自动重连
client = WebSocketRobotClient(
    ws_url="ws://server.com/ws",
    username="user",
    password="pass",
    auto_reconnect=True
)
```

## 进阶使用

### 自定义日志

```python
import logging

# 配置日志
logger = logging.getLogger("ws_robot")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# 使用自定义日志
client = WebSocketRobotClient(
    ws_url="ws://server.com/ws",
    username="user",
    password="pass",
    logger=logger
)
```

### 消息处理器

```python
def on_status_update(message):
    print(f"Status update: {message}")

# 注册消息处理器
client.register_message_handler("STATUS_UPDATE", on_status_update)
```

## 更多资源

- 完整文档: `README.md`
- 详细示例: `example.py`
- API 参考: `PACKAGE_STRUCTURE.md`
- 上传指南: `UPLOAD_GUIDE.md`

## 获取帮助

- GitHub Issues: https://github.com/yourusername/ws-robot/issues
- Email: your.email@example.com

## 下一步

1. 阅读完整的 `README.md`
2. 查看 `example.py` 中的更多示例
3. 参考 API 文档了解所有功能
4. 开始构建你的应用！

祝你使用愉快！🚀

