# LogConsole - 专业日志查看工具

[![Tests](https://img.shields.io/badge/tests-24%20passed-success)](./htmlcov/index.html)
[![Coverage](https://img.shields.io/badge/coverage-94%25%20(core)-success)](./htmlcov/index.html)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green)](https://pypi.org/project/PyQt5/)

一款专为开发者和测试工程师设计的桌面日志查看工具，提供高性能的大文件处理、智能搜索和 Material Design 3 深色主题。

## ✨ 核心特性

- 📁 **高性能文件加载**: 支持 1GB+ 日志文件，2 秒内打开
- 🔍 **强大搜索引擎**: 支持普通文本、正则表达式、忽略大小写三种模式
- 🎯 **快速导航**: F3/Shift+F3 匹配跳转，Ctrl+G 行号跳转
- 💾 **灵活导出**: 导出全部或过滤后的日志
- 🎨 **Material Design 3**: 现代化深色主题，减少眼睛疲劳
- ⚡ **编码智能检测**: 自动识别 UTF-8、GBK 等常见编码

## 🚀 快速开始

### 安装依赖

```bash
# 克隆仓库
git clone <repo-url>
cd LogConsole

# 安装依赖
pip install -e .

# 安装开发依赖（用于测试）
pip install -e ".[dev]"
```

### 运行应用

```bash
# 方法 1: 使用命令行
logconsole

# 方法 2: 直接运行 Python 模块
python -m logconsole.main

# 方法 3: 开发模式
python logconsole/main.py
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=logconsole --cov-report=html

# 查看 HTML 覆盖率报告
open htmlcov/index.html  # macOS
```

## 📖 使用说明

### 基础操作

1. **打开文件**: 点击工具栏 "打开文件" 或拖拽文件到窗口
2. **搜索**: 在搜索框输入关键词，选择搜索模式，点击 "搜索"
3. **导航**: 使用 F3/Shift+F3 在匹配结果间跳转
4. **跳转**: 按 Ctrl+G 输入行号快速定位
5. **导出**: 点击 "导出" 将日志保存为文本文件

### 搜索模式

- **普通文本**: 精确匹配关键词（特殊字符自动转义）
- **正则表达式**: 支持复杂模式匹配（如 `ERROR.*timeout`）
- **忽略大小写**: 不区分大小写（取消 "区分大小写" 复选框）

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+O` | 打开文件 |
| `Ctrl+G` | 跳转到行 |
| `F3` | 下一个匹配 |
| `Shift+F3` | 上一个匹配 |
| `Ctrl+E` | 导出日志 |

## 🏗️ 项目结构

```
LogConsole/
├── logconsole/              # 主包目录
│   ├── __init__.py         # 包初始化
│   ├── main.py             # 程序入口
│   ├── core/               # 核心业务逻辑
│   │   ├── log_parser.py   # 日志解析器 (94% 覆盖率)
│   │   └── search_engine.py # 搜索引擎 (96% 覆盖率)
│   ├── ui/                 # UI 界面
│   │   └── main_window.py  # 主窗口
│   ├── utils/              # 工具函数
│   └── tests/              # 单元测试
│       ├── test_log_parser.py
│       └── test_search_engine.py
├── docs/                   # 文档
│   ├── log-console-prd.md          # 产品需求文档
│   └── prototype-design-prompt.md  # 原型设计 prompt
├── pyproject.toml          # 项目配置
├── README.md               # 本文件
└── .claude/                # Claude Code 配置
```

## 🧪 测试覆盖率

**核心模块覆盖率** (≥90% 目标):
- ✅ **log_parser.py**: 94%
- ✅ **search_engine.py**: 96%

**总体**: 24 个测试全部通过 ✅

## 🔧 技术栈

- **语言**: Python 3.8+
- **GUI 框架**: PyQt5 5.15+
- **编码检测**: chardet 4.0+
- **测试框架**: pytest + pytest-qt + pytest-cov

## 🛣️ 开发路线图

### ✅ Phase 1 (MVP - 已完成)
- [x] 文件打开和浏览
- [x] 日志显示（行号+内容）
- [x] 关键词搜索（三种模式）
- [x] 行号跳转
- [x] 导出功能

### 🚧 Phase 2 (计划中)
- [ ] 智能过滤（日志级别、关键词规则）
- [ ] 预设高亮词配置
- [ ] 配置导入/导出
- [ ] 深色/浅色主题切换

### 🔮 Phase 3 (未来)
- [ ] 多文件对比
- [ ] 实时监控（tail -f）
- [ ] 结构化日志支持（JSON）
- [ ] 时间戳解析与过滤

## 📝 开发文档

- [产品需求文档 (PRD)](./docs/log-console-prd.md)
- [原型设计 Prompt](./docs/prototype-design-prompt.md)
- [开发计划](./claude/specs/logconsole-html-prototype/dev-plan.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**生成信息**:
- 版本: 0.1.0
- 生成日期: 2024-12-16
- 开发工具: Claude Code + /dev workflow
