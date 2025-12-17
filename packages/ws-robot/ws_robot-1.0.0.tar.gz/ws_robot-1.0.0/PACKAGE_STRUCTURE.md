# WS-Robot Package Structure

本文档描述了 ws-robot Python 包的结构和文件说明。

## 包结构

```
ws_robot/
├── __init__.py                 # 包初始化文件，导出主要类
├── ws_message.py              # WebSocket 消息模型
├── ws_robot_client.py         # WebSocket 机器人客户端
├── ws_robot_manager.py        # 机器人管理器
├── ws_robot_instance.py       # 机器人实例
├── robot_api_body.py          # API 请求体生成器
├── setup.py                   # setuptools 配置文件
├── pyproject.toml             # 现代 Python 打包配置
├── README.md                  # 包说明文档
├── LICENSE                    # MIT 许可证
├── MANIFEST.in                # 打包清单
├── requirements.txt           # 依赖列表
├── .gitignore                 # Git 忽略文件
├── example.py                 # 使用示例
├── build_and_upload.sh        # 打包上传脚本
├── UPLOAD_GUIDE.md            # PyPI 上传指南
└── PACKAGE_STRUCTURE.md       # 本文档

排除的文件（不打包）：
├── ws_robot_use.py            # 使用封装（不包含在包中）
├── test_ws_robot.py           # 测试文件（不包含在包中）
└── __pycache__/               # Python 缓存
```

## 核心模块说明

### 1. `__init__.py`
包的入口文件，导出主要的类和函数。

**导出的类：**
- `WebSocketMessage` - WebSocket 消息模型
- `WebSocketOperation` - WebSocket 操作枚举
- `WebSocketConstants` - WebSocket 常量
- `WebSocketRobotClient` - WebSocket 客户端
- `WebSocketRobotManager` - 机器人管理器
- `WebSocketRobotInstance` - 机器人实例
- `RobotAPIBody` - API 请求体生成器

### 2. `ws_message.py`
定义 WebSocket 消息格式和操作类型。

**主要类：**
- `WebSocketOperation(Enum)` - 操作类型枚举
- `WebSocketMessage` - 消息数据类
- `WebSocketConstants` - 常量配置

### 3. `ws_robot_client.py`
实现 WebSocket 客户端连接和通信。

**主要功能：**
- WebSocket 连接管理
- 自动重连机制
- 消息发送和接收
- 基础操作（创建、查询、删除机器人等）

### 4. `ws_robot_manager.py`
提供机器人批量管理功能。

**主要功能：**
- 机器人生命周期管理
- 批量操作
- 资源预分配
- 会话管理

### 5. `ws_robot_instance.py`
表示单个机器人实例。

**主要功能：**
- 机器人状态管理
- 视频/音频控制
- 参数配置
- 数据流管理

### 6. `robot_api_body.py`
生成各种 API 请求的数据体。

**主要功能：**
- 创建请求数据生成
- 更新请求数据生成
- 加密配置生成
- 数据流配置生成

## 配置文件说明

### `setup.py`
传统的 setuptools 配置文件，包含：
- 包元数据（名称、版本、作者等）
- 依赖声明
- 分类器
- 包发现配置

### `pyproject.toml`
现代 Python 打包标准（PEP 518），包含：
- 构建系统声明
- 项目元数据
- 依赖管理
- 工具配置

### `MANIFEST.in`
打包清单文件，指定哪些文件包含在分发包中：
- 包含文档文件（README.md, LICENSE）
- 包含所有 Python 文件
- 排除测试文件和使用封装文件

### `requirements.txt`
运行时依赖列表：
- `websocket-client>=1.0.0`

## 依赖关系图

```
ws_robot_use.py (不包含在包中)
    └── ws_robot_manager.py
            ├── ws_robot_client.py
            │       └── ws_message.py
            ├── ws_robot_instance.py
            │       ├── ws_message.py
            │       └── robot_api_body.py
            └── robot_api_body.py
```

## 包的使用

### 安装
```bash
pip install ws-robot
```

### 基本导入
```python
from ws_robot import (
    WebSocketRobotClient,
    WebSocketRobotManager,
    WebSocketRobotInstance,
    RobotAPIBody
)
```

### 完整示例
参见 `example.py` 文件。

## 版本控制

当前版本：**1.0.0**

版本号遵循语义化版本规范（Semantic Versioning）：
- MAJOR.MINOR.PATCH
- 1.0.0 = 第一个稳定版本

## 许可证

MIT License - 参见 `LICENSE` 文件

## 打包和发布

### 本地构建测试
```bash
python -m build
```

### 上传到 TestPyPI
```bash
./build_and_upload.sh test
```

### 上传到 PyPI
```bash
./build_and_upload.sh prod
```

详细步骤参见 `UPLOAD_GUIDE.md`。

## 开发指南

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

### 类型检查
```bash
mypy .
```

## 包大小

预计打包后大小：
- 源码包（.tar.gz）：约 30-40 KB
- Wheel 包（.whl）：约 30-40 KB

## 支持的 Python 版本

- Python 3.7+
- Python 3.8+
- Python 3.9+
- Python 3.10+
- Python 3.11+

## 平台兼容性

- Linux
- macOS
- Windows

## 注意事项

1. **ws_robot_use.py 不包含在包中**
   - 这是一个业务特定的封装层
   - 用户应该根据自己的需求实现类似功能
   - 可以作为示例参考

2. **robot_api_body.py 已集成**
   - 原本位于 `core.rest.robot_api_body`
   - 已复制到包中，成为独立模块
   - 所有导入已更新为内部导入

3. **无外部依赖冲突**
   - 唯一的外部依赖是 `websocket-client`
   - 所有其他依赖都是 Python 标准库

## 未来计划

### 1.1.0
- [ ] 添加异步支持（asyncio）
- [ ] 改进错误处理
- [ ] 添加更多测试用例

### 1.2.0
- [ ] 添加日志级别配置
- [ ] 添加性能监控
- [ ] 添加更多示例

### 2.0.0
- [ ] API 重构（如有必要）
- [ ] 支持新的 WebSocket 协议特性
- [ ] 插件系统

## 维护者

- 你的名字 <your.email@example.com>

## 贡献

欢迎提交 Issue 和 Pull Request！

请确保：
1. 代码符合 PEP 8 规范
2. 添加适当的测试
3. 更新文档
4. 提交前运行所有测试

## 相关资源

- PyPI 页面: https://pypi.org/project/ws-robot/
- GitHub 仓库: https://github.com/yourusername/ws-robot
- 文档: https://ws-robot.readthedocs.io/
- Issue 追踪: https://github.com/yourusername/ws-robot/issues

