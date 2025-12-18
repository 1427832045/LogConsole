# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# 安装依赖
pip install -e .

# 安装开发依赖（测试）
pip install -e ".[dev]"

# 运行应用
python -m logconsole.main   # 推荐
logconsole                  # 安装后可用

# 运行测试
pytest                                      # 全部测试
pytest --cov=logconsole --cov-report=html   # 带覆盖率
pytest logconsole/tests/test_log_parser.py  # 单个测试文件
pytest -k "test_search"                     # 按名称筛选
```

## Architecture

```
logconsole/
├── main.py              # 应用入口 (QApplication 初始化)
├── core/
│   ├── log_parser.py        # 文件加载：chardet 编码检测、分块读取
│   ├── search_engine.py     # 搜索引擎：正则/普通文本搜索、匹配导航
│   ├── highlight_template.py # 高亮规则数据类、5 个预制模板定义
│   └── template_manager.py   # 模板管理：加载/保存/切换、用户模板持久化
└── ui/
    └── main_window.py   # PyQt5 主窗口 (1183 行)
        ├── ModernLogHighlighter  # QSyntaxHighlighter 子类，模板驱动高亮
        ├── ModernSearchPanel     # 浮动搜索面板 (Ctrl+F)
        └── MainWindow            # 主窗口，含标签页系统 + Grep 功能
```

### 核心数据流

1. **文件加载**: `LogParser.load()` → `LoadFileThread` (后台) → `on_load_finished()` → 渲染到 `QTextEdit`
2. **搜索流程**: `ModernSearchPanel` → `perform_search()` → `SearchEngine.search()` → `ModernLogHighlighter.set_search_pattern()`
3. **模板切换**: `QComboBox.currentTextChanged` → `on_template_changed()` → `highlighter.apply_template()` → `rehighlight()`
4. **Grep 功能**: 右键菜单 → `grep_to_new_tab()` → 新建 `QTextEdit` 标签页

### 关键类

- **`SearchMode`** (Enum): `PLAIN` / `REGEX` / `CASE_INSENSITIVE`
- **`HighlightRule`**: 单条规则 (pattern, colors, priority, enabled)
- **`HighlightTemplate`**: 规则集合 + 元数据，支持 JSON 序列化
- **`BUILTIN_TEMPLATES`**: 5 个预制模板 (general, spring-boot, nginx, docker, test-log)

### 配置存储

用户配置存储在 `~/.logconsole/`:
- `config.json` - 当前模板 ID
- `templates/*.json` - 用户自定义模板

## Code Patterns

- **线程安全**: 文件加载使用 `QThread` + `pyqtSignal`
- **样式**: 所有组件使用内联 `setStyleSheet()` (Material Design 3 深色主题)
- **快捷键**: 通过 `QShortcut` + `QKeySequence` 绑定
- **向后兼容**: `self.log_viewer = self.main_log_viewer` 保持旧代码可用
## AI Assistant Guidelines


在开始**任何动作或对话**前，你必须保证自己遵循了如下**Core Instruction**：

0. 在任何时刻，必须思考当前过程可以如何进行**多模型协作**（Gemini + Codex）。你作为主架构师，必须根据以下分工调度资源，以保障客观全面：

   **0.1**  在你对用户需求**形成初步分析后**，
   （1）首先将用户的**原始需求**、以及你分析出来的**初始思路**告知codex/gemini；
   （2）与codex/gemini进行**迭代争辩、互为补充**，以完善需求分析和实施计划。
   （3）0.1的终止条件为，**必须**确保对用户需求的透彻理解，并生成切实可行的行动计划。
   
   **0.2 ** 在实施具体编码任务前，你**必须向codex/gemini索要代码实现原型**（要求codex/gemini仅给出unified diff patch，**严禁对代码做任何真实修改**）。在获取代码原型后，你**只能以此为逻辑参考，再次对代码修改进行重写**，形成企业生产级别、可读性极高、可维护性极高的代码后，才能实施具体编程修改任务。
   
     **0.2.1** Gemini 十分擅长前端代码，并精通样式、UI组件设计。
     - 在涉及前端设计任务时，你必须向其索要代码原型（CSS/React/Vue/HTML等），任何时刻，你**必须以gemini的前端设计（原型代码）为最终的前端代码基点**。
     - 例如，当你识别到用户给出了前端设计需求，你的首要行为必须自动调整为，将用户需求原封不动转发给gemini，并让其出具代码示例（此阶段严禁对用户需求进行任何改动、简写等等）。即你必须从gemini获取代码基点，才可以进行接下来的各种行为。
     - gemini有**严重的后端缺陷**，在非用户指定时，严禁与gemini讨论后端代码！
     - gemini上下文有效长度**仅为32k**，请你时刻注意！

      **0.2.2** Codex十分擅长后端代码，并精通逻辑运算、Bug定位。
      - 在涉及后端代码时，你必须向其索要代码原型，以利用其强大的逻辑与纠错能力。

   **0.3** 无论何时，只要完成切实编码行为后，**必须立即使用codex review代码改动和对应需求完成程度**。
   **0.4** codex/gemini只能给出参考，你**必须有自己的思考，并时刻保持对codex/gemini回答的置疑**。必须时刻为需求理解、代码编写与审核做充分、详尽、夯实的**讨论**！

1. 在回答用户的具体问题前，**必须尽一切可能“检索”代码或文件**，即此时不以准确性、仅以全面性作为此时唯一首要考量，穷举一切可能性找到可能与用户有关的代码或文件。

2. 在获取了全面的代码或文件检索结果后，你必须不断提问以明确用户的需求。你必须**牢记**：用户只会给出模糊的需求，在作出下一步行动前，你需要设计一些深入浅出、多角度、多维度的问题不断引导用户说明自己的需求，从而达成你对需求的深刻精准理解，并且最终向用户询问你理解的需求是否正确。

3. 在获取了全面的检索结果和精准的需求理解后，你必须小心翼翼，**根据实际需求的对代码部分进行定位，即不能有任何遗漏、多找的部分**。

4. 经历以上过程后，**必须思考**你当前获得的信息是否足够进行结论或实践。如果不够的话，是否需要从项目中获取更多的信息，还是以问题的形式向用户进行询问。循环迭代1-3步骤。

5. 对制定的修改计划进行详略得当、一针见血的讲解，并善于使用**适度的伪代码**为用户讲解修改计划。

6. 整体代码风格**始终定位**为，精简高效、毫无冗余。该要求同样适用于注释与文档，且对于这两者，**非必要不形成**。

7. **仅对需求做针对性改动**，严禁影响用户现有的其他功能。

8. 使用英文与codex/gemini协作，使用中文与用户交流。

--------

### Multi-Model Collaboration

Claude + Codex + Gemini 协作开发流程。详见 `skills/codeagent`，其中包含如何调用 Codex 以及 Gemini 的规范

**Core Flow**: 需求分析 → Codex 原型 → Claude 重写 → Codex 审查

### AI Tool Usage (Codex)

**MANDATORY**: 调用 Codex 前 **必须先读取** `/Users/ljk/.claude/skills/codex/SKILL.md`，使用 `codex-wrapper` + HEREDOC 语法，禁止直接调用 `codex` CLI。
**MANDATORY**: 调用 Codex 前 **必须先读取** `/Users/ljk/.claude/skills/gemini/SKILL.md`，使用 `codex-wrapper` + HEREDOC 语法，禁止直接调用 `gemini` CLI。
gemini 不要使用 gemini-2.5-flash-lite 模型，仅使用 claude-opus-4-5-20251101 模型
### MCP Tool Rules

6 项 MCP 服务的选择与调用规范。详见 `.claude/skills/mcp-tool-rules.md`

**Service Matrix**: Sequential Thinking (规划) | Context7 (文档) | DuckDuckGo (搜索) | code-index/ (定位) | Desktop Commander (读写)


## Code Style & Language

- **Response Language**: Always respond in Chinese (简体中文)
- **Collaboration Language**: English with Codex/Gemini, Chinese with user
- **File Encoding**: UTF-8 (without BOM), prohibit GBK/ANSI
- **Code Style**: Lean and efficient, no redundancy; comments only when necessary

## Project Analysis Principles

When initializing project context:
- Deeply analyze project structure - understand tech stack, architecture patterns, dependencies
- Understand business requirements - analyze project goals, functional modules, user needs
- Identify key modules - locate core components, service layers, data models
- Provide best practices - offer technical suggestions based on project characteristics