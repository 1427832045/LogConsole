"""
高亮规则和模板数据类
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import json
import os
from pathlib import Path


@dataclass
class HighlightRule:
    """单条高亮规则"""
    name: str
    pattern: str
    is_regex: bool = False
    foreground: str = "#FFFFFF"
    background: str = ""
    bold: bool = False
    italic: bool = False
    underline: bool = False
    priority: int = 5
    enabled: bool = True

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'HighlightRule':
        """从字典创建"""
        return cls(**data)


@dataclass
class HighlightTemplate:
    """高亮模板"""
    id: str
    name: str
    description: str
    rules: List[HighlightRule] = field(default_factory=list)
    is_builtin: bool = False
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rules": [r.to_dict() for r in self.rules],
            "is_builtin": self.is_builtin,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'HighlightTemplate':
        """从字典创建"""
        rules = [HighlightRule.from_dict(r) for r in data.get("rules", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            rules=rules,
            is_builtin=data.get("is_builtin", False),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def save_to_file(self, file_path: str):
        """保存模板到文件"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: str) -> 'HighlightTemplate':
        """从文件加载模板"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


# ========== 预制模板定义 ==========

def get_general_template() -> HighlightTemplate:
    """通用日志模板"""
    return HighlightTemplate(
        id="general",
        name="通用日志",
        description="适用于大多数应用日志",
        is_builtin=True,
        rules=[
            HighlightRule("ERROR", r"\bERROR\b", is_regex=True, foreground="#FF6B6B", background="#4A1D1D", bold=True, priority=10),
            HighlightRule("WARN", r"\bWARN\b", is_regex=True, foreground="#FFD93D", background="#3D3020", bold=True, priority=9),
            HighlightRule("INFO", r"\bINFO\b", is_regex=True, foreground="#6BCF7F", background="", bold=False, priority=7),
            HighlightRule("DEBUG", r"\bDEBUG\b", is_regex=True, foreground="#A8A8A8", background="", bold=False, priority=5),
            HighlightRule("时间戳", r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", is_regex=True, foreground="#7A7A7A", background="", italic=True, priority=3),
        ]
    )


def get_spring_boot_template() -> HighlightTemplate:
    """Spring Boot 日志模板"""
    return HighlightTemplate(
        id="spring-boot",
        name="Spring Boot",
        description="Spring Boot 应用日志",
        is_builtin=True,
        rules=[
            HighlightRule("ERROR", r"\bERROR\b", is_regex=True, foreground="#FF6B6B", background="#4A1D1D", bold=True, priority=10),
            HighlightRule("WARN", r"\bWARN\b", is_regex=True, foreground="#FFD93D", background="#3D3020", bold=True, priority=9),
            HighlightRule("Tomcat 启动", r"Tomcat started on port", is_regex=True, foreground="#6BCF7F", background="#1D4A1D", bold=True, priority=8),
            HighlightRule("SQL 语句", r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b", is_regex=True, foreground="#A78BFA", background="", priority=7),
            HighlightRule("异常堆栈", r"^\s+at\s+", is_regex=True, foreground="#EF4444", background="#3D1D1D", priority=8),
            HighlightRule("Bean 创建", r"Creating bean|Autowiring by", is_regex=True, foreground="#60A5FA", background="", priority=6),
            HighlightRule("Controller", r'Mapped ".*" onto', is_regex=True, foreground="#34D399", background="", priority=5),
        ]
    )


def get_nginx_template() -> HighlightTemplate:
    """Nginx 访问日志模板"""
    return HighlightTemplate(
        id="nginx",
        name="Nginx 访问日志",
        description="Nginx access.log 格式",
        is_builtin=True,
        rules=[
            HighlightRule("5xx 错误", r'" 5\d{2} ', is_regex=True, foreground="#FF6B6B", background="#4A1D1D", bold=True, priority=10),
            HighlightRule("4xx 错误", r'" 4\d{2} ', is_regex=True, foreground="#FFD93D", background="#3D3020", priority=9),
            HighlightRule("2xx 成功", r'" 2\d{2} ', is_regex=True, foreground="#6BCF7F", background="", priority=7),
            HighlightRule("3xx 重定向", r'" 3\d{2} ', is_regex=True, foreground="#60A5FA", background="", priority=7),
            HighlightRule("IP 地址", r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", is_regex=True, foreground="#A78BFA", background="", priority=5),
            HighlightRule("HTTP 方法", r'"(GET|POST|PUT|DELETE|PATCH) ', is_regex=True, foreground="#FFFFFF", background="", bold=True, priority=6),
            HighlightRule("慢响应", r' ([1-9]\d{3,}|\d{4,}\.\d+)$', is_regex=True, foreground="#FB923C", background="#3D2D20", priority=7),
        ]
    )


def get_docker_template() -> HighlightTemplate:
    """Docker 容器日志模板"""
    return HighlightTemplate(
        id="docker",
        name="Docker 容器",
        description="Docker 容器日志",
        is_builtin=True,
        rules=[
            HighlightRule("Container ID", r"[a-f0-9]{12}", is_regex=True, foreground="#60A5FA", background="", priority=6),
            HighlightRule("stdout", r"\[stdout\]", is_regex=True, foreground="#6BCF7F", background="", priority=7),
            HighlightRule("stderr", r"\[stderr\]", is_regex=True, foreground="#FF6B6B", background="", priority=7),
            HighlightRule("Exit code", r"exited with code \d+", is_regex=True, foreground="#FFD93D", background="", bold=True, priority=8),
            HighlightRule("ERROR", r"\bERROR\b", is_regex=True, foreground="#FF6B6B", background="#4A1D1D", bold=True, priority=9),
        ]
    )


def get_test_log_template() -> HighlightTemplate:
    """测试日志模板"""
    return HighlightTemplate(
        id="test-log",
        name="测试日志",
        description="单元测试/集成测试日志",
        is_builtin=True,
        rules=[
            HighlightRule("PASS", r"\b(PASS|PASSED|✓|✅)\b", is_regex=True, foreground="#6BCF7F", background="#1D4A1D", bold=True, priority=10),
            HighlightRule("FAIL", r"\b(FAIL|FAILED|✗|❌)\b", is_regex=True, foreground="#FF6B6B", background="#4A1D1D", bold=True, priority=10),
            HighlightRule("SKIP", r"\b(SKIP|SKIPPED|⊘)\b", is_regex=True, foreground="#FFD93D", background="", priority=8),
            HighlightRule("测试用例", r"(test_\w+|Test\w+::)", is_regex=True, foreground="#60A5FA", background="", bold=True, priority=7),
            HighlightRule("断言", r"Assert(ion)?Error", is_regex=True, foreground="#EF4444", background="", priority=9),
        ]
    )


# ========== 内置模板注册表 ==========
BUILTIN_TEMPLATES = {
    "general": get_general_template,
    "spring-boot": get_spring_boot_template,
    "nginx": get_nginx_template,
    "docker": get_docker_template,
    "test-log": get_test_log_template,
}
