# HOS办公平台核心模块初始化文件

from .app import app
from .utils.report_generator import Config, ReportGenerator
from .utils.api_client import APIClient
from .utils.template_manager import TemplateManager
from .utils.meeting_manager import MeetingManager
from .utils.project_manager import ProjectManager
from .utils.knowledge_base import KnowledgeBase
from .utils.task_manager import TaskManager
from .utils.schedule_manager import ScheduleManager
from .utils.approval_manager import ApprovalManager
from .utils.docx_template_parser import DocxTemplateParser
from .utils.complex_template_renderer import ComplexTemplateRenderer

__all__ = [
    "app",
    "Config",
    "ReportGenerator",
    "APIClient",
    "TemplateManager",
    "MeetingManager",
    "ProjectManager",
    "KnowledgeBase",
    "TaskManager",
    "ScheduleManager",
    "ApprovalManager",
    "DocxTemplateParser",
    "ComplexTemplateRenderer"
]
