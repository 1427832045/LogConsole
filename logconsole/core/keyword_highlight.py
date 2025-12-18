"""
用户关键词高亮管理器
支持多关键词同时高亮，预制颜色选择，用户模板持久化
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Callable
import json
import os
from pathlib import Path


# 预制高亮颜色 - 温暖色调，适配深色主题
PRESET_COLORS = [
    {"name": "Red", "fg": "#FF6B6B", "bg": "#4A1D1D"},
    {"name": "Orange", "fg": "#FF9F43", "bg": "#4A2D1D"},
    {"name": "Yellow", "fg": "#FFD93D", "bg": "#3D3020"},
    {"name": "Green", "fg": "#6BCF7F", "bg": "#1D4A1D"},
    {"name": "Cyan", "fg": "#4ECDC4", "bg": "#1D3D3D"},
    {"name": "Blue", "fg": "#60A5FA", "bg": "#1D2D4A"},
    {"name": "Purple", "fg": "#A78BFA", "bg": "#2D1D4A"},
    {"name": "Pink", "fg": "#F472B6", "bg": "#4A1D3D"},
    {"name": "White", "fg": "#FFFFFF", "bg": "#3A3A3A"},
    {"name": "Gray", "fg": "#A8A8A8", "bg": "#2A2A2A"},
]


@dataclass
class KeywordHighlight:
    """单个关键词高亮配置"""
    keyword: str
    fg_color: str = "#FF6B6B"
    bg_color: str = "#4A1D1D"
    bold: bool = False
    enabled: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'KeywordHighlight':
        return cls(**data)


@dataclass
class KeywordTemplate:
    """关键词高亮模板"""
    name: str
    keywords: List[KeywordHighlight] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "keywords": [k.to_dict() for k in self.keywords]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'KeywordTemplate':
        keywords = [KeywordHighlight.from_dict(k) for k in data.get("keywords", [])]
        return cls(name=data["name"], keywords=keywords)


class KeywordHighlightManager:
    """关键词高亮管理器"""

    def __init__(self):
        self.keywords: List[KeywordHighlight] = []
        self.templates: Dict[str, KeywordTemplate] = {}
        self._on_change_callbacks: List[Callable] = []
        self._config_dir = Path.home() / ".logconsole"
        self._templates_file = self._config_dir / "keyword_templates.json"
        self._load_templates()

    def add_keyword(self, keyword: str, fg_color: str = "#FF6B6B",
                    bg_color: str = "#4A1D1D", bold: bool = False) -> KeywordHighlight:
        """添加关键词高亮"""
        # 检查是否已存在
        existing = self.find_keyword(keyword)
        if existing:
            existing.fg_color = fg_color
            existing.bg_color = bg_color
            existing.bold = bold
            existing.enabled = True
        else:
            existing = KeywordHighlight(keyword, fg_color, bg_color, bold)
            self.keywords.append(existing)
        self._notify_change()
        return existing

    def remove_keyword(self, keyword: str) -> bool:
        """移除关键词高亮"""
        for i, kw in enumerate(self.keywords):
            if kw.keyword == keyword:
                self.keywords.pop(i)
                self._notify_change()
                return True
        return False

    def find_keyword(self, keyword: str) -> Optional[KeywordHighlight]:
        """查找关键词"""
        for kw in self.keywords:
            if kw.keyword == keyword:
                return kw
        return None

    def toggle_keyword(self, keyword: str) -> bool:
        """切换关键词启用状态"""
        kw = self.find_keyword(keyword)
        if kw:
            kw.enabled = not kw.enabled
            self._notify_change()
            return True
        return False

    def clear_all(self):
        """清除所有关键词"""
        self.keywords.clear()
        self._notify_change()

    def get_enabled_keywords(self) -> List[KeywordHighlight]:
        """获取所有启用的关键词"""
        return [kw for kw in self.keywords if kw.enabled]

    def on_change(self, callback: Callable):
        """注册变更回调"""
        self._on_change_callbacks.append(callback)

    def _notify_change(self):
        """通知变更"""
        for cb in self._on_change_callbacks:
            try:
                cb()
            except Exception:
                pass

    # ========== 模板管理 ==========

    def save_as_template(self, name: str) -> KeywordTemplate:
        """保存当前关键词为模板"""
        template = KeywordTemplate(
            name=name,
            keywords=[KeywordHighlight.from_dict(k.to_dict()) for k in self.keywords]
        )
        self.templates[name] = template
        self._save_templates()
        return template

    def load_template(self, name: str) -> bool:
        """加载模板"""
        if name not in self.templates:
            return False
        template = self.templates[name]
        self.keywords = [KeywordHighlight.from_dict(k.to_dict()) for k in template.keywords]
        self._notify_change()
        return True

    def delete_template(self, name: str) -> bool:
        """删除模板"""
        if name in self.templates:
            del self.templates[name]
            self._save_templates()
            return True
        return False

    def get_template_names(self) -> List[str]:
        """获取所有模板名称"""
        return list(self.templates.keys())

    def _load_templates(self):
        """从文件加载模板"""
        if not self._templates_file.exists():
            return
        try:
            with open(self._templates_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for name, tpl_data in data.items():
                self.templates[name] = KeywordTemplate.from_dict(tpl_data)
        except Exception:
            pass

    def _save_templates(self):
        """保存模板到文件"""
        self._config_dir.mkdir(parents=True, exist_ok=True)
        data = {name: tpl.to_dict() for name, tpl in self.templates.items()}
        with open(self._templates_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
