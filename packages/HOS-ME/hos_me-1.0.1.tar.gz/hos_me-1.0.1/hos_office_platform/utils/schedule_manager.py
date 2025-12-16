import os
import json
import time
from datetime import datetime, timedelta


class ScheduleManager:
    def __init__(self):
        self.schedules_dir = os.path.join(os.getcwd(), "schedules")
        self.schedules_file = os.path.join(
            self.schedules_dir, "schedules.json"
        )
        self.schedule_types = [
            "meeting", "appointment", "event", "deadline", "reminder"
        ]
        self.schedule_statuses = [
            "planned", "in_progress", "completed", "canceled", "postponed"
        ]

        # 确保目录存在
        os.makedirs(self.schedules_dir, exist_ok=True)

        # 初始化数据
        self.schedules = self._load_schedules()
    
    def _load_schedules(self):
        """加载日程数据"""
        if os.path.exists(self.schedules_file):
            with open(self.schedules_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_schedules(self):
        """保存日程数据"""
        with open(self.schedules_file, "w", encoding="utf-8") as f:
            json.dump(self.schedules, f, ensure_ascii=False, indent=2)
    
    def create_schedule(self, schedule_data):
        """创建日程"""
        # 生成唯一ID
        schedule_id = f"schedule_{int(time.time())}"
        
        # 验证类型和状态
        schedule_type = schedule_data.get("type", "meeting")
        if schedule_type not in self.schedule_types:
            schedule_type = "meeting"
        
        status = schedule_data.get("status", "planned")
        if status not in self.schedule_statuses:
            status = "planned"
        
        # 创建日程对象
        schedule = {
            "id": schedule_id,
            "title": schedule_data.get("title", "新建日程"),
            "description": schedule_data.get("description", ""),
            "type": schedule_type,
            "status": status,
            "start_time": schedule_data.get("start_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "end_time": schedule_data.get("end_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "location": schedule_data.get("location", ""),
            "organizer": schedule_data.get("organizer", ""),
            "attendees": schedule_data.get("attendees", []),
            "reminders": schedule_data.get("reminders", []),
            "repeats": schedule_data.get("repeats", False),
            "repeat_type": schedule_data.get("repeat_type", "none"),  # none, daily, weekly, monthly, yearly
            "repeat_end_date": schedule_data.get("repeat_end_date", ""),
            "tags": schedule_data.get("tags", []),
            "links": schedule_data.get("links", []),
            "attachments": schedule_data.get("attachments", []),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到日程列表
        self.schedules.append(schedule)
        self._save_schedules()
        
        return schedule
    
    def get_schedules(self, filters=None):
        """获取日程列表，支持筛选"""
        if not filters:
            return self.schedules
        
        filtered_schedules = self.schedules
        
        # 类型筛选
        if "type" in filters:
            filtered_schedules = [s for s in filtered_schedules if s["type"] == filters["type"]]
        
        # 状态筛选
        if "status" in filters:
            filtered_schedules = [s for s in filtered_schedules if s["status"] == filters["status"]]
        
        # 组织者筛选
        if "organizer" in filters:
            filtered_schedules = [s for s in filtered_schedules if s["organizer"] == filters["organizer"]]
        
        # 参会人员筛选
        if "attendee" in filters:
            filtered_schedules = [s for s in filtered_schedules if filters["attendee"] in s["attendees"]]
        
        # 日期范围筛选
        if "start_date" in filters:
            filtered_schedules = [s for s in filtered_schedules if s["start_time"] >= filters["start_date"]]
        
        if "end_date" in filters:
            filtered_schedules = [s for s in filtered_schedules if s["end_time"] <= filters["end_date"]]
        
        return filtered_schedules
    
    def get_schedule(self, schedule_id):
        """获取指定日程"""
        return next((s for s in self.schedules if s["id"] == schedule_id), None)
    
    def update_schedule(self, schedule_id, schedule_data):
        """更新日程"""
        for i, schedule in enumerate(self.schedules):
            if schedule["id"] == schedule_id:
                # 验证类型和状态
                if "type" in schedule_data:
                    if schedule_data["type"] not in self.schedule_types:
                        del schedule_data["type"]
                
                if "status" in schedule_data:
                    if schedule_data["status"] not in self.schedule_statuses:
                        del schedule_data["status"]
                
                # 更新日程数据
                self.schedules[i].update(schedule_data)
                self.schedules[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_schedules()
                return self.schedules[i]
        return None
    
    def delete_schedule(self, schedule_id):
        """删除日程"""
        self.schedules = [s for s in self.schedules if s["id"] != schedule_id]
        self._save_schedules()
        return True
    
    def add_attendee(self, schedule_id, attendee):
        """添加参会人员"""
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        # 检查参会人员是否已存在
        if attendee not in schedule["attendees"]:
            schedule["attendees"].append(attendee)
            return self.update_schedule(schedule_id, schedule)
        
        return schedule
    
    def remove_attendee(self, schedule_id, attendee):
        """移除参会人员"""
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        if attendee in schedule["attendees"]:
            schedule["attendees"].remove(attendee)
            return self.update_schedule(schedule_id, schedule)
        
        return schedule
    
    def add_reminder(self, schedule_id, reminder):
        """添加提醒"""
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        # 生成提醒ID
        reminder_id = f"reminder_{int(time.time())}"
        
        # 创建提醒对象
        new_reminder = {
            "id": reminder_id,
            "time": reminder.get("time", ""),
            "method": reminder.get("method", "email"),  # email, sms, push
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 初始化reminders字段（如果不存在）
        if "reminders" not in schedule:
            schedule["reminders"] = []
        
        # 添加提醒到日程
        schedule["reminders"].append(new_reminder)
        return self.update_schedule(schedule_id, schedule)
    
    def get_upcoming_schedules(self, days=7):
        """获取未来几天的日程"""
        today = datetime.now()
        future_date = today + timedelta(days=days)
        
        upcoming_schedules = []
        for schedule in self.schedules:
            try:
                start_time = datetime.strptime(schedule["start_time"], "%Y-%m-%d %H:%M:%S")
                if today <= start_time <= future_date and schedule["status"] != "completed" and schedule["status"] != "canceled":
                    upcoming_schedules.append(schedule)
            except:
                continue
        
        # 按开始时间排序
        upcoming_schedules.sort(key=lambda x: x["start_time"])
        return upcoming_schedules
    
    def get_todays_schedules(self):
        """获取今天的日程"""
        today = datetime.now().strftime("%Y-%m-%d")
        return [s for s in self.schedules if s["start_time"].startswith(today) and s["status"] != "completed" and s["status"] != "canceled"]
    
    def check_schedule_conflict(self, start_time, end_time, exclude_schedule_id=None):
        """检查日程冲突"""
        """
        检查给定时间范围内是否存在日程冲突
        
        Args:
            start_time (str): 开始时间，格式为"%Y-%m-%d %H:%M:%S"
            end_time (str): 结束时间，格式为"%Y-%m-%d %H:%M:%S"
            exclude_schedule_id (str, optional): 要排除的日程ID，用于更新日程时避免与自身冲突
        
        Returns:
            list: 冲突的日程列表
        """
        conflicts = []
        
        try:
            new_start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            new_end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # 时间格式错误，返回空列表
            return conflicts
        
        for schedule in self.schedules:
            # 跳过要排除的日程
            if schedule["id"] == exclude_schedule_id:
                continue
            
            try:
                schedule_start = datetime.strptime(schedule["start_time"], "%Y-%m-%d %H:%M:%S")
                schedule_end = datetime.strptime(schedule["end_time"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            
            # 检查时间冲突
            if (new_start < schedule_end and new_end > schedule_start):
                conflicts.append(schedule)
        
        return conflicts
    
    def get_schedule_statistics(self):
        """获取日程统计信息"""
        total_schedules = len(self.schedules)
        
        # 按类型统计
        type_stats = {}
        for schedule_type in self.schedule_types:
            type_stats[schedule_type] = len([s for s in self.schedules if s["type"] == schedule_type])
        
        # 按状态统计
        status_stats = {}
        for status in self.schedule_statuses:
            status_stats[status] = len([s for s in self.schedules if s["status"] == status])
        
        # 今日日程数
        todays_schedules = len(self.get_todays_schedules())
        
        # 即将到来的日程数（未来7天）
        upcoming_schedules = len(self.get_upcoming_schedules(7))
        
        return {
            "total_schedules": total_schedules,
            "type_stats": type_stats,
            "status_stats": status_stats,
            "todays_schedules": todays_schedules,
            "upcoming_schedules": upcoming_schedules
        }
    
    def add_attachment(self, schedule_id, attachment_data):
        """添加日程附件"""
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        # 生成附件ID
        attachment_id = f"attachment_{int(time.time())}"
        
        # 创建附件对象
        attachment = {
            "id": attachment_id,
            "name": attachment_data.get("name", ""),
            "file_path": attachment_data.get("file_path", ""),
            "file_type": attachment_data.get("file_type", ""),
            "file_size": attachment_data.get("file_size", 0),
            "uploaded_by": attachment_data.get("uploaded_by", ""),
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 初始化attachments字段（如果不存在）
        if "attachments" not in schedule:
            schedule["attachments"] = []
        
        # 添加附件到日程
        schedule["attachments"].append(attachment)
        return self.update_schedule(schedule_id, schedule)
    
    def remove_attachment(self, schedule_id, attachment_id):
        """移除日程附件"""
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        # 过滤掉要删除的附件
        schedule["attachments"] = [a for a in schedule.get("attachments", []) if a["id"] != attachment_id]
        return self.update_schedule(schedule_id, schedule)