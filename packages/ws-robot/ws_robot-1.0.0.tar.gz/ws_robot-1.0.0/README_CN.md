# WS-Robot - WebSocket 机器人客户端库

一个功能完整、易于使用的 WebSocket 机器人管理 Python 库。

[English](README.md) | 简体中文

## ✨ 特性

- 🚀 **同步 WebSocket 客户端** - 基于 websocket-client，简单直观
- 🔄 **自动重连机制** - 智能重连，带指数退避策略
- 🎮 **完整生命周期管理** - 创建、更新、删除机器人
- 📊 **会话管理** - 会话查询、清理、强制清理
- 🔒 **加密支持** - 支持端到端加密配置
- 🎯 **资源预分配** - 批量创建前预分配资源
- 🛠️ **上下文管理器** - 自动资源清理，代码更简洁
- 📦 **零业务依赖** - 独立打包，无外部业务依赖

## 📦 安装

### 从 PyPI 安装

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
python3 -c "from ws_robot import WebSocketRobotClient; print('✓ 安装成功！')"
```

## 🚀 快速开始

### 最简单的例子

```python
from ws_robot import WebSocketRobotClient, WebSocketRobotManager, RobotAPIBody

# 创建并连接客户端
client = WebSocketRobotClient("ws://your-server.com/ws", "username", "password")
client.connect()

# 创建管理器
manager = WebSocketRobotManager(client)
api_body = RobotAPIBody()

# 生成机器人配置
robot_data = api_body.gen_create_data(
    appId="your_app_id",
    cname="test_channel",
    user="test_user",
    uid=12345,
    activeTime=120
)

# 创建机器人
robot = manager.add_robot(robot_data)
print(f"机器人已创建: {robot.robot_id}")

# 清理
manager.stop_robot(robot)
client.disconnect()
```

### 使用上下文管理器（推荐）

```python
from ws_robot import WebSocketRobotClient, WebSocketRobotManager, RobotAPIBody

with WebSocketRobotClient("ws://server.com/ws", "user", "pass") as client:
    with WebSocketRobotManager(client) as manager:
        api_body = RobotAPIBody()
        
        robot_data = api_body.gen_create_data(
            appId="app_id",
            cname="channel",
            user="user",
            uid=12345,
            activeTime=120
        )
        
        robot = manager.add_robot(robot_data)
        robot.muteVideo()  # 操作机器人
        
        # 自动清理资源
```

## 📚 核心功能

### 1. 创建机器人

```python
# 基础机器人
robot = manager.add_robot(api_body.gen_create_data(
    appId="app_id",
    cname="channel",
    user="alice",
    uid=10001,
    url="http://example.com/video.mp4",
    width=1280,
    height=720,
    fps=30,
    bitrate=1500,
    activeTime=300
))
```

### 2. 机器人控制

```python
# 视频控制
robot.muteVideo()      # 静音视频
robot.unmuteVideo()    # 取消静音

# 音频控制
robot.muteAudio()      # 静音音频
robot.unmuteAudio()    # 取消静音

# 角色切换
robot.changeHostAudience(clientRole=1)  # 主播
robot.changeHostAudience(clientRole=0)  # 观众

# 调整参数
robot.setVideoParams(width=1920, height=1080, fps=60, bitrate=3000)
```

### 3. 批量操作

```python
# 预分配资源
manager.preallocate_resources(robot_count=10, user="alice")

# 批量创建
robots = []
for i in range(10):
    robot_data = api_body.gen_create_data(
        appId="app_id",
        cname=f"channel_{i}",
        user="alice",
        uid=10000 + i,
        activeTime=300
    )
    robot = manager.add_robot(robot_data)
    robots.append(robot)

# 批量操作
manager.mute_all_videos()    # 静音所有视频
manager.unmute_all_audios()  # 取消所有音频静音
manager.stop_all_robots()    # 停止所有机器人
```

### 4. 会话管理

```python
# 查询机器人
robots = client.query_robots()
print(f"活跃机器人数: {len(robots)}")

# 查询会话
sessions = client.query_sessions()

# 获取状态
status = client.get_status()

# 清理会话
client.cleanup_session()

# 强制清理
client.force_cleanup()
```

### 5. 加密机器人

```python
# 生成加密配置
encryption_config = api_body.gen_encryption_config(
    encryptionMode="aes-128-gcm2",
    encryptionKey="your_key",
    encryptionKdfSalt="your_salt",
    datastreamEncryptionEnabled=True
)

# 创建加密机器人
robot_data = api_body.gen_create_data(
    appId="app_id",
    cname="secure_channel",
    user="bob",
    uid=20000,
    encryptionConfig=encryption_config
)
robot = manager.add_robot(robot_data)
```

### 6. 自动重连

```python
client = WebSocketRobotClient(
    ws_url="ws://server.com/ws",
    username="user",
    password="pass",
    auto_reconnect=True,             # 启用自动重连
    max_reconnect_attempts=5,        # 最大重连次数
    reconnect_interval=5,            # 重连间隔（秒）
    reconnect_backoff_factor=1.5     # 退避因子
)

# 检查重连状态
status = client.get_reconnect_status()

# 手动重连
client.force_reconnect()
```

## 📖 详细文档

- [快速开始指南](QUICKSTART.md) - 快速入门教程
- [完整 API 文档](README.md) - 英文版详细文档
- [包结构说明](PACKAGE_STRUCTURE.md) - 代码结构和架构
- [上传到 PyPI](UPLOAD_GUIDE.md) - 发布包的步骤
- [使用示例](example.py) - 更多代码示例

## 🔧 配置选项

### 客户端配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `ws_url` | str | - | WebSocket 服务器地址（必需） |
| `username` | str | "niki" | 用户名 |
| `password` | str | "test" | 密码 |
| `timeout` | int | 30 | 请求超时时间（秒） |
| `auto_reconnect` | bool | True | 是否自动重连 |
| `max_reconnect_attempts` | int | 5 | 最大重连次数 |
| `reconnect_interval` | int | 5 | 重连间隔（秒） |
| `reconnect_backoff_factor` | float | 1.5 | 重连退避因子 |

### 机器人配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `appId` | str | - | 应用 ID（必需） |
| `cname` | str | - | 频道名（必需） |
| `user` | str | - | 用户名（必需） |
| `uid` | int | None | 用户 ID（可选） |
| `url` | str | None | 视频 URL |
| `width` | int | 640 | 视频宽度 |
| `height` | int | 360 | 视频高度 |
| `fps` | int | 30 | 帧率 |
| `bitrate` | int | 800 | 码率 |
| `codecType` | int | 2 | 编解码类型 |
| `activeTime` | int | None | 活跃时间（秒） |
| `clientRole` | int | 1 | 客户端角色（1=主播，0=观众） |

## 🏗️ 项目结构

```
ws_robot/
├── __init__.py              # 包初始化
├── ws_message.py           # WebSocket 消息模型
├── ws_robot_client.py      # WebSocket 客户端
├── ws_robot_manager.py     # 机器人管理器
├── ws_robot_instance.py    # 机器人实例
├── robot_api_body.py       # API 请求生成器
├── setup.py                # 包配置
├── pyproject.toml          # 现代包配置
├── README.md               # 英文文档
├── README_CN.md            # 中文文档（本文件）
├── LICENSE                 # MIT 许可证
└── example.py              # 使用示例
```

**注意**: `ws_robot_use.py` 文件**不包含**在包中，这是一个业务特定的封装层，用户应根据自己的需求实现类似功能。

## 🔨 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black .
```

## 📦 打包和发布

### 本地构建

```bash
cd common/ws_robot
python3 -m build
```

### 上传到 TestPyPI

```bash
./build_and_upload.sh test
```

### 上传到 PyPI

```bash
./build_and_upload.sh prod
```

详细步骤请参考 [上传指南](UPLOAD_GUIDE.md)。

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 贡献指南

- 遵循 PEP 8 代码规范
- 添加适当的测试
- 更新相关文档
- 提交前运行所有测试

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 基于 [websocket-client](https://github.com/websocket-client/websocket-client) 库
- 感谢所有贡献者

## 📧 联系方式

- **GitHub**: https://github.com/yourusername/ws-robot
- **Email**: your.email@example.com
- **Issues**: https://github.com/yourusername/ws-robot/issues

## 🗓️ 更新日志

### 1.0.0 (2024-12-11)

- ✨ 初始版本发布
- ✅ 完整的 WebSocket 机器人管理功能
- ✅ 自动重连机制
- ✅ 会话管理
- ✅ 批量操作支持
- ✅ 加密机器人支持
- ✅ 上下文管理器支持
- ✅ 详细文档和示例

## 🚀 未来计划

### v1.1.0
- [ ] 异步支持（asyncio）
- [ ] 改进错误处理
- [ ] 更多测试用例
- [ ] 性能优化

### v1.2.0
- [ ] 日志级别配置
- [ ] 性能监控
- [ ] 更多使用示例
- [ ] WebSocket 压缩支持

### v2.0.0
- [ ] API 重构
- [ ] 插件系统
- [ ] GUI 管理工具
- [ ] Docker 支持

## 💡 常见问题

### Q: 为什么 `ws_robot_use.py` 不包含在包中？

A: `ws_robot_use.py` 是一个业务特定的封装层，包含了特定的业务逻辑（如固定的视频 URL、特定的机器人配置等）。为了保持包的通用性和独立性，我们选择不将其包含在包中。用户可以参考这个文件，根据自己的业务需求实现类似的封装。

### Q: 如何自定义日志？

A: 创建客户端时传入自定义的 logger：

```python
import logging
logger = logging.getLogger("my_app")
client = WebSocketRobotClient(ws_url, username, password, logger=logger)
```

### Q: 支持异步吗？

A: 当前版本（1.0.0）是同步实现。异步支持计划在 1.1.0 版本中添加。

### Q: 如何处理连接断开？

A: 启用自动重连功能：

```python
client = WebSocketRobotClient(
    ws_url, username, password,
    auto_reconnect=True,
    max_reconnect_attempts=5
)
```

### Q: 可以同时管理多个服务器的机器人吗？

A: 可以，为每个服务器创建独立的客户端和管理器：

```python
client1 = WebSocketRobotClient("ws://server1.com/ws", "user", "pass")
client2 = WebSocketRobotClient("ws://server2.com/ws", "user", "pass")

manager1 = WebSocketRobotManager(client1)
manager2 = WebSocketRobotManager(client2)
```

---

如有问题或建议，欢迎提交 [Issue](https://github.com/yourusername/ws-robot/issues)！

⭐ 如果这个项目对你有帮助，请给我们一个 Star！

