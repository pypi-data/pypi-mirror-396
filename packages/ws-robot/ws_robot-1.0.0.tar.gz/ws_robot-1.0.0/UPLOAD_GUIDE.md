# WS-Robot 上传到 PyPI 指南

本指南将帮助你将 ws-robot 包上传到 PyPI。

## 前置准备

### 1. 安装打包工具

```bash
pip install --upgrade build twine
```

### 2. 注册 PyPI 账户

如果还没有 PyPI 账户，需要先注册：

- PyPI (正式): https://pypi.org/account/register/
- TestPyPI (测试): https://test.pypi.org/account/register/

### 3. 生成 API Token

在 PyPI 账户设置中生成 API Token：

1. 登录 PyPI
2. 进入账户设置 (Account settings)
3. 找到 API tokens 部分
4. 创建一个新的 token
5. 保存 token（只显示一次）

## 配置文件

### 更新 setup.py 和 pyproject.toml

在上传前，请确保更新以下信息：

**setup.py:**
```python
setup(
    name='ws-robot',  # 包名（确保在 PyPI 上唯一）
    version='1.0.0',  # 版本号
    author='Your Name',  # 你的名字
    author_email='your.email@example.com',  # 你的邮箱
    url='https://github.com/yourusername/ws-robot',  # 项目地址
    # ...
)
```

**pyproject.toml:**
```toml
[project]
name = "ws-robot"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
```

## 打包步骤

### 1. 清理旧的构建文件

```bash
cd common/ws_robot
rm -rf build/ dist/ *.egg-info
```

### 2. 构建包

```bash
python -m build
```

这会在 `dist/` 目录下生成两个文件：
- `ws-robot-1.0.0.tar.gz` (源码分发包)
- `ws_robot-1.0.0-py3-none-any.whl` (wheel 包)

### 3. 检查包

在上传前，检查包是否正确：

```bash
twine check dist/*
```

## 上传到 PyPI

### 方法 1: 先上传到 TestPyPI（推荐）

TestPyPI 是测试环境，可以先在这里测试：

```bash
twine upload --repository testpypi dist/*
```

然后测试安装：

```bash
pip install --index-url https://test.pypi.org/simple/ ws-robot
```

### 方法 2: 直接上传到 PyPI

确认包没有问题后，上传到正式 PyPI：

```bash
twine upload dist/*
```

上传时会提示输入用户名和密码：
- Username: `__token__`
- Password: 你的 API token（包括 `pypi-` 前缀）

## 使用 .pypirc 配置文件（可选）

为了避免每次都输入 token，可以创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PYPI-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-PYPI-TOKEN-HERE
```

**注意：** 请确保 `.pypirc` 文件的权限设置为 600：

```bash
chmod 600 ~/.pypirc
```

使用配置文件后，上传命令可以简化为：

```bash
# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 上传到 PyPI
twine upload dist/*
```

## 验证安装

上传成功后，可以通过 pip 安装测试：

```bash
# 卸载本地版本（如果有）
pip uninstall ws-robot -y

# 从 PyPI 安装
pip install ws-robot

# 测试导入
python -c "from ws_robot import WebSocketRobotClient; print('Success!')"
```

## 更新包版本

当需要更新包时：

1. 修改代码
2. 更新版本号（在 `setup.py` 和 `pyproject.toml` 中）
3. 更新 `README.md` 中的更新日志
4. 重新构建和上传：

```bash
rm -rf build/ dist/ *.egg-info
python -m build
twine check dist/*
twine upload dist/*
```

## 版本号规范

建议遵循语义化版本规范（Semantic Versioning）：

- `MAJOR.MINOR.PATCH` (如 `1.0.0`)
- MAJOR: 不兼容的 API 修改
- MINOR: 向后兼容的功能性新增
- PATCH: 向后兼容的问题修正

## 常见问题

### 1. 包名已存在

如果包名已经被占用，需要更改包名：

- 修改 `setup.py` 和 `pyproject.toml` 中的 `name`
- 可以尝试添加前缀或后缀，如 `agora-ws-robot`

### 2. 文件未包含

如果某些文件没有被包含在包中：

- 检查 `MANIFEST.in` 文件
- 确保 `setup.py` 中的 `package_data` 配置正确

### 3. 导入错误

如果安装后导入失败：

- 检查包结构是否正确
- 确保 `__init__.py` 文件存在
- 检查依赖是否正确安装

## 安全建议

1. **不要** 将 API token 提交到版本控制系统
2. **不要** 在代码中硬编码 token
3. 定期轮换 API token
4. 使用有限权限的 token（如果可能）
5. 将 `.pypirc` 添加到 `.gitignore`

## 自动化上传（GitHub Actions）

可以使用 GitHub Actions 自动化发布流程。创建 `.github/workflows/publish.yml`：

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

在 GitHub 仓库的 Settings -> Secrets 中添加 `PYPI_API_TOKEN`。

## 参考资源

- PyPI 官方文档: https://packaging.python.org/
- Twine 文档: https://twine.readthedocs.io/
- Setuptools 文档: https://setuptools.pypa.io/
- Python Packaging User Guide: https://packaging.python.org/tutorials/packaging-projects/

