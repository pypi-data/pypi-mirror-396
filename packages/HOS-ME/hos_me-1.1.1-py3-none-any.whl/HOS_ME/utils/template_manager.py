import os
import json
import shutil
import time
from datetime import datetime

# 导入DOCX解析器
from HOS_ME.utils.docx_template_parser import DocxTemplateParser

class TemplateManager:
    def __init__(self):
        self.templates_dir = os.path.join(os.getcwd(), "templates_storage")
        self.templates_config = os.path.join(self.templates_dir, "templates_config.json")
        
        # 初始化DOCX模板解析器
        self.docx_parser = DocxTemplateParser()
        
        # 确保目录和配置文件存在
        os.makedirs(self.templates_dir, exist_ok=True)
        self._init_config()
        self._ensure_default_template()
    
    def _init_config(self):
        """初始化模板配置文件"""
        if not os.path.exists(self.templates_config):
            default_config = {
                "templates": [],
                "current_template": "default"
            }
            self._save_config(default_config)
    
    def _ensure_default_template(self):
        """确保默认模板存在"""
        # 检查默认模板是否存在于配置中
        config = self._load_config()
        default_exists = any(t["id"] == "default" for t in config["templates"])
        
        if not default_exists:
            # 使用内置的默认模板内容
            default_content = """# 【结构化周报模板】

## 一、基本信息
| 项目 | 内容 |
|------|------|
| **报告类型** | 周报 |
| **周数** | 第{周数}周 |
| **时间范围** | {开始日期} ~ {结束日期} |
| **姓名** | {姓名} |
| **部门** | {部门} |
| **岗位** | {岗位} |
| **报告日期** | {报告日期} |

## 二、本周工作概述
### 2.1 工作目标完成情况
- ✅ 已完成目标：{已完成目标数量}/{总目标数量}
- 🟡 部分完成：{部分完成目标数量}
- ❌ 未完成：{未完成目标数量}

### 2.2 核心工作内容
| 工作类别 | 完成情况 | 关键成果 |
|----------|----------|----------|
| 日常工作 | {日常工作完成情况} | {日常工作成果} |
| 项目工作 | {项目工作完成情况} | {项目工作成果} |
| 创新工作 | {创新工作完成情况} | {创新工作成果} |
| 协作工作 | {协作工作完成情况} | {协作工作成果} |

## 三、详细工作内容
### 3.1 主要任务执行情况
| 任务ID | 任务名称 | 任务描述 | 责任主体 | 计划完成时间 | 实际完成时间 | 完成状态 | 完成百分比 | 备注 |
|--------|----------|----------|----------|--------------|--------------|----------|------------|------|
| {任务1ID} | {任务1名称} | {任务1描述} | {任务1责任人} | {任务1计划时间} | {任务1实际时间} | {任务1状态} | {任务1百分比} | {任务1备注} |
| {任务2ID} | {任务2名称} | {任务2描述} | {任务2责任人} | {任务2计划时间} | {任务2实际时间} | {任务2状态} | {任务2百分比} | {任务2备注} |
| {任务3ID} | {任务3名称} | {任务3描述} | {任务3责任人} | {任务3计划时间} | {任务3实际时间} | {任务3状态} | {任务3百分比} | {任务3备注} |

## 四、遇到的问题与解决方案
### 4.1 问题列表
| 问题ID | 问题描述 | 影响范围 | 严重程度 | 优先级 | 状态 |
|--------|----------|----------|----------|--------|------|
| {问题1ID} | {问题1描述} | {问题1影响} | {问题1严重度} | {问题1优先级} | {问题1状态} |
| {问题2ID} | {问题2描述} | {问题2影响} | {问题2严重度} | {问题2优先级} | {问题2状态} |
| {问题3ID} | {问题3描述} | {问题3影响} | {问题3严重度} | {问题3优先级} | {问题3状态} |

### 4.2 解决方案
| 问题ID | 解决方案 | 实施人 | 完成时间 | 效果评估 |
|--------|----------|--------|----------|----------|
| {问题1ID} | {问题1解决方案} | {问题1实施人} | {问题1解决时间} | {问题1效果} |
| {问题2ID} | {问题2解决方案} | {问题2实施人} | {问题2解决时间} | {问题2效果} |
| {问题3ID} | {问题3解决方案} | {问题3实施人} | {问题3解决时间} | {问题3效果} |

## 五、下周工作计划
### 5.1 工作计划安排
| 任务ID | 任务名称 | 任务描述 | 责任主体 | 计划开始时间 | 计划完成时间 | 优先级 | 所需资源 | 关联项目 |
|--------|----------|----------|----------|--------------|--------------|--------|----------|----------|
| {下周任务1ID} | {下周任务1名称} | {下周任务1描述} | {下周任务1责任人} | {下周任务1开始时间} | {下周任务1完成时间} | {下周任务1优先级} | {下周任务1资源} | {下周任务1关联项目} |
| {下周任务2ID} | {下周任务2名称} | {下周任务2描述} | {下周任务2责任人} | {下周任务2开始时间} | {下周任务2完成时间} | {下周任务2优先级} | {下周任务2资源} | {下周任务2关联项目} |
| {下周任务3ID} | {下周任务3名称} | {下周任务3描述} | {下周任务3责任人} | {下周任务3开始时间} | {下周任务3完成时间} | {下周任务3优先级} | {下周任务3资源} | {下周任务3关联项目} |

### 5.2 重点关注事项
1. **{重点事项1}**：{重点事项1描述}，预计影响{重点事项1影响}
2. **{重点事项2}**：{重点事项2描述}，需要协调{重点事项2协调资源}
3. **{重点事项3}**：{重点事项3描述}，风险等级{重点事项3风险等级}

### 5.3 资源需求
- **人力资源**：{所需人力资源}
- **物资资源**：{所需物资资源}
- **技术资源**：{所需技术资源}
- **预算需求**：{所需预算}

## 六、经验总结与改进建议
### 6.1 工作收获与经验
1. **{收获1}**：{收获1详细描述}
2. **{收获2}**：{收获2详细描述}
3. **{收获3}**：{收获3详细描述}

### 6.2 改进建议
1. **{改进建议1}**：{改进建议1详细描述}，预计提升{改进建议1预期效果}
2. **{改进建议2}**：{改进建议2详细描述}，预计解决{改进建议2预期问题}
3. **{改进建议3}**：{改进建议3详细描述}，预计优化{改进建议3预期流程}

## 七、其他事项
### 7.1 需协调事项
- {需协调事项1}
- {需协调事项2}
- {需协调事项3}

### 7.2 沟通与协作
- **内部沟通**：{内部沟通情况}
- **外部协作**：{外部协作情况}

### 7.3 学习与成长
- 本周学习：{本周学习内容}
- 技能提升：{技能提升情况}
- 认证考试：{认证考试情况}

## 八、附件与参考资料
1. [{附件1名称}]({附件1链接})
2. [{附件2名称}]({附件2链接})
3. [{参考资料1名称}]({参考资料1链接})

---
*本周报遵循结构化模板生成，由HOS办公平台提供技术支持*"""
            self._save_template("default", "默认周报模板", default_content)
            
            # 更新配置
            template = {
                "id": "default",
                "name": "默认周报模板",
                "description": "系统默认的周报模板",
                "type": "weekly_report",
                "output_format": "txt",
                "prompt": "请根据以下模板和提示词生成专业的周报，内容要详细、具体、符合实际工作情况。",
                "format_settings": {
                    "font_name": "微软雅黑",
                    "font_size": 12,
                    "line_spacing": 1.5,
                    "margin": {
                        "top": 2.54,
                        "right": 2.54,
                        "bottom": 2.54,
                        "left": 2.54
                    }
                },
                "batch_settings": {
                    "enabled": True,
                    "delimiter": "\n",
                    "max_batch_size": 10
                },
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "is_default": True
            }
            config["templates"].append(template)
            config["current_template"] = "default"
            self._save_config(config)
        
        # 添加更多初始化模板
        self._add_additional_templates()
    
    def _add_additional_templates(self):
        """添加更多初始化模板"""
        config = self._load_config()
        
        # 检查模板是否已存在
        existing_template_ids = [t["id"] for t in config["templates"]]
        
        # 模板列表
        templates_to_add = [
            {
                "id": "meeting_minutes",
                "name": "会议纪要模板",
                "description": "标准的会议纪要模板",
                "type": "meeting_minutes",
                "output_format": "txt",
                "prompt": "请根据会议内容生成详细的会议纪要，包括会议基本信息、讨论内容、决议事项和后续行动。",
                "content": "# 会议纪要\n\n## 一、会议基本信息\n| 项目 | 内容 |\n|------|------|\n| **会议主题** | {会议主题} |\n| **会议时间** | {会议时间} |\n| **会议地点** | {会议地点} |\n| **主持人** | {主持人} |\n| **记录人** | {记录人} |\n| **参会人员** | {参会人员} |\n| **缺席人员** | {缺席人员} |\n\n## 二、会议议程\n1. {议程1}\n2. {议程2}\n3. {议程3}\n\n## 三、讨论内容\n### 3.1 议题1：{议题1名称}\n- **讨论要点**：{议题1讨论要点}\n- **各方观点**：\n  - {参会人1}：{观点1}\n  - {参会人2}：{观点2}\n- **达成共识**：{议题1共识}\n\n### 3.2 议题2：{议题2名称}\n- **讨论要点**：{议题2讨论要点}\n- **各方观点**：\n  - {参会人3}：{观点3}\n  - {参会人4}：{观点4}\n- **达成共识**：{议题2共识}\n\n## 四、决议事项\n| 序号 | 决议内容 | 责任部门/人 | 完成时限 | 跟进情况 |\n|------|----------|--------------|----------|----------|\n| 1 | {决议1} | {责任方1} | {时限1} | {跟进1} |\n| 2 | {决议2} | {责任方2} | {时限2} | {跟进2} |\n| 3 | {决议3} | {责任方3} | {时限3} | {跟进3} |\n\n## 五、后续行动计划\n| 序号 | 行动项 | 责任部门/人 | 完成时限 | 优先级 |\n|------|--------|--------------|----------|--------|\n| 1 | {行动1} | {责任方4} | {时限4} | {优先级1} |\n| 2 | {行动2} | {责任方5} | {时限5} | {优先级2} |\n| 3 | {行动3} | {责任方6} | {时限6} | {优先级3} |\n\n## 六、其他事项\n- {其他事项1}\n- {其他事项2}\n\n## 七、会议结束\n- **结束时间**：{结束时间}\n- **下次会议时间**：{下次会议时间}\n- **下次会议主题**：{下次会议主题}\n\n---\n*本会议纪要由HOS办公平台生成*"
            },
            {
                "id": "project_plan",
                "name": "项目计划模板",
                "description": "完整的项目计划模板",
                "type": "project_plan",
                "output_format": "txt",
                "prompt": "请根据项目需求生成详细的项目计划，包括项目目标、范围、时间安排、资源分配和风险管理。",
                "content": "# 项目计划\n\n## 一、项目基本信息\n| 项目 | 内容 |\n|------|------|\n| **项目名称** | {项目名称} |\n| **项目编号** | {项目编号} |\n| **项目类型** | {项目类型} |\n| **项目负责人** | {项目负责人} |\n| **项目团队** | {项目团队} |\n| **开始日期** | {开始日期} |\n| **结束日期** | {结束日期} |\n| **总预算** | {总预算} |\n\n## 二、项目目标\n### 2.1 总体目标\n{总体目标}\n\n### 2.2 具体目标\n1. {具体目标1}\n2. {具体目标2}\n3. {具体目标3}\n\n## 三、项目范围\n### 3.1 包含范围\n- {包含范围1}\n- {包含范围2}\n- {包含范围3}\n\n### 3.2 排除范围\n- {排除范围1}\n- {排除范围2}\n- {排除范围3}\n\n## 四、项目时间计划\n### 4.1 里程碑计划\n| 里程碑 | 预计完成时间 | 负责人 | 交付物 |\n|--------|--------------|--------|--------|\n| {里程碑1} | {时间1} | {负责人1} | {交付物1} |\n| {里程碑2} | {时间2} | {负责人2} | {交付物2} |\n| {里程碑3} | {时间3} | {负责人3} | {交付物3} |\n\n### 4.2 详细任务计划\n| 任务ID | 任务名称 | 任务描述 | 负责人 | 开始时间 | 结束时间 | 前置任务 | 资源需求 | 状态 |\n|--------|----------|----------|--------|----------|----------|----------|----------|------|\n| {任务ID1} | {任务1} | {描述1} | {负责人4} | {开始1} | {结束1} | {前置1} | {资源1} | {状态1} |\n| {任务ID2} | {任务2} | {描述2} | {负责人5} | {开始2} | {结束2} | {前置2} | {资源2} | {状态2} |\n| {任务ID3} | {任务3} | {描述3} | {负责人6} | {开始3} | {结束3} | {前置3} | {资源3} | {状态3} |\n\n## 五、资源分配\n### 5.1 人力资源\n| 角色 | 人数 | 姓名 | 职责 | 工作时间 |\n|------|------|------|------|----------|\n| {角色1} | {人数1} | {姓名1} | {职责1} | {时间占比1} |\n| {角色2} | {人数2} | {姓名2} | {职责2} | {时间占比2} |\n\n### 5.2 物资资源\n| 资源名称 | 数量 | 规格 | 用途 | 来源 | 成本 |\n|----------|------|------|------|------|------|\n| {资源名称1} | {数量1} | {规格1} | {用途1} | {来源1} | {成本1} |\n| {资源名称2} | {数量2} | {规格2} | {用途2} | {来源2} | {成本2} |\n\n### 5.3 技术资源\n| 资源类型 | 资源名称 | 用途 | 负责人 |\n|----------|----------|------|--------|\n| {技术类型1} | {技术1} | {用途3} | {负责人7} |\n| {技术类型2} | {技术2} | {用途4} | {负责人8} |\n\n## 六、风险管理\n### 6.1 风险识别\n| 风险ID | 风险描述 | 影响程度 | 发生概率 | 优先级 | 风险类型 |\n|--------|----------|----------|----------|--------|----------|\n| {风险ID1} | {风险描述1} | {影响1} | {概率1} | {优先级1} | {类型1} |\n| {风险ID2} | {风险描述2} | {影响2} | {概率2} | {优先级2} | {类型2} |\n\n### 6.2 风险应对措施\n| 风险ID | 风险描述 | 应对策略 | 责任部门/人 | 完成时限 | 资源需求 |\n|--------|----------|----------|--------------|----------|----------|\n| {风险ID1} | {风险描述1} | {应对1} | {责任方1} | {时限1} | {资源4} |\n| {风险ID2} | {风险描述2} | {应对2} | {责任方2} | {时限2} | {资源5} |\n\n## 七、沟通计划\n### 7.1 沟通渠道\n| 沟通对象 | 沟通方式 | 沟通频率 | 负责人 |\n|----------|----------|----------|--------|\n| {对象1} | {方式1} | {频率1} | {负责人9} |\n| {对象2} | {方式2} | {频率2} | {负责人10} |\n\n### 7.2 报告机制\n| 报告类型 | 报告内容 | 报告频率 | 提交对象 | 负责人 |\n|----------|----------|----------|----------|--------|\n| {报告类型1} | {内容1} | {频率3} | {对象3} | {负责人11} |\n| {报告类型2} | {内容2} | {频率4} | {对象4} | {负责人12} |\n\n## 八、质量保证计划\n### 8.1 质量标准\n{质量标准}\n\n### 8.2 质量控制措施\n| 阶段 | 质量控制活动 | 负责人 | 验收标准 |\n|------|--------------|--------|----------|\n| {阶段1} | {活动1} | {负责人13} | {标准1} |\n| {阶段2} | {活动2} | {负责人14} | {标准2} |\n\n## 九、项目验收\n### 9.1 验收标准\n{验收标准}\n\n### 9.2 验收流程\n{验收流程}\n\n### 9.3 验收文档\n{验收文档}\n\n## 十、项目关闭\n### 10.1 关闭条件\n{关闭条件}\n\n### 10.2 关闭流程\n{关闭流程}\n\n### 10.3 项目总结\n{项目总结}\n\n---\n*本项目计划由HOS办公平台生成*"
            },
            {
                "id": "requirement_doc",
                "name": "需求文档模板",
                "description": "详细的需求文档模板",
                "type": "requirement_doc",
                "output_format": "txt",
                "prompt": "请根据业务需求生成完整的需求文档，包括功能需求、非功能需求、数据需求和验收标准。",
                "content": "# 需求文档\n\n## 一、文档基本信息\n| 项目 | 内容 |\n|------|------|\n| **文档名称** | {文档名称} |\n| **文档编号** | {文档编号} |\n| **版本** | {版本} |\n| **编写人** | {编写人} |\n| **审核人** | {审核人} |\n| **批准人** | {批准人} |\n| **编写日期** | {编写日期} |\n| **生效日期** | {生效日期} |\n\n## 二、项目概述\n### 2.1 项目背景\n{项目背景}\n\n### 2.2 项目目标\n{项目目标}\n\n### 2.3 术语定义\n| 术语 | 解释 |\n|------|------|\n| {术语1} | {解释1} |\n| {术语2} | {解释2} |\n\n## 三、功能需求\n### 3.1 功能模块列表\n| 模块名称 | 功能描述 | 优先级 | 负责人 |\n|----------|----------|--------|--------|\n| {模块1} | {描述1} | {优先级1} | {负责人1} |\n| {模块2} | {描述2} | {优先级2} | {负责人2} |\n\n### 3.2 详细功能需求\n#### 3.2.1 功能点1：{功能名称1}\n- **功能描述**：{功能描述1}\n- **输入**：{输入1}\n- **输出**：{输出1}\n- **流程**：{流程1}\n- **优先级**：{优先级3}\n- **验收标准**：{验收标准1}\n\n#### 3.2.2 功能点2：{功能名称2}\n- **功能描述**：{功能描述2}\n- **输入**：{输入2}\n- **输出**：{输出2}\n- **流程**：{流程2}\n- **优先级**：{优先级4}\n- **验收标准**：{验收标准2}\n\n## 四、非功能需求\n### 4.1 性能需求\n| 需求项 | 具体要求 |\n|--------|----------|\n| {性能项1} | {要求1} |\n| {性能项2} | {要求2} |\n\n### 4.2 安全需求\n| 需求项 | 具体要求 |\n|--------|----------|\n| {安全项1} | {要求3} |\n| {安全项2} | {要求4} |\n\n### 4.3 可用性需求\n| 需求项 | 具体要求 |\n|--------|----------|\n| {可用项1} | {要求5} |\n| {可用项2} | {要求6} |\n\n### 4.4 可扩展性需求\n| 需求项 | 具体要求 |\n|--------|----------|\n| {扩展项1} | {要求7} |\n| {扩展项2} | {要求8} |\n\n## 五、数据需求\n### 5.1 数据实体\n| 实体名称 | 描述 | 主要字段 |\n|----------|------|----------|\n| {实体1} | {描述3} | {字段1} |\n| {实体2} | {描述4} | {字段2} |\n\n### 5.2 数据关系\n{数据关系图描述}\n\n### 5.3 数据流转\n{数据流转图描述}\n\n## 六、验收标准\n### 6.1 功能验收标准\n| 功能点 | 验收标准 | 测试方法 |\n|--------|----------|----------|\n| {功能1} | {标准1} | {方法1} |\n| {功能2} | {标准2} | {方法2} |\n\n### 6.2 非功能验收标准\n| 需求项 | 验收标准 | 测试方法 |\n|--------|----------|----------|\n| {非功能1} | {标准3} | {方法3} |\n| {非功能2} | {标准4} | {方法4} |\n\n## 七、风险与依赖\n### 7.1 风险识别\n| 风险ID | 风险描述 | 影响程度 | 发生概率 | 优先级 | 应对措施 |\n|--------|----------|----------|----------|--------|----------|\n| {风险1} | {描述5} | {影响1} | {概率1} | {优先级5} | {措施1} |\n| {风险2} | {描述6} | {影响2} | {概率2} | {优先级6} | {措施2} |\n\n### 7.2 依赖关系\n| 依赖项 | 依赖类型 | 依赖描述 | 影响 |\n|--------|----------|----------|------|\n| {依赖1} | {类型1} | {描述7} | {影响3} |\n| {依赖2} | {类型2} | {描述8} | {影响4} |\n\n## 八、附录\n### 8.1 参考文档\n{参考文档}\n\n### 8.2 相关图表\n{相关图表}\n\n### 8.3 变更记录\n| 版本 | 变更内容 | 变更人 | 变更日期 | 审批人 |\n|------|----------|--------|----------|--------|\n| {版本1} | {变更1} | {变更人1} | {日期1} | {审批人1} |\n| {版本2} | {变更2} | {变更人2} | {日期2} | {审批人2} |\n\n---\n*本需求文档由HOS办公平台生成*"
            },
            {
                "id": "company_secret",
                "name": "公司机密文件模板",
                "description": "公司机密文件专用模板",
                "type": "company_secret",
                "output_format": "txt",
                "prompt": "请根据内容生成符合公司机密要求的文档，包含保密标识和水印。",
                "content": "# 【公司机密】{文档标题}\n\n---\n**机密等级**：{机密等级}\n**保密期限**：{保密期限}\n**发放范围**：{发放范围}\n**文档编号**：{文档编号}\n**版本**：{版本}\n**最后更新**：{更新日期}\n---\n\n## 一、{章节1标题}\n{章节1内容}\n\n## 二、{章节2标题}\n{章节2内容}\n\n## 三、{章节3标题}\n{章节3内容}\n\n---\n\n**⚠️ 保密提醒**\n本文件包含公司机密信息，仅限授权人员查阅。未经授权，不得复制、传播或向第三方披露本文件内容。如有违反，将追究法律责任。\n\n**水印**：{公司名称} 机密文件 {当前日期}\n\n---\n*本机密文件由HOS办公平台生成*"
            }
        ]
        
        # 添加不存在的模板
        for template_data in templates_to_add:
            if template_data["id"] not in existing_template_ids:
                # 保存模板内容
                self._save_template(template_data["id"], template_data["name"], template_data["content"])
                
                # 添加到配置
                template = {
                    "id": template_data["id"],
                    "name": template_data["name"],
                    "description": template_data["description"],
                    "type": template_data["type"],
                    "output_format": template_data["output_format"],
                    "prompt": template_data["prompt"],
                    "format_settings": {
                        "font_name": "微软雅黑",
                        "font_size": 12,
                        "line_spacing": 1.5,
                        "margin": {
                            "top": 2.54,
                            "right": 2.54,
                            "bottom": 2.54,
                            "left": 2.54
                        }
                    },
                    "batch_settings": {
                        "enabled": True,
                        "delimiter": "\n",
                        "max_batch_size": 10
                    },
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "is_default": False
                }
                config["templates"].append(template)
        
        # 保存更新后的配置
        self._save_config(config)
    

    
    def _load_config(self):
        """加载模板配置"""
        with open(self.templates_config, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_config(self, config):
        """保存模板配置"""
        with open(self.templates_config, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _save_template(self, template_id, template_name, content):
        """保存模板文件"""
        template_path = os.path.join(self.templates_dir, f"{template_id}.txt")
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _read_template(self, template_id):
        """读取模板内容"""
        template_path = os.path.join(self.templates_dir, f"{template_id}.txt")
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        return None
    
    def get_templates(self):
        """获取所有模板列表"""
        config = self._load_config()
        return config["templates"]
    
    def get_current_template(self):
        """获取当前使用的模板"""
        config = self._load_config()
        current_id = config["current_template"]
        content = self._read_template(current_id)
        return {
            "id": current_id,
            "content": content
        }
    
    def get_template(self, template_id):
        """获取指定模板"""
        config = self._load_config()
        template = next((t for t in config["templates"] if t["id"] == template_id), None)
        if template:
            template["content"] = self._read_template(template_id)
        return template
    
    def create_template(self, name, content, description="", template_type="weekly_report", output_format="txt", prompt="", structure=None):
        """创建新模板"""
        template_id = f"template_{int(time.time())}"
        config = self._load_config()
        
        # 保存模板文件
        self.save_template(template_id, name, content, structure)
        
        # 更新配置
        template = {
            "id": template_id,
            "name": name,
            "description": description,
            "type": template_type,
            "output_format": output_format,
            "prompt": prompt or "请根据以下模板和提示词生成专业的文档，内容要详细、具体、符合实际工作情况。",
            "format_settings": {
                "font_name": "微软雅黑",
                "font_size": 12,
                "line_spacing": 1.5,
                "margin": {
                    "top": 2.54,
                    "right": 2.54,
                    "bottom": 2.54,
                    "left": 2.54
                }
            },
            "batch_settings": {
                "enabled": True,
                "delimiter": "\n",
                "max_batch_size": 10
            },
            "structure": structure or {},
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_default": False
        }
        config["templates"].append(template)
        self._save_config(config)
        
        return template
    
    def update_template(self, template_id, name=None, content=None, description=None, template_type=None, output_format=None, prompt=None, format_settings=None, batch_settings=None, structure=None):
        """更新模板"""
        config = self._load_config()
        template = next((t for t in config["templates"] if t["id"] == template_id), None)
        
        if not template:
            return None
        
        # 更新模板文件（如果提供了内容）
        if content is not None:
            self.save_template(template_id, name or template["name"], content, structure)
        
        # 更新配置
        if name:
            template["name"] = name
        if description:
            template["description"] = description
        if template_type:
            template["type"] = template_type
        if output_format:
            template["output_format"] = output_format
        if prompt:
            template["prompt"] = prompt
        if format_settings:
            template["format_settings"] = {**template.get("format_settings", {}), **format_settings}
        if batch_settings:
            template["batch_settings"] = {**template.get("batch_settings", {}), **batch_settings}
        if structure is not None:
            template["structure"] = structure
        template["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 更新配置文件
        self._save_config(config)
        # 重新读取模板内容和结构
        content, template_structure = self._read_template(template_id)
        template["content"] = content
        template["structure"] = template_structure or template.get("structure", {})
        return template
    
    def delete_template(self, template_id):
        """删除模板"""
        # 不能删除默认模板
        if template_id == "default":
            return False
        
        config = self._load_config()
        template = next((t for t in config["templates"] if t["id"] == template_id), None)
        
        if not template:
            return False
        
        # 删除模板文件
        template_path = os.path.join(self.templates_dir, f"{template_id}.txt")
        if os.path.exists(template_path):
            os.remove(template_path)
        
        # 从配置中移除
        config["templates"] = [t for t in config["templates"] if t["id"] != template_id]
        
        # 如果删除的是当前模板，切换到默认模板
        if config["current_template"] == template_id:
            config["current_template"] = "default"
        
        self._save_config(config)
        return True
    
    def set_current_template(self, template_id):
        """设置当前使用的模板"""
        config = self._load_config()
        template = next((t for t in config["templates"] if t["id"] == template_id), None)
        
        if template:
            config["current_template"] = template_id
            self._save_config(config)
            return True
        return False
    
    def import_template(self, name, content, description="", template_type="weekly_report", output_format="txt", prompt=""):
        """导入模板"""
        return self.create_template(name, content, description, template_type, output_format, prompt)
    
    def import_docx_template(self, file_path, name, description="", template_type="weekly_report", output_format="docx", prompt=""):
        """
        导入DOCX模板
        
        Args:
            file_path: DOCX文件路径
            name: 模板名称
            description: 模板描述
            template_type: 模板类型
            output_format: 输出格式
            prompt: 提示词
            
        Returns:
            dict: 导入的模板信息
        """
        try:
            # 解析DOCX文件
            parse_result = self.docx_parser.parse_docx(file_path)
            
            if not parse_result['success']:
                return None
            
            # 生成模板配置
            template_config = self.docx_parser.generate_template_config(
                file_path, name, template_type
            )
            
            if not template_config['success']:
                return None
            
            template = template_config['template']
            template_id = template['id']
            
            # 保存模板配置
            config_path = os.path.join(self.templates_dir, f'{template_id}_config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            
            # 更新配置
            config = self._load_config()
            config["templates"].append(template)
            self._save_config(config)
            
            return template
        except Exception as e:
            print(f"导入DOCX模板失败: {str(e)}")
            return None
    
    def export_template(self, template_id):
        """导出模板"""
        template = self.get_template(template_id)
        if template:
            return {
                "name": template["name"],
                "description": template["description"],
                "content": template["content"],
                "structure": template.get("structure", {})
            }
        return None
    
    def derive_template(self, template_id, new_name, new_description=""):
        """
        基于现有模板派生新模板
        
        Args:
            template_id: 源模板ID
            new_name: 新模板名称
            new_description: 新模板描述
            
        Returns:
            dict: 新创建的模板信息
        """
        # 获取源模板
        source_template = self.get_template(template_id)
        if not source_template:
            return None
        
        # 创建新模板，保留源模板的大部分属性
        new_template = self.create_template(
            name=new_name,
            content=source_template["content"],
            description=new_description or f"基于{source_template['name']}派生的模板",
            template_type=source_template.get("type", "weekly_report"),
            output_format=source_template.get("output_format", "txt"),
            prompt=source_template.get("prompt", ""),
            structure=source_template.get("structure", {})
        )
        
        # 添加派生关系
        config = self._load_config()
        for t in config["templates"]:
            if t["id"] == new_template["id"]:
                t["derived_from"] = template_id
                t["derived_from_name"] = source_template["name"]
                break
        
        self._save_config(config)
        return new_template
    
    def get_template_structure(self, template_id):
        """
        获取模板结构信息
        
        Args:
            template_id: 模板ID
            
        Returns:
            dict: 模板结构信息
        """
        template = self.get_template(template_id)
        return template.get("structure", {}) if template else {}
    
    def save_template(self, template_id, template_name, content, structure=None):
        """
        保存模板文件，支持保存模板结构
        
        Args:
            template_id: 模板ID
            template_name: 模板名称
            content: 模板内容
            structure: 模板结构信息
        """
        # 保存文本内容
        template_path = os.path.join(self.templates_dir, f"{template_id}.txt")
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # 保存结构信息（如果提供）
        if structure:
            structure_path = os.path.join(self.templates_dir, f"{template_id}_structure.json")
            with open(structure_path, "w", encoding="utf-8") as f:
                json.dump(structure, f, ensure_ascii=False, indent=2)
    
    def _read_template(self, template_id):
        """
        读取模板内容，支持读取模板结构
        
        Args:
            template_id: 模板ID
            
        Returns:
            tuple: (content, structure)
        """
        template_path = os.path.join(self.templates_dir, f"{template_id}.txt")
        content = None
        structure = None
        
        # 读取文本内容
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
        
        # 读取结构信息
        structure_path = os.path.join(self.templates_dir, f"{template_id}_structure.json")
        if os.path.exists(structure_path):
            with open(structure_path, "r", encoding="utf-8") as f:
                structure = json.load(f)
        
        return content, structure
    
    def get_template(self, template_id):
        """
        获取指定模板，包含结构信息
        
        Args:
            template_id: 模板ID
            
        Returns:
            dict: 模板信息
        """
        config = self._load_config()
        template = next((t for t in config["templates"] if t["id"] == template_id), None)
        
        if template:
            # 读取模板内容和结构
            content, structure = self._read_template(template_id)
            template["content"] = content
            if structure:
                template["structure"] = structure
        
        return template
