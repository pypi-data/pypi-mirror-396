import os
import json
import time
from datetime import datetime

class KnowledgeBase:
    def __init__(self):
        self.knowledge_dir = os.path.join(os.getcwd(), "knowledge_base")
        self.documents_file = os.path.join(self.knowledge_dir, "documents.json")
        self.categories_file = os.path.join(self.knowledge_dir, "categories.json")
        self.tags_file = os.path.join(self.knowledge_dir, "tags.json")
        
        # 确保目录存在
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(os.path.join(self.knowledge_dir, "files"), exist_ok=True)
        
        # 初始化数据
        self.documents = self._load_documents()
        self.categories = self._load_categories()
        self.tags = self._load_tags()
    
    def _load_documents(self):
        """加载文档数据"""
        if os.path.exists(self.documents_file):
            with open(self.documents_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_documents(self):
        """保存文档数据"""
        with open(self.documents_file, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
    
    def _load_categories(self):
        """加载分类数据"""
        if os.path.exists(self.categories_file):
            with open(self.categories_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_categories(self):
        """保存分类数据"""
        with open(self.categories_file, "w", encoding="utf-8") as f:
            json.dump(self.categories, f, ensure_ascii=False, indent=2)
    
    def _load_tags(self):
        """加载标签数据"""
        if os.path.exists(self.tags_file):
            with open(self.tags_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_tags(self):
        """保存标签数据"""
        with open(self.tags_file, "w", encoding="utf-8") as f:
            json.dump(self.tags, f, ensure_ascii=False, indent=2)
    
    def create_document(self, document_data):
        """创建文档"""
        # 生成唯一ID
        document_id = f"doc_{int(time.time())}"
        
        # 创建文档对象
        document = {
            "id": document_id,
            "title": document_data.get("title", "新建文档"),
            "content": document_data.get("content", ""),
            "category_id": document_data.get("category_id", ""),
            "tags": document_data.get("tags", []),
            "author": document_data.get("author", ""),
            "file_path": document_data.get("file_path", ""),
            "file_name": document_data.get("file_name", ""),
            "file_type": document_data.get("file_type", ""),
            "version": 1,
            "status": document_data.get("status", "draft"),  # draft, published, archived
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "views": 0,
            "likes": 0
        }
        
        # 添加到文档列表
        self.documents.append(document)
        self._save_documents()
        
        return document
    
    def get_documents(self):
        """获取所有文档"""
        return self.documents
    
    def get_document(self, document_id):
        """获取指定文档"""
        return next((d for d in self.documents if d["id"] == document_id), None)
    
    def update_document(self, document_id, document_data):
        """更新文档"""
        for i, document in enumerate(self.documents):
            if document["id"] == document_id:
                # 更新文档数据
                self.documents[i].update(document_data)
                self.documents[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_documents()
                return self.documents[i]
        return None
    
    def delete_document(self, document_id):
        """删除文档"""
        self.documents = [d for d in self.documents if d["id"] != document_id]
        self._save_documents()
        return True
    
    def search_documents(self, query):
        """搜索文档"""
        results = []
        query_lower = query.lower()
        
        for document in self.documents:
            # 在标题、内容、标签中搜索
            if (query_lower in document["title"].lower() or 
                query_lower in document["content"].lower() or
                any(query_lower in tag.lower() for tag in document["tags"])):
                results.append(document)
        
        return results
    
    def get_documents_by_category(self, category_id):
        """根据分类获取文档"""
        return [d for d in self.documents if d["category_id"] == category_id]
    
    def get_documents_by_tag(self, tag):
        """根据标签获取文档"""
        return [d for d in self.documents if tag in d["tags"]]
    
    def create_category(self, category_data):
        """创建分类"""
        # 生成唯一ID
        category_id = f"cat_{int(time.time())}"
        
        # 创建分类对象
        category = {
            "id": category_id,
            "name": category_data.get("name", "新分类"),
            "description": category_data.get("description", ""),
            "parent_id": category_data.get("parent_id", ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到分类列表
        self.categories.append(category)
        self._save_categories()
        
        return category
    
    def get_categories(self):
        """获取所有分类"""
        return self.categories
    
    def get_category(self, category_id):
        """获取指定分类"""
        return next((c for c in self.categories if c["id"] == category_id), None)
    
    def update_category(self, category_id, category_data):
        """更新分类"""
        for i, category in enumerate(self.categories):
            if category["id"] == category_id:
                # 更新分类数据
                self.categories[i].update(category_data)
                self.categories[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_categories()
                return self.categories[i]
        return None
    
    def delete_category(self, category_id):
        """删除分类"""
        # 先更新该分类下的文档，将其分类ID设为空
        for i, document in enumerate(self.documents):
            if document["category_id"] == category_id:
                self.documents[i]["category_id"] = ""
        
        # 删除分类
        self.categories = [c for c in self.categories if c["id"] != category_id]
        self._save_categories()
        self._save_documents()
        return True
    
    def create_tag(self, tag_data):
        """创建标签"""
        # 检查标签是否已存在
        existing_tag = next((t for t in self.tags if t["name"].lower() == tag_data["name"].lower()), None)
        if existing_tag:
            return existing_tag
        
        # 生成唯一ID
        tag_id = f"tag_{int(time.time())}"
        
        # 创建标签对象
        tag = {
            "id": tag_id,
            "name": tag_data.get("name", "新标签"),
            "description": tag_data.get("description", ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到标签列表
        self.tags.append(tag)
        self._save_tags()
        
        return tag
    
    def get_tags(self):
        """获取所有标签"""
        return self.tags
    
    def get_tag(self, tag_id):
        """获取指定标签"""
        return next((t for t in self.tags if t["id"] == tag_id), None)
    
    def update_tag(self, tag_id, tag_data):
        """更新标签"""
        for i, tag in enumerate(self.tags):
            if tag["id"] == tag_id:
                # 更新标签数据
                self.tags[i].update(tag_data)
                self.tags[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_tags()
                return self.tags[i]
        return None
    
    def delete_tag(self, tag_id):
        """删除标签"""
        # 获取标签名称
        tag = self.get_tag(tag_id)
        if not tag:
            return False
        
        # 从所有文档中移除该标签
        for i, document in enumerate(self.documents):
            if tag["name"] in document["tags"]:
                self.documents[i]["tags"].remove(tag["name"])
        
        # 删除标签
        self.tags = [t for t in self.tags if t["id"] != tag_id]
        self._save_tags()
        self._save_documents()
        return True
    
    def add_view(self, document_id):
        """增加文档浏览量"""
        for i, document in enumerate(self.documents):
            if document["id"] == document_id:
                self.documents[i]["views"] += 1
                self._save_documents()
                return self.documents[i]
        return None
    
    def toggle_like(self, document_id):
        """切换文档点赞状态"""
        for i, document in enumerate(self.documents):
            if document["id"] == document_id:
                self.documents[i]["likes"] += 1
                self._save_documents()
                return self.documents[i]
        return None
    
    def _load_document_versions(self):
        """加载文档版本数据"""
        versions_file = os.path.join(self.knowledge_dir, "document_versions.json")
        if os.path.exists(versions_file):
            with open(versions_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_document_versions(self):
        """保存文档版本数据"""
        versions_file = os.path.join(self.knowledge_dir, "document_versions.json")
        with open(versions_file, "w", encoding="utf-8") as f:
            json.dump(self.document_versions, f, ensure_ascii=False, indent=2)
    
    def __init__(self):
        self.knowledge_dir = os.path.join(os.getcwd(), "knowledge_base")
        self.documents_file = os.path.join(self.knowledge_dir, "documents.json")
        self.categories_file = os.path.join(self.knowledge_dir, "categories.json")
        self.tags_file = os.path.join(self.knowledge_dir, "tags.json")
        self.document_versions_file = os.path.join(self.knowledge_dir, "document_versions.json")
        self.permissions_file = os.path.join(self.knowledge_dir, "permissions.json")
        
        # 确保目录存在
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(os.path.join(self.knowledge_dir, "files"), exist_ok=True)
        
        # 初始化数据
        self.documents = self._load_documents()
        self.categories = self._load_categories()
        self.tags = self._load_tags()
        self.document_versions = self._load_document_versions()
        self.permissions = self._load_permissions()
    
    def _load_permissions(self):
        """加载权限数据"""
        if os.path.exists(self.permissions_file):
            with open(self.permissions_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_permissions(self):
        """保存权限数据"""
        with open(self.permissions_file, "w", encoding="utf-8") as f:
            json.dump(self.permissions, f, ensure_ascii=False, indent=2)
    
    def save_document_version(self, document):
        """保存文档版本"""
        """
        保存文档的当前版本到历史记录中
        
        Args:
            document (dict): 文档对象
        """
        # 创建版本记录
        version_record = {
            "id": f"version_{int(time.time())}",
            "document_id": document["id"],
            "version": document.get("version", 1),
            "title": document["title"],
            "content": document["content"],
            "author": document.get("author", ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_path": document.get("file_path", ""),
            "file_name": document.get("file_name", ""),
            "file_type": document.get("file_type", "")
        }
        
        # 添加到版本记录
        self.document_versions.append(version_record)
        self._save_document_versions()
    
    def update_document(self, document_id, document_data):
        """更新文档（带版本控制）"""
        for i, document in enumerate(self.documents):
            if document["id"] == document_id:
                # 保存当前版本
                self.save_document_version(document)
                
                # 更新文档数据
                self.documents[i].update(document_data)
                
                # 增加版本号
                if "content" in document_data or "file_path" in document_data:
                    self.documents[i]["version"] = self.documents[i].get("version", 1) + 1
                
                self.documents[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_documents()
                return self.documents[i]
        return None
    
    def get_document_versions(self, document_id):
        """获取文档的所有版本"""
        """
        获取指定文档的所有历史版本
        
        Args:
            document_id (str): 文档ID
        
        Returns:
            list: 文档版本列表
        """
        versions = [v for v in self.document_versions if v["document_id"] == document_id]
        # 按版本号降序排序
        versions.sort(key=lambda x: x["version"], reverse=True)
        return versions
    
    def get_document_version(self, version_id):
        """获取指定版本"""
        """
        获取文档的指定版本
        
        Args:
            version_id (str): 版本ID
        
        Returns:
            dict: 版本信息
        """
        return next((v for v in self.document_versions if v["id"] == version_id), None)
    
    def restore_document_version(self, document_id, version_id):
        """恢复文档到指定版本"""
        """
        将文档恢复到指定的历史版本
        
        Args:
            document_id (str): 文档ID
            version_id (str): 要恢复的版本ID
        
        Returns:
            dict: 更新后的文档信息
        """
        # 获取指定版本
        version = self.get_document_version(version_id)
        if not version:
            return None
        
        # 获取当前文档
        for i, document in enumerate(self.documents):
            if document["id"] == document_id:
                # 保存当前版本（作为新版本）
                self.save_document_version(document)
                
                # 恢复到指定版本
                self.documents[i]["title"] = version["title"]
                self.documents[i]["content"] = version["content"]
                self.documents[i]["file_path"] = version["file_path"]
                self.documents[i]["file_name"] = version["file_name"]
                self.documents[i]["file_type"] = version["file_type"]
                
                # 增加版本号
                self.documents[i]["version"] += 1
                self.documents[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self._save_documents()
                return self.documents[i]
        return None
    
    def add_document_permission(self, permission_data):
        """添加文档权限"""
        """
        为文档添加权限
        
        Args:
            permission_data (dict): 权限信息，包含document_id, user_id, role, permissions等字段
        
        Returns:
            dict: 添加的权限信息
        """
        # 生成权限ID
        permission_id = f"permission_{int(time.time())}"
        
        # 创建权限对象
        permission = {
            "id": permission_id,
            "document_id": permission_data["document_id"],
            "user_id": permission_data.get("user_id", ""),
            "role": permission_data.get("role", "reader"),  # reader, editor, admin
            "permissions": permission_data.get("permissions", []),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到权限列表
        self.permissions.append(permission)
        self._save_permissions()
        
        return permission
    
    def get_document_permissions(self, document_id):
        """获取文档的所有权限"""
        """
        获取指定文档的所有权限
        
        Args:
            document_id (str): 文档ID
        
        Returns:
            list: 权限列表
        """
        return [p for p in self.permissions if p["document_id"] == document_id]
    
    def check_document_permission(self, document_id, user_id, permission_type):
        """检查用户是否有指定权限"""
        """
        检查用户是否对文档有指定类型的权限
        
        Args:
            document_id (str): 文档ID
            user_id (str): 用户ID
            permission_type (str): 权限类型，如'read', 'edit', 'delete', 'manage'
        
        Returns:
            bool: 是否有该权限
        """
        # 获取文档权限
        document_permissions = self.get_document_permissions(document_id)
        
        # 检查用户权限
        for perm in document_permissions:
            if perm["user_id"] == user_id:
                # 角色权限映射
                role_permissions = {
                    "reader": ["read"],
                    "editor": ["read", "edit"],
                    "admin": ["read", "edit", "delete", "manage"]
                }
                
                # 检查角色权限
                if permission_type in role_permissions.get(perm["role"], []):
                    return True
                
                # 检查具体权限
                if permission_type in perm.get("permissions", []):
                    return True
        
        # 默认权限：文档作者有所有权限
        document = self.get_document(document_id)
        if document and document.get("author") == user_id:
            return True
        
        # 默认权限：公开文档允许只读访问
        document = self.get_document(document_id)
        if document and document.get("status") == "published":
            if permission_type == "read":
                return True
        
        return False
    
    def update_document_permission(self, permission_id, permission_data):
        """更新文档权限"""
        """
        更新指定的文档权限
        
        Args:
            permission_id (str): 权限ID
            permission_data (dict): 更新的权限数据
        
        Returns:
            dict: 更新后的权限信息
        """
        for i, permission in enumerate(self.permissions):
            if permission["id"] == permission_id:
                self.permissions[i].update(permission_data)
                self.permissions[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_permissions()
                return self.permissions[i]
        return None
    
    def delete_document_permission(self, permission_id):
        """删除文档权限"""
        """
        删除指定的文档权限
        
        Args:
            permission_id (str): 权限ID
        
        Returns:
            bool: 删除是否成功
        """
        self.permissions = [p for p in self.permissions if p["id"] != permission_id]
        self._save_permissions()
        return True
    
    def get_document_statistics(self):
        """获取文档统计信息"""
        """
        获取知识库的统计信息
        
        Returns:
            dict: 统计信息
        """
        total_documents = len(self.documents)
        published_documents = len([d for d in self.documents if d["status"] == "published"])
        draft_documents = len([d for d in self.documents if d["status"] == "draft"])
        archived_documents = len([d for d in self.documents if d["status"] == "archived"])
        
        total_categories = len(self.categories)
        total_tags = len(self.tags)
        total_versions = len(self.document_versions)
        
        # 计算总浏览量和点赞数
        total_views = sum(d.get("views", 0) for d in self.documents)
        total_likes = sum(d.get("likes", 0) for d in self.documents)
        
        return {
            "total_documents": total_documents,
            "published_documents": published_documents,
            "draft_documents": draft_documents,
            "archived_documents": archived_documents,
            "total_categories": total_categories,
            "total_tags": total_tags,
            "total_versions": total_versions,
            "total_views": total_views,
            "total_likes": total_likes
        }
