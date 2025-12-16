# PyTestifyx 新架构设计

## 设计目标
- 支持三大核心能力：API自动化（httpx）、UI自动化（playwright）、性能测试（locust）
- 基于pytest生态，充分利用其插件机制
- 企业级使用，支持详细HTML报告和可视化图表
- 开箱即用，轻量级部署
- 面向Python 3.13和uv包管理

## 新架构模式

### 1. 分层架构设计

```
PyTestifyx Framework
├── Core Layer (核心层)
│   ├── TestCase基类
│   ├── 配置管理系统
│   └── 插件注册机制
├── Driver Layer (驱动层)
│   ├── API Driver (httpx-based)
│   ├── UI Driver (playwright-based)
│   └── Performance Driver (locust-based)
├── Utils Layer (工具层)
│   ├── 数据工厂
│   ├── 报告生成器
│   ├── 日志系统
│   └── 断言库
├── Plugin Layer (插件层)
│   ├── pytest集成插件
│   ├── HTML报告插件
│   └── 实时监控插件
└── CLI Layer (命令行层)
    ├── 项目脚手架
    ├── 测试执行器
    └── 报告查看器
```

### 2. 核心设计原则

#### 2.1 统一接口设计
- 所有测试类型继承统一的`TestCase`基类
- 提供一致的配置接口和执行流程
- 支持混合测试场景（API+UI+性能）

#### 2.2 异步优先设计
- 基于httpx的异步HTTP客户端
- 支持异步测试执行和并发控制
- 与playwright的异步API无缝集成

#### 2.3 插件化架构
- 基于pytest的hook机制
- 支持自定义插件扩展
- 模块化的功能组件

### 3. 技术栈升级

#### 3.1 核心依赖
```yaml
# 核心框架
pytest: ">=8.3.0"
pytest-asyncio: ">=0.23.0"

# HTTP客户端 (替换requests)
httpx: ">=0.27.0"
httpx[http2]: ">=0.27.0"

# UI测试
playwright: ">=1.40.0"
pytest-playwright: ">=0.4.3"

# 性能测试
locust: ">=2.17.0"

# 报告和可视化
jinja2: ">=3.1.0"
plotly: ">=5.17.0"
pandas: ">=2.1.0"

# 工具库
pydantic: ">=2.5.0"
loguru: ">=0.7.2"
rich: ">=13.7.0"
```

#### 3.2 Python版本支持
- 主要支持：Python 3.13
- 兼容支持：Python 3.11, 3.12
- 包管理：uv优先，pip备选

### 4. 模块重构设计

#### 4.1 新的目录结构
```
pytestifyx/
├── __init__.py
├── core/                    # 核心模块
│   ├── __init__.py
│   ├── base.py             # 基础TestCase类
│   ├── config.py           # 配置管理
│   ├── registry.py         # 插件注册
│   └── exceptions.py       # 异常定义
├── drivers/                 # 驱动模块
│   ├── __init__.py
│   ├── api/                # API测试驱动
│   │   ├── __init__.py
│   │   ├── client.py       # httpx客户端封装
│   │   ├── hooks.py        # 请求钩子
│   │   └── models.py       # 数据模型
│   ├── ui/                 # UI测试驱动
│   │   ├── __init__.py
│   │   ├── page.py         # 页面对象基类
│   │   ├── browser.py      # 浏览器管理
│   │   └── elements.py     # 元素操作
│   └── performance/        # 性能测试驱动
│       ├── __init__.py
│       ├── locust_runner.py # Locust集成
│       ├── metrics.py      # 性能指标
│       └── scenarios.py    # 测试场景
├── plugins/                 # 插件模块
│   ├── __init__.py
│   ├── pytest_integration.py # pytest集成
│   ├── html_reporter.py    # HTML报告生成
│   ├── realtime_monitor.py # 实时监控
│   └── data_collector.py   # 数据收集
├── utils/                   # 工具模块
│   ├── __init__.py
│   ├── data_factory/       # 数据工厂（保留现有）
│   ├── database/           # 数据库操作（保留现有）
│   ├── logs/               # 日志系统（升级）
│   ├── reports/            # 报告生成
│   │   ├── __init__.py
│   │   ├── html_template.py # HTML模板
│   │   ├── charts.py       # 图表生成
│   │   └── exporters.py    # 导出器
│   ├── assertions/         # 断言库
│   │   ├── __init__.py
│   │   ├── api_assertions.py
│   │   ├── ui_assertions.py
│   │   └── performance_assertions.py
│   └── helpers/            # 辅助工具
│       ├── __init__.py
│       ├── async_utils.py  # 异步工具
│       ├── decorators.py   # 装饰器
│       └── validators.py   # 验证器
├── cli/                     # 命令行模块
│   ├── __init__.py
│   ├── main.py             # 主命令入口
│   ├── scaffold.py         # 脚手架生成
│   ├── runner.py           # 测试执行器
│   └── server.py           # 报告服务器
└── templates/               # 模板文件
    ├── project/            # 项目模板
    ├── reports/            # 报告模板
    └── configs/            # 配置模板
```

### 5. 关键设计决策

#### 5.1 异步架构
- 所有HTTP请求使用httpx异步客户端
- 支持异步测试方法和fixture
- 提供同步兼容层，保持向后兼容

#### 5.2 配置系统
- 基于Pydantic的类型安全配置
- 支持环境变量、YAML、TOML多种格式
- 分层配置：全局 -> 项目 -> 测试用例

#### 5.3 报告系统
- 自定义HTML模板，支持主题切换
- 集成Plotly实现交互式图表
- 支持实时数据更新和WebSocket推送

#### 5.4 性能测试集成
- Locust作为性能测试引擎
- 与API测试共享用例定义
- 支持分布式性能测试

### 6. 兼容性策略

#### 6.1 向后兼容
- 保持现有API接口不变
- 提供迁移工具和指南
- 渐进式升级路径

#### 6.2 迁移路径
1. 保留现有requests实现作为legacy模式
2. 新增httpx实现作为默认模式
3. 提供配置开关支持两种模式
4. 逐步废弃requests实现

### 7. 性能优化

#### 7.1 并发控制
- 基于asyncio的异步并发
- 智能连接池管理
- 资源使用监控和限制

#### 7.2 内存管理
- 流式数据处理
- 大文件上传/下载优化
- 测试结果数据压缩存储

### 8. 扩展性设计

#### 8.1 插件机制
- 基于entry_points的插件发现
- 标准化的插件接口
- 插件生命周期管理

#### 8.2 自定义扩展
- 支持自定义驱动器
- 支持自定义报告格式
- 支持自定义断言方法