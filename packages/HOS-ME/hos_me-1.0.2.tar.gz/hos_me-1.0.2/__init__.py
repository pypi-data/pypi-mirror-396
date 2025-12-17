# HOS可扩展式办公平台包初始化文件

__version__ = "1.0.2"
__author__ = "HOS Office Platform Team"
__email__ = "hos_office@example.com"
__description__ = "HOS可扩展式办公平台 - 一个基于Flask的多功能办公自动化平台"

# 导出主要组件
from .hos_office_platform.app import app
from .hos_office_platform.utils.report_generator import Config, ReportGenerator
from .hos_office_platform.utils.api_client import APIClient
from .hos_office_platform.utils.template_manager import TemplateManager
from .hos_office_platform.utils.meeting_manager import MeetingManager
from .hos_office_platform.utils.project_manager import ProjectManager
from .hos_office_platform.utils.knowledge_base import KnowledgeBase
from .hos_office_platform.utils.task_manager import TaskManager
from .hos_office_platform.utils.schedule_manager import ScheduleManager
from .hos_office_platform.utils.approval_manager import ApprovalManager

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
    "ApprovalManager"
]