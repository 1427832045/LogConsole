# 高亮模板系统设计文档

**版本**: 1.0
**日期**: 2024-12-16
**基于**: LogConsole PRD v1.0 - 功能 6 扩展

---

## 概述

高亮模板系统是 LogConsole 第二阶段的核心功能，允许用户创建、管理和切换不同的日志高亮方案，提升不同场景下的日志分析效率。

---

## 功能架构

### 1. 高亮规则（HighlightRule）

**数据结构**:
```python
@dataclass
class HighlightRule:
    name: str              # 规则名称（如 "ERROR"）
    pattern: str           # 匹配模式
    is_regex: bool         # 是否为正则表达式
    foreground: str        # 前景色（十六进制，如 "#FF6B6B"）
    background: str        # 背景色（可选，空字符串表示透明）
    bold: bool             # 是否粗体
    italic: bool           # 是否斜体
    underline: bool        # 是否下划线
    priority: int          # 优先级（1-10，10 最高）
    enabled: bool          # 是否启用
```

**规则应用逻辑**:
1. 按优先级从高到低应用
2. 高优先级规则覆盖低优先级
3. 同一位置多个规则时，取优先级最高的

### 2. 高亮模板（HighlightTemplate）

**数据结构**:
```python
@dataclass
class HighlightTemplate:
    id: str                # 模板 ID（唯一标识）
    name: str              # 模板名称
    description: str       # 模板描述
    rules: List[HighlightRule]  # 高亮规则列表
    is_builtin: bool       # 是否为内置模板
    created_at: str        # 创建时间
    updated_at: str        # 更新时间
```

### 3. 预制模板定义

#### 3.1 通用模板（默认）
```python
GENERAL_TEMPLATE = {
    "id": "general",
    "name": "通用日志",
    "description": "适用于大多数应用日志",
    "rules": [
        {"name": "ERROR", "pattern": r"\bERROR\b", "regex": True, "fg": "#FF6B6B", "bg": "#4A1D1D", "bold": True, "priority": 10},
        {"name": "WARN", "pattern": r"\bWARN\b", "regex": True, "fg": "#FFD93D", "bg": "#3D3020", "bold": True, "priority": 9},
        {"name": "INFO", "pattern": r"\bINFO\b", "regex": True, "fg": "#6BCF7F", "bg": "", "bold": False, "priority": 7},
        {"name": "DEBUG", "pattern": r"\bDEBUG\b", "regex": True, "fg": "#A8A8A8", "bg": "", "bold": False, "priority": 5},
        {"name": "时间戳", "pattern": r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", "regex": True, "fg": "#7A7A7A", "bg": "", "italic": True, "priority": 3},
    ]
}
```

#### 3.2 Spring Boot 模板
```python
SPRING_BOOT_TEMPLATE = {
    "id": "spring-boot",
    "name": "Spring Boot",
    "description": "Spring Boot 应用日志",
    "rules": [
        # 基础日志级别（继承通用模板）
        {"name": "ERROR", "pattern": r"\bERROR\b", "regex": True, "fg": "#FF6B6B", "bg": "#4A1D1D", "bold": True, "priority": 10},
        {"name": "WARN", "pattern": r"\bWARN\b", "regex": True, "fg": "#FFD93D", "bg": "#3D3020", "bold": True, "priority": 9},

        # Spring 特定关键词
        {"name": "Tomcat 启动", "pattern": r"Tomcat started on port", "regex": True, "fg": "#6BCF7F", "bg": "#1D4A1D", "bold": True, "priority": 8},
        {"name": "Bean 创建", "pattern": r"Creating bean|Autowiring by", "regex": True, "fg": "#60A5FA", "bg": "", "priority": 6},
        {"name": "SQL 语句", "pattern": r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b", "regex": True, "fg": "#A78BFA", "bg": "", "priority": 7},
        {"name": "异常堆栈", "pattern": r"^\s+at\s+", "regex": True, "fg": "#EF4444", "bg": "#3D1D1D", "priority": 8},
        {"name": "Controller 映射", "pattern": r"Mapped \".*\" onto", "regex": True, "fg": "#34D399", "bg": "", "priority": 5},
    ]
}
```

#### 3.3 Nginx 访问日志模板
```python
NGINX_TEMPLATE = {
    "id": "nginx-access",
    "name": "Nginx 访问日志",
    "description": "Nginx access.log 格式",
    "rules": [
        {"name": "2xx 成功", "pattern": r'\" 2\d{2} ', "regex": True, "fg": "#6BCF7F", "bg": "", "priority": 9},
        {"name": "3xx 重定向", "pattern": r'\" 3\d{2} ', "regex": True, "fg": "#60A5FA", "bg": "", "priority": 9},
        {"name": "4xx 客户端错误", "pattern": r'\" 4\d{2} ', "regex": True, "fg": "#FFD93D", "bg": "#3D3020", "priority": 10},
        {"name": "5xx 服务器错误", "pattern": r'\" 5\d{2} ', "regex": True, "fg": "#FF6B6B", "bg": "#4A1D1D", "bold": True, "priority": 10},
        {"name": "IP 地址", "pattern": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "regex": True, "fg": "#A78BFA", "bg": "", "priority": 5},
        {"name": "HTTP 方法", "pattern": r'"(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) ', "regex": True, "fg": "#FFFFFF", "bg": "", "bold": True, "priority": 6},
        {"name": "慢响应 (>1s)", "pattern": r' ([1-9]\d{3,}|\d{4,}\.\d+)$', "regex": True, "fg": "#FB923C", "bg": "#3D2D20", "priority": 7},
    ]
}
```

#### 3.4 Docker 容器日志模板
```python
DOCKER_TEMPLATE = {
    "id": "docker",
    "name": "Docker 容器",
    "description": "Docker 容器日志",
    "rules": [
        {"name": "Container ID", "pattern": r"[a-f0-9]{12}", "regex": True, "fg": "#60A5FA", "bg": "", "priority": 6},
        {"name": "stdout", "pattern": r"\[stdout\]", "regex": True, "fg": "#6BCF7F", "bg": "", "priority": 7},
        {"name": "stderr", "pattern": r"\[stderr\]", "regex": True, "fg": "#FF6B6B", "bg": "", "priority": 7},
        {"name": "Exit code", "pattern": r"exited with code \d+", "regex": True, "fg": "#FFD93D", "bg": "", "bold": True, "priority": 8},
    ]
}
```

#### 3.5 测试日志模板
```python
TEST_LOG_TEMPLATE = {
    "id": "test-log",
    "name": "测试日志",
    "description": "单元测试/集成测试日志",
    "rules": [
        {"name": "PASS", "pattern": r"\b(PASS|PASSED|✓|✅)\b", "regex": True, "fg": "#6BCF7F", "bg": "#1D4A1D", "bold": True, "priority": 10},
        {"name": "FAIL", "pattern": r"\b(FAIL|FAILED|✗|❌)\b", "regex": True, "fg": "#FF6B6B", "bg": "#4A1D1D", "bold": True, "priority": 10},
        {"name": "SKIP", "pattern": r"\b(SKIP|SKIPPED|⊘)\b", "regex": True, "fg": "#FFD93D", "bg": "", "priority": 8},
        {"name": "测试用例", "pattern": r"(test_\w+|Test\w+::)", "regex": True, "fg": "#60A5FA", "bg": "", "bold": True, "priority": 7},
        {"name": "断言失败", "pattern": r"Assert(ion)?Error", "regex": True, "fg": "#EF4444", "bg": "", "priority": 9},
    ]
}
```

---

## UI 设计

### 模板选择器（工具栏）

**位置**: 工具栏中部，"查找" 按钮右侧

**组件**: QComboBox 下拉菜单

**显示内容**:
```
🎨 模板: [通用日志 ▼]
```

**下拉选项**:
```
─── 预制模板 ───
  通用日志 ✓
  Spring Boot
  Nginx 访问日志
  Docker 容器
  测试日志
─── 自定义模板 ───
  我的模板 1
  我的模板 2
─── 操作 ───
  + 新建模板...
  ⚙ 管理模板...
```

### 模板编辑器（设置界面）

**打开方式**: 工具栏 "设置" → "高亮模板管理"

**布局**:
```
+------------------------------------------+
| 高亮模板管理                             |
+------------------+-----------------------+
| 模板列表         | 规则编辑器            |
| ├ 通用日志 (内置)| 规则名称: [ERROR  ] ✓ |
| ├ Spring Boot    | 匹配模式: [\bERROR\b]|
| ├ Nginx         | [✓] 正则表达式        |
| └ + 新建模板     | 前景色: [🎨 #FF6B6B] |
|                  | 背景色: [🎨 #4A1D1D] |
| [导入] [导出]    | [✓] 粗体  [ ] 斜体   |
|                  | 优先级: [10 ▼]       |
|                  | ─────────────────    |
|                  | [添加规则] [删除]    |
|                  |                      |
|                  | 规则列表:            |
|                  | 1. ERROR (优先级10) |
|                  | 2. WARN (优先级9)   |
|                  | 3. INFO (优先级7)   |
+------------------+----------------------+
|          [取消]          [保存并应用]     |
+------------------------------------------+
```

---

## 技术实现

### 1. 模板管理器（TemplateManager）

```python
class TemplateManager:
    """高亮模板管理器"""

    def __init__(self):
        self.templates: Dict[str, HighlightTemplate] = {}
        self.current_template_id: str = "general"
        self.load_builtin_templates()
        self.load_user_templates()

    def load_builtin_templates(self):
        """加载内置模板"""
        pass

    def load_user_templates(self):
        """从本地加载用户模板"""
        pass

    def save_template(self, template: HighlightTemplate):
        """保存模板到本地"""
        pass

    def export_template(self, template_id: str, file_path: str):
        """导出模板为 JSON"""
        pass

    def import_template(self, file_path: str) -> HighlightTemplate:
        """从 JSON 导入模板"""
        pass

    def apply_template(self, template_id: str):
        """应用模板到高亮器"""
        pass
```

### 2. 存储路径

- **用户模板**: `~/.logconsole/templates/*.json`
- **配置文件**: `~/.logconsole/config.json`（记录当前模板 ID）

---

## 用户交互流程

### 快速切换模板
1. 用户点击工具栏 "🎨 模板" 下拉菜单
2. 选择目标模板（如 "Spring Boot"）
3. 系统立即应用模板，日志重新渲染
4. 显示提示："已切换到 Spring Boot 模板"

### 创建自定义模板
1. 工具栏 "设置" → "高亮模板管理"
2. 点击 "+ 新建模板"
3. 输入模板名称和描述
4. 添加高亮规则：
   - 输入规则名称（如 "数据库错误"）
   - 输入匹配模式（如 `SQLException`）
   - 选择是否使用正则表达式
   - 选择前景色和背景色（颜色选择器）
   - 设置字体样式（粗体/斜体/下划线）
   - 设置优先级（1-10）
5. 点击 "添加规则" 将规则加入列表
6. 重复添加多条规则
7. 点击 "保存并应用"

### 编辑现有模板
1. 在模板列表中选择要编辑的模板
2. 右侧显示该模板的所有规则
3. 点击规则可编辑
4. 点击删除按钮移除规则
5. 保存修改

### 导入/导出模板
- **导出**: 选择模板 → 点击 "导出" → 保存为 `.json` 文件
- **导入**: 点击 "导入" → 选择 `.json` 文件 → 验证格式 → 添加到模板列表

---

## 验收标准

- [ ] 提供 5 个预制模板（通用、Spring Boot、Nginx、Docker、测试日志）
- [ ] 工具栏模板切换器正常工作，<100ms 响应
- [ ] 模板编辑器界面直观，支持添加/编辑/删除规则
- [ ] 颜色选择器易用（支持十六进制输入和可视化选择）
- [ ] 模板导入/导出功能完整
- [ ] 非法模板导入时显示详细错误信息
- [ ] 用户模板持久化保存到 `~/.logconsole/templates/`
- [ ] 模板切换后日志立即重新渲染
- [ ] 支持禁用单个规则而不删除

---

## 性能考虑

- **规则数量限制**: 每个模板最多 50 条规则（避免性能问题）
- **正则表达式优化**: 预编译所有正则表达式
- **增量渲染**: 仅重新高亮可见区域（虚拟滚动）
- **缓存**: 缓存已应用的格式，避免重复计算

---

## 风险与缓解

| 风险 | 缓解策略 |
|------|----------|
| 复杂正则导致性能问题 | 限制正则复杂度，超时保护 |
| 颜色冲突难以理解 | 提供规则预览功能 |
| 模板过多导致选择困难 | 支持收藏和分组 |
| 导入恶意模板 | 严格验证 JSON 格式和数据类型 |

---

**下一步**: 实现 TemplateManager 和 HighlightEditor UI
