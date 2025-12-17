import os
import json
import time
from datetime import datetime

class ApprovalManager:
    def __init__(self):
        self.approvals_dir = os.path.join(os.getcwd(), "approvals")
        self.approval_processes_file = os.path.join(self.approvals_dir, "approval_processes.json")
        self.approval_requests_file = os.path.join(self.approvals_dir, "approval_requests.json")
        self.approval_statuses = ["pending", "in_progress", "approved", "rejected", "canceled"]
        self.approval_actions = ["approve", "reject", "forward", "hold"]
        
        # 确保目录存在
        os.makedirs(self.approvals_dir, exist_ok=True)
        
        # 初始化数据
        self.approval_processes = self._load_approval_processes()
        self.approval_requests = self._load_approval_requests()
    
    def _load_approval_processes(self):
        """加载审批流程数据"""
        if os.path.exists(self.approval_processes_file):
            with open(self.approval_processes_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_approval_processes(self):
        """保存审批流程数据"""
        with open(self.approval_processes_file, "w", encoding="utf-8") as f:
            json.dump(self.approval_processes, f, ensure_ascii=False, indent=2)
    
    def _load_approval_requests(self):
        """加载审批请求数据"""
        if os.path.exists(self.approval_requests_file):
            with open(self.approval_requests_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_approval_requests(self):
        """保存审批请求数据"""
        with open(self.approval_requests_file, "w", encoding="utf-8") as f:
            json.dump(self.approval_requests, f, ensure_ascii=False, indent=2)
    
    def create_approval_process(self, process_data):
        """创建审批流程"""
        # 生成唯一ID
        process_id = f"process_{int(time.time())}"
        
        # 创建审批流程对象
        approval_process = {
            "id": process_id,
            "name": process_data.get("name", "新建审批流程"),
            "description": process_data.get("description", ""),
            "steps": process_data.get("steps", []),
            "creator": process_data.get("creator", ""),
            "is_active": process_data.get("is_active", True),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到审批流程列表
        self.approval_processes.append(approval_process)
        self._save_approval_processes()
        
        return approval_process
    
    def get_approval_processes(self):
        """获取审批流程列表"""
        return self.approval_processes
    
    def get_approval_process(self, process_id):
        """获取指定审批流程"""
        return next((p for p in self.approval_processes if p["id"] == process_id), None)
    
    def update_approval_process(self, process_id, process_data):
        """更新审批流程"""
        for i, process in enumerate(self.approval_processes):
            if process["id"] == process_id:
                self.approval_processes[i].update(process_data)
                self.approval_processes[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_approval_processes()
                return self.approval_processes[i]
        return None
    
    def delete_approval_process(self, process_id):
        """删除审批流程"""
        self.approval_processes = [p for p in self.approval_processes if p["id"] != process_id]
        self._save_approval_processes()
        return True
    
    def create_approval_request(self, request_data):
        """创建审批请求"""
        # 生成唯一ID
        request_id = f"request_{int(time.time())}"
        
        # 验证状态
        status = request_data.get("status", "pending")
        if status not in self.approval_statuses:
            status = "pending"
        
        # 获取审批流程
        process_id = request_data.get("process_id", "")
        process = self.get_approval_process(process_id)
        
        # 初始化当前步骤
        current_step = 0
        approvers = []
        if process and process["steps"]:
            # 获取第一个步骤的审批人
            approvers = process["steps"][0].get("approvers", [])
        
        # 创建审批请求对象
        approval_request = {
            "id": request_id,
            "title": request_data.get("title", "新建审批请求"),
            "description": request_data.get("description", ""),
            "process_id": process_id,
            "process_name": process["name"] if process else "",
            "requester": request_data.get("requester", ""),
            "status": status,
            "current_step": current_step,
            "approvers": approvers,
            "history": [],
            "comments": request_data.get("comments", []),
            "attachments": request_data.get("attachments", []),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到审批请求列表
        self.approval_requests.append(approval_request)
        self._save_approval_requests()
        
        return approval_request
    
    def get_approval_requests(self, filters=None):
        """获取审批请求列表，支持筛选"""
        if not filters:
            return self.approval_requests
        
        filtered_requests = self.approval_requests
        
        # 状态筛选
        if "status" in filters:
            filtered_requests = [r for r in filtered_requests if r["status"] == filters["status"]]
        
        # 请求人筛选
        if "requester" in filters:
            filtered_requests = [r for r in filtered_requests if r["requester"] == filters["requester"]]
        
        # 审批流程筛选
        if "process_id" in filters:
            filtered_requests = [r for r in filtered_requests if r["process_id"] == filters["process_id"]]
        
        return filtered_requests
    
    def get_approval_request(self, request_id):
        """获取指定审批请求"""
        return next((r for r in self.approval_requests if r["id"] == request_id), None)
    
    def update_approval_request(self, request_id, request_data):
        """更新审批请求"""
        for i, request in enumerate(self.approval_requests):
            if request["id"] == request_id:
                # 验证状态
                if "status" in request_data:
                    if request_data["status"] not in self.approval_statuses:
                        del request_data["status"]
                
                self.approval_requests[i].update(request_data)
                self.approval_requests[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_approval_requests()
                return self.approval_requests[i]
        return None
    
    def delete_approval_request(self, request_id):
        """删除审批请求"""
        self.approval_requests = [r for r in self.approval_requests if r["id"] != request_id]
        self._save_approval_requests()
        return True
    
    def handle_approval(self, request_id, action_data):
        """处理审批"""
        """
        处理审批请求，支持批准、拒绝、转发、搁置等操作
        
        Args:
            request_id (str): 审批请求ID
            action_data (dict): 处理数据，包含action, approver, comments等字段
        
        Returns:
            dict: 更新后的审批请求
        """
        approval_request = self.get_approval_request(request_id)
        if not approval_request:
            return None
        
        # 验证操作类型
        action = action_data.get("action", "approve")
        if action not in self.approval_actions:
            action = "approve"
        
        # 获取审批流程
        process = self.get_approval_process(approval_request["process_id"])
        if not process:
            return None
        
        # 创建审批历史记录
        history_record = {
            "id": f"history_{int(time.time())}",
            "action": action,
            "approver": action_data.get("approver", ""),
            "comments": action_data.get("comments", ""),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 更新审批历史
        approval_request["history"].append(history_record)
        
        # 根据操作更新审批状态
        if action == "approve":
            # 检查是否还有下一个步骤
            if approval_request["current_step"] < len(process["steps"]) - 1:
                # 进入下一个步骤
                approval_request["current_step"] += 1
                # 获取下一个步骤的审批人
                approval_request["approvers"] = process["steps"][approval_request["current_step"]].get("approvers", [])
                approval_request["status"] = "in_progress"
            else:
                # 所有步骤已完成，审批通过
                approval_request["status"] = "approved"
                approval_request["approvers"] = []
        elif action == "reject":
            # 审批拒绝
            approval_request["status"] = "rejected"
            approval_request["approvers"] = []
        elif action == "canceled":
            # 审批取消
            approval_request["status"] = "canceled"
            approval_request["approvers"] = []
        
        # 更新审批请求
        approval_request["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.update_approval_request(request_id, approval_request)
    
    def add_approval_comment(self, request_id, comment_data):
        """添加审批评论"""
        approval_request = self.get_approval_request(request_id)
        if not approval_request:
            return None
        
        # 生成评论ID
        comment_id = f"comment_{int(time.time())}"
        
        # 创建评论对象
        comment = {
            "id": comment_id,
            "author": comment_data.get("author", ""),
            "content": comment_data.get("content", ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加评论到审批请求
        approval_request["comments"].append(comment)
        
        # 更新审批请求
        return self.update_approval_request(request_id, approval_request)
    
    def add_approval_attachment(self, request_id, attachment_data):
        """添加审批附件"""
        approval_request = self.get_approval_request(request_id)
        if not approval_request:
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
        
        # 添加附件到审批请求
        approval_request["attachments"].append(attachment)
        
        # 更新审批请求
        return self.update_approval_request(request_id, approval_request)
    
    def get_approval_requests_by_requester(self, requester):
        """根据请求人获取审批请求"""
        return [r for r in self.approval_requests if r["requester"] == requester]
    
    def get_approval_requests_by_approver(self, approver):
        """根据审批人获取审批请求"""
        """
        获取需要当前用户审批的请求
        
        Args:
            approver (str): 审批人
        
        Returns:
            list: 审批请求列表
        """
        return [r for r in self.approval_requests if approver in r["approvers"] and r["status"] in ["pending", "in_progress"]]
    
    def get_approval_statistics(self):
        """获取审批统计信息"""
        total_requests = len(self.approval_requests)
        
        # 按状态统计
        status_stats = {}
        for status in self.approval_statuses:
            status_stats[status] = len([r for r in self.approval_requests if r["status"] == status])
        
        # 按流程统计
        process_stats = {}
        for process in self.approval_processes:
            process_stats[process["name"]] = len([r for r in self.approval_requests if r["process_id"] == process["id"]])
        
        return {
            "total_requests": total_requests,
            "status_stats": status_stats,
            "process_stats": process_stats
        }