# pytestifyx

pytestifyx is a pytest-based automation testing framework for api, ui, app testing

## 安装

### 使用 uv (推荐)

```bash
# 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone https://github.com/jaylu2018/PyTestifyx.git
cd PyTestifyx

# 使用 uv 安装依赖
uv sync

# 激活虚拟环境并安装项目
uv run pip install -e .
```

### 使用 pip

```bash
pip install pytestifyx
```

## 使用方法

### CLI 命令

```bash
# 查看帮助
uv run pytestifyx --help

# 查看版本
uv run pytestifyx --version

# 创建测试项目
uv run pytestifyx --project

# 解析 fiddler saz 文件
uv run pytestifyx --parse
```

### 作为 pytest 插件

pytestifyx 会自动注册为 pytest 插件，提供额外的测试功能和中文支持。

```bash
# 运行测试
uv run pytest

# 使用 pytestifyx 功能
uv run python -c "from pytestifyx import TestCase, log; print('pytestifyx ready!')"
```

## 开发

```bash
# 克隆项目
git clone https://github.com/jaylu2018/PyTestifyx.git
cd PyTestifyx

# 安装开发依赖
uv sync

# 运行测试
uv run pytest

# 构建项目
uv build
```

## 许可证

Apache License 2.0
