# PyTestifyx 项目目录结构规划

## 新目录结构设计

基于新架构设计，以下是完整的项目目录结构规划：

```
PyTestifyx/
├── README.md
├── LICENSE
├── pyproject.toml                    # uv项目配置文件
├── setup.py                          # 向后兼容
├── MANIFEST.in
├── .gitignore
├── .github/                          # GitHub Actions
│   └── workflows/
│       ├── test.yml
│       ├── build.yml
│       └── release.yml
├── docs/                             # 文档目录
│   ├── README.md
│   ├── getting-started.md
│   ├── api-reference.md
│   ├── migration-guide.md
│   └── examples/
├── examples/                         # 示例项目
│   ├── api_test_example/
│   ├── ui_test_example/
│   ├── performance_test_example/
│   └── mixed_test_example/
├── tests/                            # 框架自身的测试
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── pytestifyx/                       # 主要源码目录
│   ├── __init__.py
│   ├── version.py                    # 版本信息
│   ├── core/                         # 核心模块
│   │   ├── __init__.py
│   │   ├── base.py                   # 基础TestCase类
│   │   ├── config.py                 # 配置管理系统
│   │   ├── registry.py               # 插件注册机制
│   │   ├── exceptions.py             # 自定义异常
│   │   └── types.py                  # 类型定义
│   ├── drivers/                      # 驱动层
│   │   ├── __init__.py
│   │   ├── api/                      # API测试驱动
│   │   │   ├── __init__.py
│   │   │   ├── client.py             # httpx异步客户端
│   │   │   ├── hooks.py              # 请求/响应钩子
│   │   │   ├── models.py             # 请求/响应数据模型
│   │   │   ├── auth.py               # 认证处理
│   │   │   ├── middleware.py         # 中间件
│   │   │   └── legacy.py             # requests兼容层
│   │   ├── ui/                       # UI测试驱动
│   │   │   ├── __init__.py
│   │   │   ├── page.py               # 页面对象基类
│   │   │   ├── browser.py            # 浏览器管理
│   │   │   ├── elements.py           # 元素操作封装
│   │   │   ├── actions.py            # 用户操作封装
│   │   │   └── mobile.py             # 移动端支持
│   │   └── performance/              # 性能测试驱动
│   │       ├── __init__.py
│   │       ├── locust_runner.py      # Locust集成
│   │       ├── metrics.py            # 性能指标收集
│   │       ├── scenarios.py          # 测试场景定义
│   │       ├── load_patterns.py      # 负载模式
│   │       └── reporters.py          # 性能报告生成
│   ├── plugins/                      # 插件系统
│   │   ├── __init__.py
│   │   ├── pytest_integration.py    # pytest集成插件
│   │   ├── html_reporter.py          # HTML报告插件
│   │   ├── realtime_monitor.py       # 实时监控插件
│   │   ├── data_collector.py         # 数据收集插件
│   │   ├── screenshot.py             # 截图插件
│   │   └── video_recorder.py         # 视频录制插件
│   ├── utils/                        # 工具模块
│   │   ├── __init__.py
│   │   ├── data_factory/             # 数据工厂（保留现有结构）
│   │   │   ├── __init__.py
│   │   │   ├── run.py
│   │   │   ├── core/
│   │   │   ├── providers/
│   │   │   └── single_interface/
│   │   ├── database/                 # 数据库操作（保留现有结构）
│   │   │   ├── __init__.py
│   │   │   ├── case.py
│   │   │   ├── assertion/
│   │   │   └── model/
│   │   ├── logs/                     # 日志系统（升级）
│   │   │   ├── __init__.py
│   │   │   ├── core.py               # 核心日志功能
│   │   │   ├── config.py             # 日志配置
│   │   │   ├── formatters.py         # 日志格式化器
│   │   │   └── handlers.py           # 自定义处理器
│   │   ├── reports/                  # 报告生成系统
│   │   │   ├── __init__.py
│   │   │   ├── html/                 # HTML报告
│   │   │   │   ├── __init__.py
│   │   │   │   ├── template.py       # 模板引擎
│   │   │   │   ├── generator.py      # 报告生成器
│   │   │   │   └── assets/           # 静态资源
│   │   │   │       ├── css/
│   │   │   │       ├── js/
│   │   │   │       └── images/
│   │   │   ├── charts/               # 图表生成
│   │   │   │   ├── __init__.py
│   │   │   │   ├── plotly_charts.py  # Plotly图表
│   │   │   │   ├── performance_charts.py # 性能图表
│   │   │   │   └── trend_analysis.py # 趋势分析
│   │   │   ├── exporters/            # 导出器
│   │   │   │   ├── __init__.py
│   │   │   │   ├── json_exporter.py
│   │   │   │   ├── xml_exporter.py
│   │   │   │   └── csv_exporter.py
│   │   │   └── collectors/           # 数据收集器
│   │   │       ├── __init__.py
│   │   │       ├── test_collector.py
│   │   │       ├── metrics_collector.py
│   │   │       └── screenshot_collector.py
│   │   ├── assertions/               # 断言库
│   │   │   ├── __init__.py
│   │   │   ├── api_assertions.py     # API断言
│   │   │   ├── ui_assertions.py      # UI断言
│   │   │   ├── performance_assertions.py # 性能断言
│   │   │   └── custom_matchers.py    # 自定义匹配器
│   │   ├── helpers/                  # 辅助工具
│   │   │   ├── __init__.py
│   │   │   ├── async_utils.py        # 异步工具
│   │   │   ├── decorators.py         # 装饰器集合
│   │   │   ├── validators.py         # 验证器
│   │   │   ├── retry.py              # 重试机制
│   │   │   └── wait.py               # 等待工具
│   │   ├── json/                     # JSON处理（保留）
│   │   │   ├── __init__.py
│   │   │   ├── core.py
│   │   │   └── utils.py
│   │   ├── msg_push/                 # 消息推送（保留）
│   │   │   ├── __init__.py
│   │   │   ├── email_tools.py
│   │   │   ├── feishu_tools.py
│   │   │   ├── slack_tools.py        # 新增Slack支持
│   │   │   └── webhook_tools.py      # 新增Webhook支持
│   │   ├── parse/                    # 解析工具（保留）
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── xmind_parse.py
│   │   │   └── har_parse.py          # 新增HAR文件解析
│   │   └── public/                   # 公共工具（保留）
│   │       ├── __init__.py
│   │       ├── constant.py
│   │       ├── extract_url.py
│   │       ├── get_hash_code.py
│   │       ├── get_project_path.py
│   │       ├── img_to_base64.py
│   │       ├── printify_table.py
│   │       └── trans_param_style.py
│   ├── cli/                          # 命令行接口
│   │   ├── __init__.py
│   │   ├── main.py                   # 主命令入口
│   │   ├── commands/                 # 子命令
│   │   │   ├── __init__.py
│   │   │   ├── init.py               # 初始化项目
│   │   │   ├── run.py                # 运行测试
│   │   │   ├── report.py             # 报告相关
│   │   │   ├── scaffold.py           # 脚手架生成
│   │   │   ├── parse.py              # 文件解析
│   │   │   └── server.py             # 报告服务器
│   │   ├── scaffold/                 # 脚手架模板
│   │   │   ├── __init__.py
│   │   │   ├── generators.py         # 代码生成器
│   │   │   └── validators.py         # 模板验证
│   │   └── server/                   # 内置服务器
│   │       ├── __init__.py
│   │       ├── app.py                # Flask/FastAPI应用
│   │       ├── routes.py             # 路由定义
│   │       └── websocket.py          # WebSocket支持
│   └── templates/                    # 模板文件
│       ├── project/                  # 项目模板
│       │   ├── api_test/
│       │   │   ├── conftest.py
│       │   │   ├── config.yaml
│       │   │   ├── requirements.txt
│       │   │   └── test_example.py
│       │   ├── ui_test/
│       │   │   ├── conftest.py
│       │   │   ├── config.yaml
│       │   │   ├── requirements.txt
│       │   │   └── test_example.py
│       │   ├── performance_test/
│       │   │   ├── conftest.py
│       │   │   ├── config.yaml
│       │   │   ├── requirements.txt
│       │   │   └── locustfile.py
│       │   └── mixed_test/
│       │       ├── conftest.py
│       │       ├── config.yaml
│       │       ├── requirements.txt
│       │       ├── api_tests/
│       │       ├── ui_tests/
│       │       └── performance_tests/
│       ├── reports/                  # 报告模板
│       │   ├── html/
│       │   │   ├── base.html
│       │   │   ├── summary.html
│       │   │   ├── details.html
│       │   │   └── charts.html
│       │   └── email/
│       │       ├── summary.html
│       │       └── failure_alert.html
│       └── configs/                  # 配置模板
│           ├── pytest.ini
│           ├── config.yaml
│           ├── logging.yaml
│           └── ci_cd/
│               ├── github_actions.yml
│               ├── gitlab_ci.yml
│               └── jenkins.groovy
└── scripts/                          # 构建和部署脚本
    ├── build.sh
    ├── test.sh
    ├── release.sh
    └── install_deps.sh
```

## 关键目录说明

### 1. 核心模块 (`pytestifyx/core/`)
- **base.py**: 统一的TestCase基类，支持API/UI/性能测试
- **config.py**: 基于Pydantic的配置管理系统
- **registry.py**: 插件注册和发现机制
- **exceptions.py**: 框架自定义异常类
- **types.py**: 类型定义和协议

### 2. 驱动层 (`pytestifyx/drivers/`)
- **api/**: httpx异步客户端，支持HTTP/2，包含认证和中间件
- **ui/**: playwright封装，支持多浏览器和移动端
- **performance/**: locust集成，支持分布式性能测试

### 3. 插件系统 (`pytestifyx/plugins/`)
- **pytest_integration.py**: 深度集成pytest生态
- **html_reporter.py**: 自定义HTML报告生成
- **realtime_monitor.py**: 实时测试监控
- **data_collector.py**: 测试数据收集和分析

### 4. 报告系统 (`pytestifyx/utils/reports/`)
- **html/**: 自定义HTML报告模板和生成器
- **charts/**: 基于Plotly的交互式图表
- **exporters/**: 多格式导出支持
- **collectors/**: 测试数据收集器

### 5. 命令行接口 (`pytestifyx/cli/`)
- **commands/**: 模块化的子命令实现
- **scaffold/**: 项目脚手架生成器
- **server/**: 内置报告服务器

### 6. 模板系统 (`pytestifyx/templates/`)
- **project/**: 不同类型测试项目的模板
- **reports/**: 报告模板（HTML、邮件等）
- **configs/**: 配置文件模板

## 迁移策略

### 1. 保留现有功能
- 保持现有的工具模块结构（data_factory、database、json等）
- 保留现有的API接口，确保向后兼容
- 保持现有的配置文件格式支持

### 2. 渐进式升级
- 新功能优先使用新架构
- 现有功能逐步迁移到新架构
- 提供迁移工具和指南

### 3. 兼容性考虑
- 支持Python 3.11+ (主要支持3.13)
- 支持uv和pip两种包管理方式
- 支持现有的pytest插件生态

## 配置文件结构

### pyproject.toml (uv项目配置)
```toml
[project]
name = "pytestifyx"
version = "1.0.0"
description = "全功能自动化测试框架"
authors = [{name = "luyh", email = "jaylu1995@outlook.com"}]
license = {text = "Apache-2.0"}
readme = "README.md"
requires-python = ">=3.11"

dependencies = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.23.0",
    "httpx[http2]>=0.27.0",
    "playwright>=1.40.0",
    "locust>=2.17.0",
    "pydantic>=2.5.0",
    "jinja2>=3.1.0",
    "plotly>=5.17.0",
    "loguru>=0.7.2",
    "rich>=13.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest-cov",
    "black",
    "isort",
    "mypy",
    "pre-commit",
]

[project.scripts]
pytestifyx = "pytestifyx.cli.main:main"

[project.entry-points."pytest11"]
pytestifyx = "pytestifyx.plugins.pytest_integration"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.7.0",
]
```

## 部署和分发

### 1. 包分发
- 主包：pytestifyx (核心功能)
- 扩展包：pytestifyx-plugins (额外插件)
- 模板包：pytestifyx-templates (项目模板)

### 2. 安装方式
```bash
# 使用uv安装（推荐）
uv add pytestifyx

# 使用pip安装
pip install pytestifyx

# 开发模式安装
uv sync --dev
```

### 3. 轻量级部署
- 支持Docker容器化部署
- 支持单文件可执行程序
- 支持云原生环境部署