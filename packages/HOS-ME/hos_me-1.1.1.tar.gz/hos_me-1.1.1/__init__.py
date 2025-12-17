# HOS可扩展式办公平台包初始化文件

__version__ = "1.1.1"
__author__ = "HOS Office Platform Team"
__email__ = "hos_office@example.com"
__description__ = "HOS可扩展式办公平台 - 一个基于Flask的多功能办公自动化平台"

# 导出主要组件
from .HOS_ME.app import app
from .HOS_ME.utils.report_generator import Config, ReportGenerator
from .HOS_ME.utils.api_client import APIClient
from .HOS_ME.utils.template_manager import TemplateManager
from .HOS_ME.utils.meeting_manager import MeetingManager
from .HOS_ME.utils.project_manager import ProjectManager
from .HOS_ME.utils.knowledge_base import KnowledgeBase
from .HOS_ME.utils.task_manager import TaskManager
from .HOS_ME.utils.schedule_manager import ScheduleManager
from .HOS_ME.utils.approval_manager import ApprovalManager

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