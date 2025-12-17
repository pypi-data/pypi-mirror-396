import threading
import time
import uuid
from datetime import datetime

class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.tasks_lock = threading.Lock()
        self.task_conditions = {}
    
    def create_task(self, task_type, description, total_steps=1):
        """创建新任务"""
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "type": task_type,
            "description": description,
            "status": "running",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_step": 0,
            "total_steps": total_steps,
            "percentage": 0,
            "result": None,
            "error": None,
            "paused": False
        }
        
        with self.tasks_lock:
            self.tasks[task_id] = task
            self.task_conditions[task_id] = threading.Condition()
        
        return task_id
    
    def get_task(self, task_id):
        """获取任务详情"""
        with self.tasks_lock:
            return self.tasks.get(task_id, None)
    
    def get_all_tasks(self):
        """获取所有任务"""
        with self.tasks_lock:
            return list(self.tasks.values())
    
    def update_task(self, task_id, **kwargs):
        """更新任务状态"""
        with self.tasks_lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                for key, value in kwargs.items():
                    task[key] = value
                task["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 计算百分比
                if "current_step" in kwargs or "total_steps" in kwargs:
                    if task["total_steps"] > 0:
                        task["percentage"] = round((task["current_step"] / task["total_steps"]) * 100, 2)
                
                return True
        return False
    
    def complete_task(self, task_id, result=None):
        """完成任务"""
        return self.update_task(
            task_id,
            status="completed",
            result=result,
            current_step=100,
            percentage=100
        )
    
    def fail_task(self, task_id, error):
        """任务失败"""
        return self.update_task(
            task_id,
            status="failed",
            error=error
        )
    
    def pause_task(self, task_id):
        """暂停任务"""
        if self.update_task(task_id, paused=True, status="paused"):
            with self.task_conditions[task_id]:
                self.task_conditions[task_id].notify()
            return True
        return False
    
    def resume_task(self, task_id):
        """恢复任务"""
        if self.update_task(task_id, paused=False, status="running"):
            with self.task_conditions[task_id]:
                self.task_conditions[task_id].notify()
            return True
        return False
    
    def cancel_task(self, task_id):
        """取消任务"""
        return self.update_task(task_id, status="cancelled")
    
    def wait_for_resume(self, task_id):
        """等待任务恢复"""
        with self.task_conditions[task_id]:
            while self.tasks[task_id]["paused"]:
                self.task_conditions[task_id].wait()
    
    def cleanup_completed_tasks(self):
        """清理已完成的任务"""
        with self.tasks_lock:
            completed_task_ids = [
                task_id for task_id, task in self.tasks.items() 
                if task["status"] in ["completed", "failed", "cancelled"]
            ]
            for task_id in completed_task_ids:
                del self.tasks[task_id]
                del self.task_conditions[task_id]