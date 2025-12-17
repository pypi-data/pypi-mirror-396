import os
import json
import time
from datetime import datetime

class MeetingManager:
    def __init__(self):
        self.meetings_dir = os.path.join(os.getcwd(), "meetings")
        self.meetings_file = os.path.join(self.meetings_dir, "meetings.json")
        self.templates_dir = os.path.join(os.getcwd(), "templates_storage")
        
        # 确保目录存在
        os.makedirs(self.meetings_dir, exist_ok=True)
        
        # 初始化会议数据
        self.meetings = self._load_meetings()
    
    def _load_meetings(self):
        """加载会议数据"""
        if os.path.exists(self.meetings_file):
            with open(self.meetings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_meetings(self):
        """保存会议数据"""
        with open(self.meetings_file, "w", encoding="utf-8") as f:
            json.dump(self.meetings, f, ensure_ascii=False, indent=2)
    
    def create_meeting(self, meeting_data):
        """创建会议"""
        # 生成唯一ID
        meeting_id = f"meeting_{int(time.time())}"
        
        # 创建会议对象
        meeting = {
            "id": meeting_id,
            "title": meeting_data.get("title", "新建会议"),
            "description": meeting_data.get("description", ""),
            "start_time": meeting_data.get("start_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "end_time": meeting_data.get("end_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "location": meeting_data.get("location", ""),
            "attendees": meeting_data.get("attendees", []),
            "organizer": meeting_data.get("organizer", ""),
            "status": meeting_data.get("status", "planned"),  # planned, in_progress, completed
            "agenda": meeting_data.get("agenda", []),
            "minutes": meeting_data.get("minutes", ""),
            "action_items": meeting_data.get("action_items", []),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到会议列表
        self.meetings.append(meeting)
        self._save_meetings()
        
        return meeting
    
    def get_meetings(self):
        """获取所有会议"""
        return self.meetings
    
    def get_meeting(self, meeting_id):
        """获取指定会议"""
        return next((m for m in self.meetings if m["id"] == meeting_id), None)
    
    def update_meeting(self, meeting_id, meeting_data):
        """更新会议"""
        for i, meeting in enumerate(self.meetings):
            if meeting["id"] == meeting_id:
                # 更新会议数据
                self.meetings[i].update(meeting_data)
                self.meetings[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_meetings()
                return self.meetings[i]
        return None
    
    def delete_meeting(self, meeting_id):
        """删除会议"""
        self.meetings = [m for m in self.meetings if m["id"] != meeting_id]
        self._save_meetings()
        return True
    
    def generate_minutes(self, meeting_id, prompt, template_id=None):
        """生成会议纪要"""
        from api_client import APIClient
        from template_manager import TemplateManager
        
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            raise Exception("会议不存在")
        
        # 获取模板
        template_manager = TemplateManager()
        if template_id:
            template_info = template_manager.get_template(template_id)
            if template_info:
                template_content = template_info["content"]
                template_prompt = template_info.get("prompt", "请根据以下模板和会议信息生成会议纪要。")
            else:
                # 使用默认模板
                template_content = template_manager.get_current_template()["content"]
                template_prompt = "请根据以下模板和会议信息生成会议纪要。"
        else:
            # 使用默认模板
            template_content = template_manager.get_current_template()["content"]
            template_prompt = "请根据以下模板和会议信息生成会议纪要。"
        
        # 构建完整提示词
        full_prompt = f"{template_prompt}\n\n会议信息：\n"
        full_prompt += f"标题：{meeting['title']}\n"
        full_prompt += f"时间：{meeting['start_time']} 到 {meeting['end_time']}\n"
        full_prompt += f"地点：{meeting['location']}\n"
        full_prompt += f"主持人：{meeting['organizer']}\n"
        full_prompt += f"参会人员：{', '.join(meeting['attendees'])}\n"
        full_prompt += f"会议议程：{'; '.join(meeting['agenda'])}\n"
        full_prompt += f"补充提示：{prompt}\n\n"
        full_prompt += f"模板：\n{template_content}\n\n"
        full_prompt += "请生成符合模板格式的会议纪要，内容要详细、专业，符合实际会议情况。"
        
        # 调用API生成会议纪要
        api_client = APIClient(config.api_key)  # 使用配置的API密钥
        minutes_content = api_client.generate_report(full_prompt)
        
        # 更新会议纪要
        meeting["minutes"] = minutes_content
        self.update_meeting(meeting_id, meeting)
        
        return minutes_content
    
    def add_action_item(self, meeting_id, action_item):
        """添加行动项"""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return None
        
        action_item_id = f"action_{int(time.time())}"
        action_item = {
            "id": action_item_id,
            "description": action_item.get("description", ""),
            "assigned_to": action_item.get("assigned_to", ""),
            "due_date": action_item.get("due_date", ""),
            "status": action_item.get("status", "pending"),  # pending, in_progress, completed
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        meeting["action_items"].append(action_item)
        self.update_meeting(meeting_id, meeting)
        return action_item
    
    def update_action_item(self, meeting_id, action_item_id, action_item_data):
        """更新行动项"""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return None
        
        for i, action_item in enumerate(meeting["action_items"]):
            if action_item["id"] == action_item_id:
                meeting["action_items"][i].update(action_item_data)
                meeting["action_items"][i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.update_meeting(meeting_id, meeting)
                return meeting["action_items"][i]
        return None
    
    def delete_action_item(self, meeting_id, action_item_id):
        """删除行动项"""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return False
        
        meeting["action_items"] = [ai for ai in meeting["action_items"] if ai["id"] != action_item_id]
        self.update_meeting(meeting_id, meeting)
        return True
    
    def get_meetings_by_status(self, status):
        """根据状态获取会议"""
        return [m for m in self.meetings if m["status"] == status]
    
    def get_meetings_by_date(self, date):
        """根据日期获取会议"""
        return [m for m in self.meetings if m["start_time"].startswith(date)]
    
    def add_attendee(self, meeting_id, attendee):
        """添加参会人员"""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return None
        
        # 检查参会人员是否已存在
        if attendee not in meeting["attendees"]:
            meeting["attendees"].append(attendee)
            self.update_meeting(meeting_id, meeting)
        
        return meeting
    
    def remove_attendee(self, meeting_id, attendee):
        """移除参会人员"""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return None
        
        if attendee in meeting["attendees"]:
            meeting["attendees"].remove(attendee)
            self.update_meeting(meeting_id, meeting)
        
        return meeting
    
    def set_meeting_reminder(self, meeting_id, reminder_time):
        """设置会议提醒"""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return None
        
        meeting["reminder_time"] = reminder_time
        self.update_meeting(meeting_id, meeting)
        return meeting
    
    def get_upcoming_meetings(self, days=7):
        """获取未来几天的会议"""
        from datetime import datetime, timedelta
        
        today = datetime.now()
        future_date = today + timedelta(days=days)
        upcoming_meetings = []
        
        for meeting in self.meetings:
            meeting_start = datetime.strptime(meeting["start_time"], "%Y-%m-%d %H:%M:%S")
            if today <= meeting_start <= future_date and meeting["status"] != "completed":
                upcoming_meetings.append(meeting)
        
        # 按开始时间排序
        upcoming_meetings.sort(key=lambda x: x["start_time"])
        return upcoming_meetings
    
    def generate_meeting_report(self, meeting_id):
        """生成会议报告"""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return None
        
        report = {
            "meeting_id": meeting_id,
            "title": meeting["title"],
            "start_time": meeting["start_time"],
            "end_time": meeting["end_time"],
            "location": meeting["location"],
            "organizer": meeting["organizer"],
            "attendees": meeting["attendees"],
            "agenda": meeting["agenda"],
            "minutes": meeting["minutes"],
            "action_items": meeting["action_items"],
            "status": meeting["status"],
            "created_at": meeting["created_at"],
            "updated_at": meeting["updated_at"]
        }
        
        return report
    
    def get_meeting_statistics(self):
        """获取会议统计信息"""
        total_meetings = len(self.meetings)
        completed_meetings = len([m for m in self.meetings if m["status"] == "completed"])
        ongoing_meetings = len([m for m in self.meetings if m["status"] == "in_progress"])
        planned_meetings = len([m for m in self.meetings if m["status"] == "planned"])
        
        # 计算平均会议时长
        total_duration = 0
        valid_meetings = 0
        from datetime import datetime
        
        for meeting in self.meetings:
            try:
                start = datetime.strptime(meeting["start_time"], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(meeting["end_time"], "%Y-%m-%d %H:%M:%S")
                duration = (end - start).total_seconds() / 60  # 转换为分钟
                total_duration += duration
                valid_meetings += 1
            except:
                continue
        
        avg_duration = round(total_duration / valid_meetings, 2) if valid_meetings > 0 else 0
        
        return {
            "total_meetings": total_meetings,
            "completed_meetings": completed_meetings,
            "ongoing_meetings": ongoing_meetings,
            "planned_meetings": planned_meetings,
            "average_duration": avg_duration
        }
