"""
模板管理器 - 管理高亮模板的加载、保存、切换
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .highlight_template import (
    HighlightTemplate,
    HighlightRule,
    BUILTIN_TEMPLATES
)


class TemplateManager:
    """高亮模板管理器"""

    def __init__(self):
        self.templates: Dict[str, HighlightTemplate] = {}
        self.current_template_id: str = "general"
        self.config_dir = Path.home() / ".logconsole"
        self.templates_dir = self.config_dir / "templates"
        self.config_file = self.config_dir / "config.json"

        # 确保目录存在
        self.config_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)

        # 加载模板
        self.load_builtin_templates()
        self.load_user_templates()
        self.load_config()

    def load_builtin_templates(self):
        """加载所有内置模板"""
        for template_id, template_func in BUILTIN_TEMPLATES.items():
            template = template_func()
            self.templates[template_id] = template

    def load_user_templates(self):
        """加载用户自定义模板"""
        if not self.templates_dir.exists():
            return

        for json_file in self.templates_dir.glob("*.json"):
            try:
                template = HighlightTemplate.load_from_file(str(json_file))
                if template.id not in self.templates:  # 不覆盖内置模板
                    self.templates[template.id] = template
            except Exception as e:
                print(f"加载模板失败 {json_file}: {e}")

    def load_config(self):
        """加载配置（当前模板 ID）"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.current_template_id = config.get("current_template", "general")
            except:
                self.current_template_id = "general"

    def save_config(self):
        """保存配置"""
        config = {"current_template": self.current_template_id}
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def get_current_template(self) -> Optional[HighlightTemplate]:
        """获取当前模板"""
        return self.templates.get(self.current_template_id)

    def get_template(self, template_id: str) -> Optional[HighlightTemplate]:
        """获取指定模板"""
        return self.templates.get(template_id)

    def get_all_templates(self) -> List[HighlightTemplate]:
        """获取所有模板"""
        return list(self.templates.values())

    def get_builtin_templates(self) -> List[HighlightTemplate]:
        """获取内置模板"""
        return [t for t in self.templates.values() if t.is_builtin]

    def get_user_templates(self) -> List[HighlightTemplate]:
        """获取用户模板"""
        return [t for t in self.templates.values() if not t.is_builtin]

    def switch_template(self, template_id: str) -> bool:
        """切换到指定模板"""
        if template_id in self.templates:
            self.current_template_id = template_id
            self.save_config()
            return True
        return False

    def save_template(self, template: HighlightTemplate):
        """保存模板（用户模板）"""
        if template.is_builtin:
            raise ValueError("不能修改内置模板")

        # 更新时间戳
        template.updated_at = datetime.now().isoformat()
        if not template.created_at:
            template.created_at = template.updated_at

        # 保存到文件
        file_path = self.templates_dir / f"{template.id}.json"
        template.save_to_file(str(file_path))

        # 更新内存中的模板
        self.templates[template.id] = template

    def delete_template(self, template_id: str) -> bool:
        """删除用户模板"""
        template = self.templates.get(template_id)
        if not template or template.is_builtin:
            return False

        # 删除文件
        file_path = self.templates_dir / f"{template_id}.json"
        if file_path.exists():
            file_path.unlink()

        # 从内存删除
        del self.templates[template_id]

        # 如果删除的是当前模板，切换到默认模板
        if self.current_template_id == template_id:
            self.current_template_id = "general"
            self.save_config()

        return True

    def export_template(self, template_id: str, file_path: str):
        """导出模板到指定路径"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"模板不存在: {template_id}")

        template.save_to_file(file_path)

    def import_template(self, file_path: str) -> HighlightTemplate:
        """导入模板"""
        template = HighlightTemplate.load_from_file(file_path)

        # 检查 ID 冲突
        if template.id in self.templates:
            # 生成新 ID
            original_id = template.id
            counter = 1
            while f"{original_id}_{counter}" in self.templates:
                counter += 1
            template.id = f"{original_id}_{counter}"

        # 标记为用户模板
        template.is_builtin = False

        # 保存
        self.save_template(template)

        return template

    def create_template(self, name: str, description: str = "") -> HighlightTemplate:
        """创建新模板"""
        # 生成唯一 ID
        import uuid
        template_id = f"custom_{uuid.uuid4().hex[:8]}"

        template = HighlightTemplate(
            id=template_id,
            name=name,
            description=description,
            rules=[],
            is_builtin=False,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        self.templates[template_id] = template
        return template
