import os
import json
import time
from datetime import datetime

class ProjectManager:
    def __init__(self):
        self.projects_dir = os.path.join(os.getcwd(), "projects")
        self.projects_file = os.path.join(self.projects_dir, "projects.json")
        self.tasks_file = os.path.join(self.projects_dir, "tasks.json")
        
        # 确保目录存在
        os.makedirs(self.projects_dir, exist_ok=True)
        
        # 初始化数据
        self.projects = self._load_projects()
        self.tasks = self._load_tasks()
    
    def _load_projects(self):
        """加载项目数据"""
        if os.path.exists(self.projects_file):
            with open(self.projects_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_projects(self):
        """保存项目数据"""
        with open(self.projects_file, "w", encoding="utf-8") as f:
            json.dump(self.projects, f, ensure_ascii=False, indent=2)
    
    def _load_tasks(self):
        """加载任务数据"""
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_tasks(self):
        """保存任务数据"""
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def create_project(self, project_data):
        """创建项目"""
        # 生成唯一ID
        project_id = f"project_{int(time.time())}"
        
        # 创建项目对象
        project = {
            "id": project_id,
            "name": project_data.get("name", "新建项目"),
            "description": project_data.get("description", ""),
            "start_date": project_data.get("start_date", datetime.now().strftime("%Y-%m-%d")),
            "end_date": project_data.get("end_date", ""),
            "status": project_data.get("status", "planning"),  # planning, in_progress, completed, on_hold
            "priority": project_data.get("priority", "medium"),  # high, medium, low
            "manager": project_data.get("manager", ""),
            "members": project_data.get("members", []),
            "budget": project_data.get("budget", 0.0),
            "documents": project_data.get("documents", []),
            "progress": project_data.get("progress", 0),  # 0-100
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到项目列表
        self.projects.append(project)
        self._save_projects()
        
        return project
    
    def get_projects(self):
        """获取所有项目"""
        return self.projects
    
    def get_project(self, project_id):
        """获取指定项目"""
        return next((p for p in self.projects if p["id"] == project_id), None)
    
    def update_project(self, project_id, project_data):
        """更新项目"""
        for i, project in enumerate(self.projects):
            if project["id"] == project_id:
                # 更新项目数据
                self.projects[i].update(project_data)
                self.projects[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_projects()
                return self.projects[i]
        return None
    
    def delete_project(self, project_id):
        """删除项目"""
        # 删除项目
        self.projects = [p for p in self.projects if p["id"] != project_id]
        # 删除项目相关任务
        self.tasks = [t for t in self.tasks if t["project_id"] != project_id]
        # 保存数据
        self._save_projects()
        self._save_tasks()
        return True
    
    def add_task(self, task_data):
        """添加任务"""
        # 生成唯一ID
        task_id = f"task_{int(time.time())}"
        
        # 创建任务对象
        task = {
            "id": task_id,
            "project_id": task_data.get("project_id", ""),
            "name": task_data.get("name", "新建任务"),
            "description": task_data.get("description", ""),
            "start_date": task_data.get("start_date", datetime.now().strftime("%Y-%m-%d")),
            "end_date": task_data.get("end_date", ""),
            "status": task_data.get("status", "pending"),  # pending, in_progress, completed, on_hold
            "priority": task_data.get("priority", "medium"),  # high, medium, low
            "assignee": task_data.get("assignee", ""),
            "progress": task_data.get("progress", 0),  # 0-100
            "dependencies": task_data.get("dependencies", []),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到任务列表
        self.tasks.append(task)
        self._save_tasks()
        
        # 更新项目进度
        self._update_project_progress(task["project_id"])
        
        return task
    
    def get_tasks(self, project_id=None):
        """获取任务列表"""
        if project_id:
            return [t for t in self.tasks if t["project_id"] == project_id]
        return self.tasks
    
    def get_task(self, task_id):
        """获取指定任务"""
        return next((t for t in self.tasks if t["id"] == task_id), None)
    
    def update_task(self, task_id, task_data):
        """更新任务"""
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                # 更新任务数据
                project_id = task["project_id"]
                self.tasks[i].update(task_data)
                self.tasks[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_tasks()
                
                # 更新项目进度
                self._update_project_progress(project_id)
                return self.tasks[i]
        return None
    
    def delete_task(self, task_id):
        """删除任务"""
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                project_id = task["project_id"]
                # 删除任务
                del self.tasks[i]
                self._save_tasks()
                
                # 更新项目进度
                self._update_project_progress(project_id)
                return True
        return False
    
    def _update_project_progress(self, project_id):
        """更新项目进度"""
        # 获取项目相关任务
        project_tasks = [t for t in self.tasks if t["project_id"] == project_id]
        if not project_tasks:
            return
        
        # 计算平均进度
        total_progress = sum(t["progress"] for t in project_tasks)
        average_progress = int(total_progress / len(project_tasks))
        
        # 更新项目进度
        for i, project in enumerate(self.projects):
            if project["id"] == project_id:
                self.projects[i]["progress"] = average_progress
                self._save_projects()
                break
    
    def add_document(self, project_id, document_data):
        """添加项目文档"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        # 生成唯一ID
        document_id = f"doc_{int(time.time())}"
        
        # 创建文档对象
        document = {
            "id": document_id,
            "name": document_data.get("name", "新建文档"),
            "type": document_data.get("type", "") ,  # docx, pdf, txt, etc.
            "path": document_data.get("path", ""),
            "description": document_data.get("description", ""),
            "uploaded_by": document_data.get("uploaded_by", ""),
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到项目文档列表
        project["documents"].append(document)
        self.update_project(project_id, project)
        
        return document
    
    def remove_document(self, project_id, document_id):
        """删除项目文档"""
        project = self.get_project(project_id)
        if not project:
            return False
        
        # 从项目文档列表中移除
        project["documents"] = [d for d in project["documents"] if d["id"] != document_id]
        self.update_project(project_id, project)
        return True
    
    def get_projects_by_status(self, status):
        """根据状态获取项目"""
        return [p for p in self.projects if p["status"] == status]
    
    def get_projects_by_manager(self, manager):
        """根据项目经理获取项目"""
        return [p for p in self.projects if p["manager"] == manager]
    
    def get_projects_by_member(self, member):
        """根据项目成员获取项目"""
        return [p for p in self.projects if member in p["members"]]
    
    def update_project_progress(self, project_id, progress):
        """更新项目进度"""
        """
        手动更新项目进度，覆盖自动计算的进度
        
        Args:
            project_id (str): 项目ID
            progress (int): 项目进度，0-100
        
        Returns:
            dict: 更新后的项目信息
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        # 确保进度在0-100之间
        progress = max(0, min(100, progress))
        project["progress"] = progress
        project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_projects()
        
        return project
    
    def get_project_gantt_data(self, project_id):
        """获取项目甘特图数据"""
        """
        获取项目的甘特图数据，包括项目和任务的时间线信息
        
        Args:
            project_id (str): 项目ID
        
        Returns:
            dict: 甘特图数据
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        # 获取项目相关任务
        project_tasks = self.get_tasks(project_id)
        
        gantt_data = {
            "project": {
                "id": project["id"],
                "name": project["name"],
                "start_date": project["start_date"],
                "end_date": project["end_date"],
                "progress": project["progress"],
                "status": project["status"]
            },
            "tasks": []
        }
        
        # 转换任务数据为甘特图格式
        for task in project_tasks:
            gantt_task = {
                "id": task["id"],
                "name": task["name"],
                "start_date": task["start_date"],
                "end_date": task["end_date"],
                "progress": task["progress"],
                "status": task["status"],
                "priority": task["priority"],
                "assignee": task["assignee"],
                "dependencies": task["dependencies"]
            }
            gantt_data["tasks"].append(gantt_task)
        
        return gantt_data
    
    def generate_project_report(self, project_id):
        """生成项目报告"""
        """
        生成项目的综合报告，包括项目信息、任务完成情况、进度分析等
        
        Args:
            project_id (str): 项目ID
        
        Returns:
            dict: 项目报告
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        # 获取项目相关任务
        project_tasks = self.get_tasks(project_id)
        
        # 计算任务统计信息
        total_tasks = len(project_tasks)
        completed_tasks = len([t for t in project_tasks if t["status"] == "completed"])
        in_progress_tasks = len([t for t in project_tasks if t["status"] == "in_progress"])
        pending_tasks = len([t for t in project_tasks if t["status"] == "pending"])
        on_hold_tasks = len([t for t in project_tasks if t["status"] == "on_hold"])
        
        # 计算任务进度统计
        if total_tasks > 0:
            avg_task_progress = sum(t["progress"] for t in project_tasks) / total_tasks
            completed_task_percentage = (completed_tasks / total_tasks) * 100
        else:
            avg_task_progress = 0
            completed_task_percentage = 0
        
        report = {
            "project": project,
            "task_statistics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "pending_tasks": pending_tasks,
                "on_hold_tasks": on_hold_tasks,
                "avg_task_progress": round(avg_task_progress, 2),
                "completed_task_percentage": round(completed_task_percentage, 2)
            },
            "tasks": project_tasks,
            "documents": project.get("documents", []),
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return report
    
    def get_project_statistics(self):
        """获取项目统计信息"""
        """
        获取所有项目的统计信息
        
        Returns:
            dict: 项目统计信息
        """
        total_projects = len(self.projects)
        completed_projects = len([p for p in self.projects if p["status"] == "completed"])
        in_progress_projects = len([p for p in self.projects if p["status"] == "in_progress"])
        planning_projects = len([p for p in self.projects if p["status"] == "planning"])
        on_hold_projects = len([p for p in self.projects if p["status"] == "on_hold"])
        
        # 计算平均项目进度
        total_progress = sum(p["progress"] for p in self.projects)
        avg_progress = round(total_progress / total_projects, 2) if total_projects > 0 else 0
        
        # 计算任务总数
        total_tasks = len(self.tasks)
        
        return {
            "total_projects": total_projects,
            "completed_projects": completed_projects,
            "in_progress_projects": in_progress_projects,
            "planning_projects": planning_projects,
            "on_hold_projects": on_hold_projects,
            "avg_progress": avg_progress,
            "total_tasks": total_tasks
        }
    
    def add_project_milestone(self, project_id, milestone):
        """添加项目里程碑"""
        """
        为项目添加里程碑
        
        Args:
            project_id (str): 项目ID
            milestone (dict): 里程碑信息，包含name, date, description等字段
        
        Returns:
            dict: 更新后的项目信息
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        # 初始化milestones字段（如果不存在）
        if "milestones" not in project:
            project["milestones"] = []
        
        # 生成里程碑ID
        milestone_id = f"milestone_{int(time.time())}"
        
        # 创建里程碑对象
        new_milestone = {
            "id": milestone_id,
            "name": milestone.get("name", "新建里程碑"),
            "date": milestone.get("date", datetime.now().strftime("%Y-%m-%d")),
            "description": milestone.get("description", ""),
            "status": milestone.get("status", "pending"),  # pending, completed, delayed
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加里程碑到项目
        project["milestones"].append(new_milestone)
        project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_projects()
        
        return project
    
    def update_project_milestone(self, project_id, milestone_id, milestone_data):
        """更新项目里程碑"""
        """
        更新项目的指定里程碑
        
        Args:
            project_id (str): 项目ID
            milestone_id (str): 里程碑ID
            milestone_data (dict): 里程碑更新数据
        
        Returns:
            dict: 更新后的项目信息
        """
        project = self.get_project(project_id)
        if not project or "milestones" not in project:
            return None
        
        # 查找里程碑
        for i, milestone in enumerate(project["milestones"]):
            if milestone["id"] == milestone_id:
                # 更新里程碑数据
                project["milestones"][i].update(milestone_data)
                project["milestones"][i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_projects()
                return project
        
        return None
    
    def delete_project_milestone(self, project_id, milestone_id):
        """删除项目里程碑"""
        """
        删除项目的指定里程碑
        
        Args:
            project_id (str): 项目ID
            milestone_id (str): 里程碑ID
        
        Returns:
            dict: 更新后的项目信息
        """
        project = self.get_project(project_id)
        if not project or "milestones" not in project:
            return None
        
        # 过滤掉要删除的里程碑
        project["milestones"] = [m for m in project["milestones"] if m["id"] != milestone_id]
        project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_projects()
        
        return project
