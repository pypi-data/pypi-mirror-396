from flask import Flask, render_template, request, jsonify, send_file, Response
import os
import time
import json
from datetime import datetime
from threading import Lock
from hos_office_platform.utils.report_generator import Config, ReportGenerator
from hos_office_platform.utils.api_client import APIClient
from hos_office_platform.utils.template_manager import TemplateManager
from hos_office_platform.utils.meeting_manager import MeetingManager
from hos_office_platform.utils.project_manager import ProjectManager
from hos_office_platform.utils.knowledge_base import KnowledgeBase
from hos_office_platform.utils.schedule_manager import ScheduleManager
from hos_office_platform.utils.approval_manager import ApprovalManager
from hos_office_platform.utils.task_manager import TaskManager

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 初始化Flask应用，配置模板和静态文件夹路径
app = Flask(__name__, 
            template_folder=os.path.join(current_dir, 'templates'), 
            static_folder=os.path.join(current_dir, 'static'))

# 全局变量
config = Config()
api_client = APIClient(config.api_key)
report_generator = ReportGenerator(config, api_client)
template_manager = TemplateManager()
meeting_manager = MeetingManager()
project_manager = ProjectManager()
knowledge_base = KnowledgeBase()
schedule_manager = ScheduleManager()
approval_manager = ApprovalManager()

# 任务管理器
app_task_manager = TaskManager()

# 进度管理：用于存储和推送生成进度
progress_data = {}
progress_lock = Lock()
progress_counter = 0

# 主页面路由
@app.route('/')
def index():
    return render_template('index.html')

# 单周报生成路由
@app.route('/api/generate', methods=['POST'])
def generate_report():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        template_id = data.get('template_id', None)
        
        if not prompt.strip():
            return jsonify({'success': False, 'message': '请输入提示词'})
        
        # 生成进度ID
        global progress_counter
        with progress_lock:
            progress_counter += 1
            progress_id = f'progress_{progress_counter}'
        
        # 进度回调函数
        def progress_callback(current, total, percentage, message):
            update_progress(progress_id, current, total, percentage, message)
        
        # 添加进度支持
        update_progress(progress_id, 0, 1, 0, '准备生成周报...')
        
        report_content = report_generator.generate_single_report(prompt, template_id)
        
        update_progress(progress_id, 1, 1, 100, '生成完成')
        
        return jsonify({'success': True, 'content': report_content, 'progress_id': progress_id})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成失败: {str(e)}'})

def update_progress(progress_id, current, total, percentage, message):
    """更新生成进度"""
    with progress_lock:
        progress_data[progress_id] = {
            'current': current,
            'total': total,
            'percentage': round(percentage, 2),
            'message': message,
            'timestamp': time.time()
        }

# SSE端点：推送生成进度
@app.route('/api/generate/progress/<progress_id>')
def generate_progress(progress_id):
    """推送生成进度的SSE端点"""
    def generate():
        with progress_lock:
            # 初始化进度
            if progress_id not in progress_data:
                progress_data[progress_id] = {
                    'current': 0,
                    'total': 0,
                    'percentage': 0,
                    'message': '准备开始生成...',
                    'timestamp': time.time()
                }
        
        while True:
            with progress_lock:
                progress = progress_data.get(progress_id)
                if not progress:
                    break
            
            # 发送进度更新
            yield f'data: {json.dumps(progress)}\n\n'
            
            # 检查是否完成
            if progress['percentage'] >= 100:
                break
            
            # 每0.5秒更新一次
            time.sleep(0.5)
        
        # 清理进度数据
        with progress_lock:
            if progress_id in progress_data:
                del progress_data[progress_id]
    
    return Response(generate(), mimetype='text/event-stream')

# 批量周报生成路由
@app.route('/api/batch_generate', methods=['POST'])
def batch_generate_reports():
    try:
        data = request.get_json()
        prompts = data.get('prompts', '')
        template_id = data.get('template_id', None)
        file_format = data.get('file_format', 'txt')
        
        if not prompts.strip():
            return jsonify({'success': False, 'message': '请输入提示词'})
        
        prompts_list = [p.strip() for p in prompts.split('\n') if p.strip()]
        
        # 生成进度ID
        global progress_counter
        with progress_lock:
            progress_counter += 1
            progress_id = f'progress_{progress_counter}'
        
        # 创建任务
        task_id = app_task_manager.create_task(
            task_type="batch_generate",
            description=f"批量生成 {len(prompts_list)} 份文档",
            total_steps=len(prompts_list)
        )
        
        # 进度回调函数
        def progress_callback(current, total, percentage, message):
            update_progress(progress_id, current, total, percentage, message)
            app_task_manager.update_task(
                task_id,
                current_step=current,
                percentage=percentage
            )
            # 检查任务是否被暂停
            app_task_manager.wait_for_resume(task_id)
        
        # 异步执行批量生成
        import threading
        results = []
        
        def batch_generate_task():
            nonlocal results
            try:
                results = report_generator.generate_batch_reports(prompts_list, template_id, progress_callback, file_format)
                app_task_manager.complete_task(task_id, result={"generated": len(results), "results": results})
            except Exception as e:
                app_task_manager.fail_task(task_id, error=str(e))
        
        thread = threading.Thread(target=batch_generate_task)
        thread.daemon = True
        thread.start()
        
        # 返回进度ID和任务ID，客户端可以通过这些ID获取实时进度和任务状态
        return jsonify({
            'success': True, 
            'progress_id': progress_id,
            'task_id': task_id,
            'message': '批量生成已开始，请通过进度ID获取实时进度，通过任务ID管理任务'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'批量生成失败: {str(e)}'})

# 保存周报路由
@app.route('/api/save', methods=['POST'])
def save_report():
    try:
        data = request.get_json()
        content = data.get('content', '')
        filename = data.get('filename', '')
        file_format = data.get('file_format', 'txt')
        
        if not content.strip():
            return jsonify({'success': False, 'message': '请输入周报内容'})
        
        saved_filename = report_generator.save_report(content, filename, file_format)
        return jsonify({'success': True, 'filename': saved_filename})
    except Exception as e:
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'})

# 加载周报列表路由
@app.route('/api/load_reports', methods=['GET'])
def load_reports():
    try:
        reports = report_generator.load_reports()
        # 只返回文件名和日期
        report_list = [{'filename': r['filename'], 'date': r['date']} for r in reports]
        return jsonify({'success': True, 'reports': report_list})
    except Exception as e:
        return jsonify({'success': False, 'message': f'加载失败: {str(e)}'})

# 加载特定周报路由
@app.route('/api/load_report/<filename>', methods=['GET'])
def load_report(filename):
    try:
        content = report_generator.read_report(filename)
        return jsonify({'success': True, 'content': content})
    except Exception as e:
        return jsonify({'success': False, 'message': f'加载失败: {str(e)}'})

# 删除周报路由
@app.route('/api/delete_report/<filename>', methods=['DELETE'])
def delete_report(filename):
    try:
        success = report_generator.delete_report(filename)
        if success:
            return jsonify({'success': True, 'message': '删除成功'})
        else:
            return jsonify({'success': False, 'message': '删除失败，文件不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})

# 批量删除周报路由
@app.route('/api/batch_delete_reports', methods=['POST'])
def batch_delete_reports():
    try:
        data = request.get_json()
        filenames = data.get('filenames', [])
        
        if not filenames:
            return jsonify({'success': False, 'message': '请选择要删除的文件'})
        
        # 生成进度ID
        global progress_counter
        with progress_lock:
            progress_counter += 1
            progress_id = f'progress_{progress_counter}'
        
        # 进度回调函数
        def progress_callback(current, total, percentage, message):
            update_progress(progress_id, current, total, percentage, message)
        
        # 异步执行批量删除
        import threading
        result = {}
        
        def batch_delete_task():
            nonlocal result
            result = report_generator.batch_delete_reports(filenames, progress_callback)
        
        thread = threading.Thread(target=batch_delete_task)
        thread.daemon = True
        thread.start()
        
        # 返回进度ID，客户端可以通过这个ID获取实时进度
        return jsonify({
            'success': True, 
            'progress_id': progress_id,
            'message': '批量删除已开始，请通过进度ID获取实时进度'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'批量删除失败: {str(e)}'})

# Excel导入路由
@app.route('/api/import_excel', methods=['POST'])
def import_excel():
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '请选择要上传的Excel文件'})
        
        file = request.files['file']
        
        # 检查文件是否为空
        if file.filename == '':
            return jsonify({'success': False, 'message': '请选择要上传的Excel文件'})
        
        # 检查文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'success': False, 'message': '请选择Excel文件（.xlsx或.xls格式）'})
        
        # 生成进度ID
        global progress_counter
        with progress_lock:
            progress_counter += 1
            progress_id = f'progress_{progress_counter}'
        
        # 进度回调函数
        def progress_callback(current, total, percentage, message):
            update_progress(progress_id, current, total, percentage, message)
        
        # 异步执行Excel导入
        import threading
        result = {}
        
        def import_excel_task():
            nonlocal result
            result = report_generator.import_excel(file, progress_callback)
        
        thread = threading.Thread(target=import_excel_task)
        thread.daemon = True
        thread.start()
        
        # 返回进度ID，客户端可以通过这个ID获取实时进度
        return jsonify({
            'success': True, 
            'progress_id': progress_id,
            'message': 'Excel导入已开始，请通过进度ID获取实时进度'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Excel导入失败: {str(e)}'})

# 切换API来源路由
@app.route('/api/switch_api', methods=['POST'])
def switch_api():
    try:
        data = request.get_json()
        api_source = data.get('api_source', 'deepseek')
        
        success = api_client.set_api_source(api_source)
        if success:
            # 更新report_generator的api_client
            report_generator.api_client = api_client
            status_msg = "DeepSeek API已连接" if api_source == "deepseek" else "本地Ollama已连接"
            return jsonify({'success': True, 'status': status_msg})
        else:
            return jsonify({'success': False, 'message': '切换API失败，未知来源'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'切换API失败: {str(e)}'})

# 下载周报路由
@app.route('/api/download/<filename>', methods=['GET'])
def download_report(filename):
    try:
        filepath = os.path.join(config.reports_dir, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'success': False, 'message': '文件不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'下载失败: {str(e)}'})

# 模板管理API

# 获取所有模板
@app.route('/api/templates', methods=['GET'])
def get_templates():
    try:
        templates = template_manager.get_templates()
        return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取模板列表失败: {str(e)}'})

# 获取当前模板
@app.route('/api/templates/current', methods=['GET'])
def get_current_template():
    try:
        template = template_manager.get_current_template()
        return jsonify({'success': True, 'template': template})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取当前模板失败: {str(e)}'})

# 获取指定模板
@app.route('/api/templates/<template_id>', methods=['GET'])
def get_template(template_id):
    try:
        template = template_manager.get_template(template_id)
        if template:
            return jsonify({'success': True, 'template': template})
        else:
            return jsonify({'success': False, 'message': '模板不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取模板失败: {str(e)}'})

# 创建模板
@app.route('/api/templates', methods=['POST'])
def create_template():
    try:
        data = request.get_json()
        name = data.get('name', '')
        content = data.get('content', '')
        description = data.get('description', '')
        
        if not name or not content:
            return jsonify({'success': False, 'message': '模板名称和内容不能为空'})
        
        template = template_manager.create_template(name, content, description)
        return jsonify({'success': True, 'template': template})
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建模板失败: {str(e)}'})

# 更新模板
@app.route('/api/templates/<template_id>', methods=['PUT'])
def update_template(template_id):
    try:
        data = request.get_json()
        name = data.get('name')
        content = data.get('content')
        description = data.get('description')
        
        template = template_manager.update_template(template_id, name, content, description)
        if template:
            return jsonify({'success': True, 'template': template})
        else:
            return jsonify({'success': False, 'message': '模板不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新模板失败: {str(e)}'})

# 删除模板
@app.route('/api/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    try:
        success = template_manager.delete_template(template_id)
        if success:
            return jsonify({'success': True, 'message': '模板删除成功'})
        else:
            return jsonify({'success': False, 'message': '模板不存在或无法删除'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除模板失败: {str(e)}'})

# 设置当前模板
@app.route('/api/templates/current', methods=['PUT'])
def set_current_template():
    try:
        data = request.get_json()
        template_id = data.get('template_id', '')
        
        success = template_manager.set_current_template(template_id)
        if success:
            return jsonify({'success': True, 'message': '当前模板设置成功'})
        else:
            return jsonify({'success': False, 'message': '模板不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'设置当前模板失败: {str(e)}'})

# 导入模板
@app.route('/api/templates/import', methods=['POST'])
def import_template():
    try:
        data = request.get_json()
        name = data.get('name', '')
        content = data.get('content', '')
        description = data.get('description', '')
        
        if not name or not content:
            return jsonify({'success': False, 'message': '模板名称和内容不能为空'})
        
        template = template_manager.import_template(name, content, description)
        return jsonify({'success': True, 'template': template})
    except Exception as e:
        return jsonify({'success': False, 'message': f'导入模板失败: {str(e)}'})

# 导入DOCX模板
@app.route('/api/templates/import_docx', methods=['POST'])
def import_docx_template():
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '请选择要上传的DOCX文件'})
        
        file = request.files['file']
        
        # 检查文件类型
        if not file.filename.endswith('.docx'):
            return jsonify({'success': False, 'message': '请上传DOCX格式的文件'})
        
        # 获取其他参数
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        template_type = request.form.get('type', 'weekly_report')
        
        # 如果没有提供名称，使用文件名作为模板名称
        if not name:
            name = os.path.splitext(file.filename)[0]
        
        # 保存上传的文件到临时位置
        temp_file_path = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(temp_file_path)
        
        # 导入DOCX模板
        template = template_manager.import_docx_template(
            temp_file_path, 
            name, 
            description, 
            template_type
        )
        
        # 删除临时文件
        os.remove(temp_file_path)
        
        if template:
            return jsonify({'success': True, 'template': template, 'message': 'DOCX模板导入成功'})
        else:
            return jsonify({'success': False, 'message': '导入DOCX模板失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'导入DOCX模板失败: {str(e)}'})

# 导出模板
@app.route('/api/templates/<template_id>/export', methods=['GET'])
def export_template(template_id):
    try:
        template = template_manager.export_template(template_id)
        if template:
            return jsonify({'success': True, 'template': template})
        else:
            return jsonify({'success': False, 'message': '模板不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'导出模板失败: {str(e)}'})

# 派生模板
@app.route('/api/templates/<template_id>/derive', methods=['POST'])
def derive_template(template_id):
    try:
        data = request.get_json()
        new_name = data.get('name', '')
        new_description = data.get('description', '')
        
        if not new_name:
            return jsonify({'success': False, 'message': '新模板名称不能为空'})
        
        new_template = template_manager.derive_template(template_id, new_name, new_description)
        if new_template:
            return jsonify({'success': True, 'template': new_template})
        else:
            return jsonify({'success': False, 'message': '源模板不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'派生模板失败: {str(e)}'})

# 获取模板结构
@app.route('/api/templates/<template_id>/structure', methods=['GET'])
def get_template_structure(template_id):
    try:
        structure = template_manager.get_template_structure(template_id)
        return jsonify({'success': True, 'structure': structure})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取模板结构失败: {str(e)}'})

# 系统设置API

# 获取模板配置
@app.route('/api/system/template-settings', methods=['GET'])
def get_template_settings():
    try:
        settings = config.get_template_settings()
        return jsonify({'success': True, 'settings': settings})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取模板配置失败: {str(e)}'})

# 更新模板配置
@app.route('/api/system/template-settings', methods=['PUT'])
def update_template_settings():
    try:
        data = request.get_json()
        config.update_template_settings(data)
        return jsonify({'success': True, 'message': '模板配置更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新模板配置失败: {str(e)}'})

# 获取系统配置
@app.route('/api/system/settings', methods=['GET'])
def get_system_settings():
    try:
        settings = config.system_settings
        return jsonify({'success': True, 'settings': settings})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取系统配置失败: {str(e)}'})

# 获取当前API Key
@app.route('/api/get_api_key', methods=['GET'])
def get_api_key():
    try:
        # 从key.txt文件读取API Key
        with open('key.txt', 'r', encoding='utf-8') as f:
            api_key = f.read().strip()
        return jsonify({'success': True, 'api_key': api_key})
    except FileNotFoundError:
        # 如果key.txt文件不存在，返回空字符串
        return jsonify({'success': True, 'api_key': ''})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取API Key失败: {str(e)}'})

# 更新API Key
@app.route('/api/update_api_key', methods=['POST'])
def update_api_key():
    try:
        data = request.get_json()
        new_api_key = data.get('api_key', '')
        if not new_api_key.strip():
            return jsonify({'success': False, 'message': 'API Key不能为空'})
        # 写入新的API Key到key.txt文件
        with open('key.txt', 'w', encoding='utf-8') as f:
            f.write(new_api_key.strip())
        # 更新全局API客户端
        global api_client, report_generator
        api_client = APIClient(new_api_key)
        report_generator = ReportGenerator(config, api_client)
        return jsonify({'success': True, 'message': 'API Key更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新API Key失败: {str(e)}'})

# 更新系统配置
@app.route('/api/system/settings', methods=['PUT'])
def update_system_settings():
    try:
        data = request.get_json()
        config.system_settings.update(data)
        config.save_system_settings()
        return jsonify({'success': True, 'message': '系统配置更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新系统配置失败: {str(e)}'})

# 工作流管理API

# 获取工作流列表
@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    try:
        workflows = config.get_workflows()
        return jsonify({'success': True, 'workflows': workflows})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取工作流列表失败: {str(e)}'})

# 添加工作流
@app.route('/api/workflows', methods=['POST'])
def add_workflow():
    try:
        data = request.get_json()
        workflow = config.add_workflow(data)
        return jsonify({'success': True, 'workflow': workflow})
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加工作流失败: {str(e)}'})

# 更新工作流
@app.route('/api/workflows/<workflow_id>', methods=['PUT'])
def update_workflow(workflow_id):
    try:
        data = request.get_json()
        workflow = config.update_workflow(workflow_id, data)
        if workflow:
            return jsonify({'success': True, 'workflow': workflow})
        else:
            return jsonify({'success': False, 'message': '工作流不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新工作流失败: {str(e)}'})

# 删除工作流
@app.route('/api/workflows/<workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id):
    try:
        config.delete_workflow(workflow_id)
        return jsonify({'success': True, 'message': '工作流删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除工作流失败: {str(e)}'})

# 测试Ollama连接
@app.route('/api/test_ollama_connection', methods=['POST'])
def test_ollama_connection():
    try:
        data = request.get_json()
        base_url = data.get('base_url', 'http://localhost:11434')
        model = data.get('model', 'llama3')
        
        # 创建临时API客户端测试连接
        from hos_office_platform.utils.api_client import APIClient
        
        # 对于Ollama，API密钥可以是任意值
        test_client = APIClient(api_key='test', api_source='ollama')
        
        # 更新配置
        test_client.config['ollama']['base_url'] = base_url.replace('/v1/chat/completions', '')
        test_client.config['ollama']['model'] = model
        test_client.set_api_source('ollama')
        
        # 测试连接
        success, message = test_client.test_connection()
        
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'测试连接失败: {str(e)}'})

# 下载提示词导入模板
@app.route('/api/download_prompt_template', methods=['GET'])
def download_prompt_template():
    try:
        import os
        from flask import send_file
        
        template_path = os.path.join(os.getcwd(), 'prompt_import_template.xlsx')
        
        if os.path.exists(template_path):
            return send_file(template_path, as_attachment=True, download_name='提示词导入模板.xlsx')
        else:
            return jsonify({'success': False, 'message': '模板文件不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'下载模板失败: {str(e)}'})

# AI生成工作流
@app.route('/api/workflows/generate', methods=['POST'])
def generate_workflow():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt.trim():
            return jsonify({'success': False, 'message': '请输入工作流需求描述'})
        
        workflow = config.generate_workflow(prompt)
        return jsonify({'success': True, 'workflow': workflow})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成工作流失败: {str(e)}'})

# 将工作流转换为正式模块
@app.route('/api/workflows/<workflow_id>/convert_to_module', methods=['POST'])
def convert_workflow_to_module(workflow_id):
    try:
        module = config.convert_workflow_to_module(workflow_id)
        if module:
            return jsonify({'success': True, 'module': module, 'message': '工作流已成功转换为正式模块'})
        else:
            return jsonify({'success': False, 'message': '工作流不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'转换模块失败: {str(e)}'})

# 自定义模块管理API

# 获取自定义模块列表
@app.route('/api/modules', methods=['GET'])
def get_custom_modules():
    try:
        modules = config.get_custom_modules()
        return jsonify({'success': True, 'modules': modules})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取自定义模块列表失败: {str(e)}'})

# 添加自定义模块
@app.route('/api/modules', methods=['POST'])
def add_custom_module():
    try:
        data = request.get_json()
        module = config.add_custom_module(data)
        return jsonify({'success': True, 'module': module})
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加自定义模块失败: {str(e)}'})

# 更新自定义模块
@app.route('/api/modules/<module_id>', methods=['PUT'])
def update_custom_module(module_id):
    try:
        data = request.get_json()
        module = config.update_custom_module(module_id, data)
        if module:
            return jsonify({'success': True, 'module': module})
        else:
            return jsonify({'success': False, 'message': '自定义模块不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新自定义模块失败: {str(e)}'})

# 删除自定义模块
@app.route('/api/modules/<module_id>', methods=['DELETE'])
def delete_custom_module(module_id):
    try:
        config.delete_custom_module(module_id)
        return jsonify({'success': True, 'message': '自定义模块删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除自定义模块失败: {str(e)}'})

# 重新排序自定义模块
@app.route('/api/modules/reorder', methods=['PUT'])
def reorder_custom_modules():
    try:
        data = request.get_json()
        module_ids = data.get('module_ids', [])
        config.reorder_custom_modules(module_ids)
        return jsonify({'success': True, 'message': '自定义模块排序更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新自定义模块排序失败: {str(e)}'})

# 工作流模板API

# 获取工作流模板列表
@app.route('/api/workflow-templates', methods=['GET'])
def get_workflow_templates():
    try:
        templates = config.hos_config.get('workflow_templates', [])
        return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取工作流模板列表失败: {str(e)}'})

# 获取指定工作流模板
@app.route('/api/workflow-templates/<template_id>', methods=['GET'])
def get_workflow_template(template_id):
    try:
        templates = config.hos_config.get('workflow_templates', [])
        template = next((t for t in templates if t['id'] == template_id), None)
        if template:
            return jsonify({'success': True, 'template': template})
        else:
            return jsonify({'success': False, 'message': '工作流模板不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取工作流模板失败: {str(e)}'})

# 批次管理API

# 获取所有批次
@app.route('/api/batches', methods=['GET'])
def get_batches():
    try:
        batches = report_generator.get_batches()
        return jsonify({'success': True, 'batches': batches})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取批次列表失败: {str(e)}'})

# 获取特定批次
@app.route('/api/batches/<batch_id>', methods=['GET'])
def get_batch(batch_id):
    try:
        batch = report_generator.get_batch(batch_id)
        if batch:
            return jsonify({'success': True, 'batch': batch})
        else:
            return jsonify({'success': False, 'message': '批次不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取批次失败: {str(e)}'})

# 批量下载API
@app.route('/api/batch_download', methods=['POST'])
def batch_download():
    try:
        data = request.get_json()
        filenames = data.get('filenames', [])
        batch_id = data.get('batch_id', None)
        
        # 处理批次下载
        if batch_id:
            batch = report_generator.get_batch(batch_id)
            if batch:
                filenames = batch['files']
        
        if not filenames:
            return jsonify({'success': False, 'message': '请选择要下载的文件'})
        
        # 创建临时目录
        import tempfile
        import zipfile
        import os
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        # 创建压缩包
        zip_filename = f"batch_download_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in filenames:
                file_path = os.path.join(report_generator.config.reports_dir, filename)
                if os.path.exists(file_path):
                    zipf.write(file_path, filename)
        
        # 返回压缩包
        return send_file(zip_path, as_attachment=True, download_name=zip_filename)
    except Exception as e:
        return jsonify({'success': False, 'message': f'批量下载失败: {str(e)}'})

# 任务管理API

# 获取所有任务
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = app_task_manager.get_all_tasks()
        return jsonify({'success': True, 'tasks': tasks})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取任务列表失败: {str(e)}'})

# 获取特定任务
@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    try:
        task = app_task_manager.get_task(task_id)
        if task:
            return jsonify({'success': True, 'task': task})
        else:
            return jsonify({'success': False, 'message': '任务不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取任务失败: {str(e)}'})

# 暂停任务
@app.route('/api/tasks/<task_id>/pause', methods=['POST'])
def pause_task(task_id):
    try:
        success = app_task_manager.pause_task(task_id)
        if success:
            return jsonify({'success': True, 'message': '任务已暂停'})
        else:
            return jsonify({'success': False, 'message': '任务不存在或无法暂停'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'暂停任务失败: {str(e)}'})

# 恢复任务
@app.route('/api/tasks/<task_id>/resume', methods=['POST'])
def resume_task(task_id):
    try:
        success = app_task_manager.resume_task(task_id)
        if success:
            return jsonify({'success': True, 'message': '任务已恢复'})
        else:
            return jsonify({'success': False, 'message': '任务不存在或无法恢复'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'恢复任务失败: {str(e)}'})

# 取消任务
@app.route('/api/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    try:
        success = app_task_manager.cancel_task(task_id)
        if success:
            return jsonify({'success': True, 'message': '任务已取消'})
        else:
            return jsonify({'success': False, 'message': '任务不存在或无法取消'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'取消任务失败: {str(e)}'})

# 清理已完成任务
@app.route('/api/tasks/cleanup', methods=['POST'])
def cleanup_tasks():
    try:
        app_task_manager.cleanup_completed_tasks()
        return jsonify({'success': True, 'message': '已清理已完成任务'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'清理任务失败: {str(e)}'})

# 批量提示词表格导入API
@app.route('/api/import_prompts_excel', methods=['POST'])
def import_prompts_excel():
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '请选择要上传的Excel文件'})
        
        file = request.files['file']
        
        # 检查文件是否为空
        if file.filename == '':
            return jsonify({'success': False, 'message': '请选择要上传的Excel文件'})
        
        # 检查文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'success': False, 'message': '请选择Excel文件（.xlsx或.xls格式）'})
        
        # 导入pandas库
        import pandas as pd
        import io
        
        # 读取Excel文件
        df = pd.read_excel(io.BytesIO(file.read()))
        
        # 检查必要的列
        if 'prompt' not in df.columns:
            return jsonify({'success': False, 'message': 'Excel文件必须包含prompt列'})
        
        # 提取提示词列表
        prompts = []
        for index, row in df.iterrows():
            prompt = row['prompt']
            if not pd.isna(prompt) and str(prompt).strip():
                prompts.append(str(prompt).strip())
        
        return jsonify({
            'success': True, 
            'message': f'成功导入 {len(prompts)} 个提示词',
            'prompts': prompts
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'导入提示词失败: {str(e)}'})

# 工作流提示词模板API

# 获取工作流提示词模板列表
@app.route('/api/workflow-prompt-templates', methods=['GET'])
def get_workflow_prompt_templates():
    try:
        # 直接从文件加载工作流提示词模板
        import json
        import os
        workflow_prompt_templates_file = os.path.join(os.getcwd(), "workflow_prompt_templates.json")
        if os.path.exists(workflow_prompt_templates_file):
            with open(workflow_prompt_templates_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return jsonify({'success': True, 'templates': data.get('workflow_prompt_templates', [])})
        else:
            return jsonify({'success': True, 'templates': []})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取工作流提示词模板列表失败: {str(e)}'})

# 获取指定工作流提示词模板
@app.route('/api/workflow-prompt-templates/<template_id>', methods=['GET'])
def get_workflow_prompt_template(template_id):
    try:
        # 直接从文件加载工作流提示词模板
        import json
        import os
        workflow_prompt_templates_file = os.path.join(os.getcwd(), "workflow_prompt_templates.json")
        if os.path.exists(workflow_prompt_templates_file):
            with open(workflow_prompt_templates_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                templates = data.get('workflow_prompt_templates', [])
                template = next((t for t in templates if t['id'] == template_id), None)
                if template:
                    return jsonify({'success': True, 'template': template})
                else:
                    return jsonify({'success': False, 'message': '工作流提示词模板不存在'})
        else:
            return jsonify({'success': False, 'message': '工作流提示词模板文件不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取工作流提示词模板失败: {str(e)}'})

# 会议管理API

# 获取会议列表
@app.route('/api/meetings', methods=['GET'])
def get_meetings():
    try:
        meetings = meeting_manager.get_meetings()
        return jsonify({'success': True, 'meetings': meetings})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取会议列表失败: {str(e)}'})

# 获取会议详情
@app.route('/api/meetings/<meeting_id>', methods=['GET'])
def get_meeting(meeting_id):
    try:
        meeting = meeting_manager.get_meeting(meeting_id)
        if meeting:
            return jsonify({'success': True, 'meeting': meeting})
        else:
            return jsonify({'success': False, 'message': '会议不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取会议详情失败: {str(e)}'})

# 创建会议
@app.route('/api/meetings', methods=['POST'])
def create_meeting():
    try:
        data = request.get_json()
        meeting = meeting_manager.create_meeting(data)
        return jsonify({'success': True, 'meeting': meeting})
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建会议失败: {str(e)}'})

# 更新会议
@app.route('/api/meetings/<meeting_id>', methods=['PUT'])
def update_meeting(meeting_id):
    try:
        data = request.get_json()
        meeting = meeting_manager.update_meeting(meeting_id, data)
        if meeting:
            return jsonify({'success': True, 'meeting': meeting})
        else:
            return jsonify({'success': False, 'message': '会议不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新会议失败: {str(e)}'})

# 删除会议
@app.route('/api/meetings/<meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    try:
        success = meeting_manager.delete_meeting(meeting_id)
        if success:
            return jsonify({'success': True, 'message': '删除会议成功'})
        else:
            return jsonify({'success': False, 'message': '会议不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除会议失败: {str(e)}'})

# 生成会议纪要
@app.route('/api/meetings/<meeting_id>/generate_minutes', methods=['POST'])
def generate_minutes(meeting_id):
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        template_id = data.get('template_id', None)
        
        if not prompt.strip():
            return jsonify({'success': False, 'message': '请输入提示词'})
        
        minutes = meeting_manager.generate_minutes(meeting_id, prompt, template_id)
        return jsonify({'success': True, 'minutes': minutes})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成会议纪要失败: {str(e)}'})

# 添加行动项
@app.route('/api/meetings/<meeting_id>/action_items', methods=['POST'])
def add_action_item(meeting_id):
    try:
        data = request.get_json()
        action_item = meeting_manager.add_action_item(meeting_id, data)
        if action_item:
            return jsonify({'success': True, 'action_item': action_item})
        else:
            return jsonify({'success': False, 'message': '会议不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加行动项失败: {str(e)}'})

# 更新行动项
@app.route('/api/meetings/<meeting_id>/action_items/<action_item_id>', methods=['PUT'])
def update_action_item(meeting_id, action_item_id):
    try:
        data = request.get_json()
        action_item = meeting_manager.update_action_item(meeting_id, action_item_id, data)
        if action_item:
            return jsonify({'success': True, 'action_item': action_item})
        else:
            return jsonify({'success': False, 'message': '行动项不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新行动项失败: {str(e)}'})

# 删除行动项
@app.route('/api/meetings/<meeting_id>/action_items/<action_item_id>', methods=['DELETE'])
def delete_action_item(meeting_id, action_item_id):
    try:
        success = meeting_manager.delete_action_item(meeting_id, action_item_id)
        if success:
            return jsonify({'success': True, 'message': '删除行动项成功'})
        else:
            return jsonify({'success': False, 'message': '行动项不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除行动项失败: {str(e)}'})

# 会议管理扩展API

# 添加参会人员
@app.route('/api/meetings/<meeting_id>/attendees', methods=['POST'])
def add_attendee(meeting_id):
    try:
        data = request.get_json()
        attendee = data.get('attendee', '')
        if not attendee:
            return jsonify({'success': False, 'message': '参会人员不能为空'})
        meeting = meeting_manager.add_attendee(meeting_id, attendee)
        if meeting:
            return jsonify({'success': True, 'meeting': meeting})
        else:
            return jsonify({'success': False, 'message': '会议不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加参会人员失败: {str(e)}'})

# 移除参会人员
@app.route('/api/meetings/<meeting_id>/attendees', methods=['DELETE'])
def remove_attendee(meeting_id):
    try:
        data = request.get_json()
        attendee = data.get('attendee', '')
        if not attendee:
            return jsonify({'success': False, 'message': '参会人员不能为空'})
        meeting = meeting_manager.remove_attendee(meeting_id, attendee)
        if meeting:
            return jsonify({'success': True, 'meeting': meeting})
        else:
            return jsonify({'success': False, 'message': '会议不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'移除参会人员失败: {str(e)}'})

# 设置会议提醒
@app.route('/api/meetings/<meeting_id>/reminder', methods=['PUT'])
def set_meeting_reminder(meeting_id):
    try:
        data = request.get_json()
        reminder_time = data.get('reminder_time', '')
        if not reminder_time:
            return jsonify({'success': False, 'message': '提醒时间不能为空'})
        meeting = meeting_manager.set_meeting_reminder(meeting_id, reminder_time)
        if meeting:
            return jsonify({'success': True, 'meeting': meeting})
        else:
            return jsonify({'success': False, 'message': '会议不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'设置会议提醒失败: {str(e)}'})

# 获取即将到来的会议
@app.route('/api/meetings/upcoming', methods=['GET'])
def get_upcoming_meetings():
    try:
        days = request.args.get('days', 7)
        meetings = meeting_manager.get_upcoming_meetings(int(days))
        return jsonify({'success': True, 'meetings': meetings})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取即将到来的会议失败: {str(e)}'})

# 生成会议报告
@app.route('/api/meetings/<meeting_id>/report', methods=['GET'])
def generate_meeting_report(meeting_id):
    try:
        report = meeting_manager.generate_meeting_report(meeting_id)
        if report:
            return jsonify({'success': True, 'report': report})
        else:
            return jsonify({'success': False, 'message': '会议不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成会议报告失败: {str(e)}'})

# 获取会议统计信息
@app.route('/api/meetings/statistics', methods=['GET'])
def get_meeting_statistics():
    try:
        statistics = meeting_manager.get_meeting_statistics()
        return jsonify({'success': True, 'statistics': statistics})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取会议统计信息失败: {str(e)}'})

# 项目管理API

# 获取项目列表
@app.route('/api/projects', methods=['GET'])
def get_projects():
    try:
        projects = project_manager.get_projects()
        return jsonify({'success': True, 'projects': projects})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取项目列表失败: {str(e)}'})

# 获取项目详情
@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    try:
        project = project_manager.get_project(project_id)
        if project:
            return jsonify({'success': True, 'project': project})
        else:
            return jsonify({'success': False, 'message': '项目不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取项目详情失败: {str(e)}'})

# 创建项目
@app.route('/api/projects', methods=['POST'])
def create_project():
    try:
        data = request.get_json()
        project = project_manager.create_project(data)
        return jsonify({'success': True, 'project': project})
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建项目失败: {str(e)}'})

# 更新项目
@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    try:
        data = request.get_json()
        project = project_manager.update_project(project_id, data)
        if project:
            return jsonify({'success': True, 'project': project})
        else:
            return jsonify({'success': False, 'message': '项目不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新项目失败: {str(e)}'})

# 删除项目
@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        success = project_manager.delete_project(project_id)
        if success:
            return jsonify({'success': True, 'message': '删除项目成功'})
        else:
            return jsonify({'success': False, 'message': '项目不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除项目失败: {str(e)}'})

# 获取项目任务列表
@app.route('/api/projects/<project_id>/tasks', methods=['GET'])
def get_project_tasks(project_id):
    try:
        tasks = project_manager.get_tasks(project_id)
        return jsonify({'success': True, 'tasks': tasks})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取任务列表失败: {str(e)}'})



# 添加项目文档
@app.route('/api/projects/<project_id>/documents', methods=['POST'])
def add_document(project_id):
    try:
        data = request.get_json()
        document = project_manager.add_document(project_id, data)
        if document:
            return jsonify({'success': True, 'document': document})
        else:
            return jsonify({'success': False, 'message': '项目不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加文档失败: {str(e)}'})

# 删除项目文档
@app.route('/api/projects/<project_id>/documents/<document_id>', methods=['DELETE'])
def delete_document(project_id, document_id):
    try:
        success = project_manager.remove_document(project_id, document_id)
        if success:
            return jsonify({'success': True, 'message': '删除文档成功'})
        else:
            return jsonify({'success': False, 'message': '文档不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除文档失败: {str(e)}'})

# 项目管理扩展API

# 更新项目进度
@app.route('/api/projects/<project_id>/progress', methods=['PUT'])
def update_project_progress(project_id):
    try:
        data = request.get_json()
        progress = data.get('progress', 0)
        project = project_manager.update_project_progress(project_id, progress)
        if project:
            return jsonify({'success': True, 'project': project})
        else:
            return jsonify({'success': False, 'message': '项目不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新项目进度失败: {str(e)}'})

# 获取项目甘特图数据
@app.route('/api/projects/<project_id>/gantt', methods=['GET'])
def get_project_gantt_data(project_id):
    try:
        gantt_data = project_manager.get_project_gantt_data(project_id)
        if gantt_data:
            return jsonify({'success': True, 'data': gantt_data})
        else:
            return jsonify({'success': False, 'message': '项目不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取甘特图数据失败: {str(e)}'})

# 生成项目报告
@app.route('/api/projects/<project_id>/report', methods=['GET'])
def generate_project_report(project_id):
    try:
        report = project_manager.generate_project_report(project_id)
        if report:
            return jsonify({'success': True, 'report': report})
        else:
            return jsonify({'success': False, 'message': '项目不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成项目报告失败: {str(e)}'})

# 获取项目统计信息
@app.route('/api/projects/statistics', methods=['GET'])
def get_project_statistics():
    try:
        statistics = project_manager.get_project_statistics()
        return jsonify({'success': True, 'statistics': statistics})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取项目统计信息失败: {str(e)}'})

# 添加项目里程碑
@app.route('/api/projects/<project_id>/milestones', methods=['POST'])
def add_project_milestone(project_id):
    try:
        data = request.get_json()
        milestone = project_manager.add_project_milestone(project_id, data)
        if milestone:
            return jsonify({'success': True, 'project': milestone})
        else:
            return jsonify({'success': False, 'message': '项目不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加项目里程碑失败: {str(e)}'})

# 更新项目里程碑
@app.route('/api/projects/<project_id>/milestones/<milestone_id>', methods=['PUT'])
def update_project_milestone(project_id, milestone_id):
    try:
        data = request.get_json()
        milestone = project_manager.update_project_milestone(project_id, milestone_id, data)
        if milestone:
            return jsonify({'success': True, 'project': milestone})
        else:
            return jsonify({'success': False, 'message': '项目或里程碑不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新项目里程碑失败: {str(e)}'})

# 删除项目里程碑
@app.route('/api/projects/<project_id>/milestones/<milestone_id>', methods=['DELETE'])
def delete_project_milestone(project_id, milestone_id):
    try:
        milestone = project_manager.delete_project_milestone(project_id, milestone_id)
        if milestone:
            return jsonify({'success': True, 'project': milestone})
        else:
            return jsonify({'success': False, 'message': '项目或里程碑不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除项目里程碑失败: {str(e)}'})

# 知识库管理API

# 文档管理

# 获取文档列表
@app.route('/api/knowledge/documents', methods=['GET'])
def get_knowledge_documents():
    try:
        documents = knowledge_base.get_documents()
        return jsonify({'success': True, 'documents': documents})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取文档列表失败: {str(e)}'})

# 获取文档详情
@app.route('/api/knowledge/documents/<document_id>', methods=['GET'])
def get_knowledge_document(document_id):
    try:
        document = knowledge_base.get_document(document_id)
        if document:
            # 增加浏览量
            knowledge_base.add_view(document_id)
            return jsonify({'success': True, 'document': document})
        else:
            return jsonify({'success': False, 'message': '文档不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取文档详情失败: {str(e)}'})

# 创建文档
@app.route('/api/knowledge/documents', methods=['POST'])
def create_knowledge_document():
    try:
        data = request.get_json()
        document = knowledge_base.create_document(data)
        return jsonify({'success': True, 'document': document})
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建文档失败: {str(e)}'})

# 更新文档
@app.route('/api/knowledge/documents/<document_id>', methods=['PUT'])
def update_knowledge_document(document_id):
    try:
        data = request.get_json()
        document = knowledge_base.update_document(document_id, data)
        if document:
            return jsonify({'success': True, 'document': document})
        else:
            return jsonify({'success': False, 'message': '文档不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新文档失败: {str(e)}'})

# 删除文档
@app.route('/api/knowledge/documents/<document_id>', methods=['DELETE'])
def delete_knowledge_document(document_id):
    try:
        success = knowledge_base.delete_document(document_id)
        if success:
            return jsonify({'success': True, 'message': '删除文档成功'})
        else:
            return jsonify({'success': False, 'message': '文档不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除文档失败: {str(e)}'})

# 搜索文档
@app.route('/api/knowledge/documents/search', methods=['GET'])
def search_knowledge_documents():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'message': '搜索关键词不能为空'})
        results = knowledge_base.search_documents(query)
        return jsonify({'success': True, 'documents': results})
    except Exception as e:
        return jsonify({'success': False, 'message': f'搜索文档失败: {str(e)}'})

# 根据分类获取文档
@app.route('/api/knowledge/documents/category/<category_id>', methods=['GET'])
def get_documents_by_category(category_id):
    try:
        documents = knowledge_base.get_documents_by_category(category_id)
        return jsonify({'success': True, 'documents': documents})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取分类文档失败: {str(e)}'})

# 根据标签获取文档
@app.route('/api/knowledge/documents/tag/<tag>', methods=['GET'])
def get_documents_by_tag(tag):
    try:
        documents = knowledge_base.get_documents_by_tag(tag)
        return jsonify({'success': True, 'documents': documents})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取标签文档失败: {str(e)}'})

# 点赞文档
@app.route('/api/knowledge/documents/<document_id>/like', methods=['POST'])
def like_document(document_id):
    try:
        document = knowledge_base.toggle_like(document_id)
        if document:
            return jsonify({'success': True, 'document': document})
        else:
            return jsonify({'success': False, 'message': '文档不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'点赞失败: {str(e)}'})

# 分类管理

# 获取分类列表
@app.route('/api/knowledge/categories', methods=['GET'])
def get_categories():
    try:
        categories = knowledge_base.get_categories()
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取分类列表失败: {str(e)}'})

# 获取分类详情
@app.route('/api/knowledge/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    try:
        category = knowledge_base.get_category(category_id)
        if category:
            return jsonify({'success': True, 'category': category})
        else:
            return jsonify({'success': False, 'message': '分类不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取分类详情失败: {str(e)}'})

# 创建分类
@app.route('/api/knowledge/categories', methods=['POST'])
def create_category():
    try:
        data = request.get_json()
        category = knowledge_base.create_category(data)
        return jsonify({'success': True, 'category': category})
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建分类失败: {str(e)}'})

# 更新分类
@app.route('/api/knowledge/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    try:
        data = request.get_json()
        category = knowledge_base.update_category(category_id, data)
        if category:
            return jsonify({'success': True, 'category': category})
        else:
            return jsonify({'success': False, 'message': '分类不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新分类失败: {str(e)}'})

# 删除分类
@app.route('/api/knowledge/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        success = knowledge_base.delete_category(category_id)
        if success:
            return jsonify({'success': True, 'message': '删除分类成功'})
        else:
            return jsonify({'success': False, 'message': '分类不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除分类失败: {str(e)}'})

# 标签管理

# 获取标签列表
@app.route('/api/knowledge/tags', methods=['GET'])
def get_tags():
    try:
        tags = knowledge_base.get_tags()
        return jsonify({'success': True, 'tags': tags})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取标签列表失败: {str(e)}'})

# 获取标签详情
@app.route('/api/knowledge/tags/<tag_id>', methods=['GET'])
def get_tag(tag_id):
    try:
        tag = knowledge_base.get_tag(tag_id)
        if tag:
            return jsonify({'success': True, 'tag': tag})
        else:
            return jsonify({'success': False, 'message': '标签不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取标签详情失败: {str(e)}'})

# 创建标签
@app.route('/api/knowledge/tags', methods=['POST'])
def create_tag():
    try:
        data = request.get_json()
        tag = knowledge_base.create_tag(data)
        return jsonify({'success': True, 'tag': tag})
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建标签失败: {str(e)}'})

# 更新标签
@app.route('/api/knowledge/tags/<tag_id>', methods=['PUT'])
def update_tag(tag_id):
    try:
        data = request.get_json()
        tag = knowledge_base.update_tag(tag_id, data)
        if tag:
            return jsonify({'success': True, 'tag': tag})
        else:
            return jsonify({'success': False, 'message': '标签不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新标签失败: {str(e)}'})

# 删除标签
@app.route('/api/knowledge/tags/<tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    try:
        success = knowledge_base.delete_tag(tag_id)
        if success:
            return jsonify({'success': True, 'message': '删除标签成功'})
        else:
            return jsonify({'success': False, 'message': '标签不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除标签失败: {str(e)}'})

# 知识库扩展API

# 获取文档版本列表
@app.route('/api/knowledge/documents/<document_id>/versions', methods=['GET'])
def get_document_versions(document_id):
    try:
        versions = knowledge_base.get_document_versions(document_id)
        return jsonify({'success': True, 'versions': versions})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取文档版本列表失败: {str(e)}'})

# 获取指定文档版本
@app.route('/api/knowledge/documents/versions/<version_id>', methods=['GET'])
def get_document_version(version_id):
    try:
        version = knowledge_base.get_document_version(version_id)
        if version:
            return jsonify({'success': True, 'version': version})
        else:
            return jsonify({'success': False, 'message': '版本不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取文档版本失败: {str(e)}'})

# 恢复文档到指定版本
@app.route('/api/knowledge/documents/<document_id>/versions/<version_id>/restore', methods=['POST'])
def restore_document_version(document_id, version_id):
    try:
        document = knowledge_base.restore_document_version(document_id, version_id)
        if document:
            return jsonify({'success': True, 'document': document})
        else:
            return jsonify({'success': False, 'message': '文档或版本不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'恢复文档版本失败: {str(e)}'})

# 添加文档权限
@app.route('/api/knowledge/documents/<document_id>/permissions', methods=['POST'])
def add_document_permission(document_id):
    try:
        data = request.get_json()
        # 添加document_id到数据中
        data['document_id'] = document_id
        permission = knowledge_base.add_document_permission(data)
        return jsonify({'success': True, 'permission': permission})
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加文档权限失败: {str(e)}'})

# 获取文档权限
@app.route('/api/knowledge/documents/<document_id>/permissions', methods=['GET'])
def get_document_permissions(document_id):
    try:
        permissions = knowledge_base.get_document_permissions(document_id)
        return jsonify({'success': True, 'permissions': permissions})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取文档权限失败: {str(e)}'})

# 更新文档权限
@app.route('/api/knowledge/documents/permissions/<permission_id>', methods=['PUT'])
def update_document_permission(permission_id):
    try:
        data = request.get_json()
        permission = knowledge_base.update_document_permission(permission_id, data)
        if permission:
            return jsonify({'success': True, 'permission': permission})
        else:
            return jsonify({'success': False, 'message': '权限不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新文档权限失败: {str(e)}'})

# 删除文档权限
@app.route('/api/knowledge/documents/permissions/<permission_id>', methods=['DELETE'])
def delete_document_permission(permission_id):
    try:
        success = knowledge_base.delete_document_permission(permission_id)
        if success:
            return jsonify({'success': True, 'message': '删除文档权限成功'})
        else:
            return jsonify({'success': False, 'message': '权限不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除文档权限失败: {str(e)}'})

# 检查文档权限
@app.route('/api/knowledge/documents/<document_id>/check-permission', methods=['GET'])
def check_document_permission(document_id):
    try:
        user_id = request.args.get('user_id', '')
        permission_type = request.args.get('permission_type', 'read')
        has_permission = knowledge_base.check_document_permission(document_id, user_id, permission_type)
        return jsonify({'success': True, 'has_permission': has_permission})
    except Exception as e:
        return jsonify({'success': False, 'message': f'检查文档权限失败: {str(e)}'})

# 获取知识库统计信息
@app.route('/api/knowledge/statistics', methods=['GET'])
def get_knowledge_statistics():
    try:
        statistics = knowledge_base.get_document_statistics()
        return jsonify({'success': True, 'statistics': statistics})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取知识库统计信息失败: {str(e)}'})

import socket
import subprocess
import sys

def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        result = s.connect_ex(('127.0.0.1', port))
        return result == 0

def get_process_using_port(port):
    """获取占用端口的进程信息"""
    try:
        # 使用netstat命令获取端口占用情况
        cmd = f'netstat -ano | findstr :{port}'
        result = subprocess.check_output(cmd, shell=True, text=True)
        # 提取PID
        lines = result.strip().split('\n')
        if lines:
            # 取最后一行的PID
            last_line = lines[-1]
            pid = last_line.split()[-1]
            # 获取进程名称
            cmd = f'tasklist /fi "PID eq {pid}" /fo csv /nh'
            task_result = subprocess.check_output(cmd, shell=True, text=True)
            return pid, task_result.strip()
    except Exception as e:
        pass
    return None, None

def is_hos_office_platform(pid):
    """判断进程是否为HOS办公平台"""
    try:
        # 获取进程命令行
        cmd = f'wmic process where ProcessID={pid} get CommandLine /format:list'
        result = subprocess.check_output(cmd, shell=True, text=True)
        # 检查命令行是否包含HOS办公平台相关信息
        return 'weekly_report_tool.py' in result or 'app.py' in result
    except Exception as e:
        pass
    return False

def main():
    """主函数，处理端口自动分配"""
    base_port = 50000
    max_attempts = 100
    use_port = base_port
    
    print("=== HOS可扩展式办公平台 ===")
    print(f"正在启动，基础端口: {base_port}")
    
    for attempt in range(max_attempts):
        print(f"检测端口: {use_port}")
        
        if not is_port_in_use(use_port):
            # 端口可用，直接使用
            print(f"端口 {use_port} 可用，使用该端口启动服务")
            break
        
        # 端口被占用，检查是否是HOS办公平台
        pid, process_info = get_process_using_port(use_port)
        if pid:
            print(f"端口 {use_port} 已被占用，PID: {pid}")
            print(f"进程信息: {process_info}")
            
            # 检查是否为HOS办公平台
            if is_hos_office_platform(pid):
                print("检测到这是另一个HOS办公平台实例")
                
                # 询问用户选择
                print("\n请选择操作：")
                print("1. 尝试使用下一个可用端口")
                print("2. 关闭现有HOS办公平台并在当前端口启动")
                print("3. 退出程序")
                
                choice = input("请输入选择 (1/2/3): ").strip()
                
                if choice == '1':
                    print("将尝试使用下一个端口")
                elif choice == '2':
                    # 关闭现有HOS办公平台进程
                    print(f"正在关闭占用端口 {use_port} 的HOS办公平台进程...")
                    try:
                        subprocess.run(f'taskkill /pid {pid} /f', shell=True, check=True)
                        print(f"进程 {pid} 已成功关闭")
                        print(f"现在使用端口 {use_port} 启动服务")
                        break
                    except subprocess.CalledProcessError:
                        print(f"关闭进程 {pid} 失败，将尝试使用下一个端口")
                elif choice == '3':
                    print("程序退出")
                    sys.exit(0)
                else:
                    print("无效选择，将尝试使用下一个端口")
            else:
                print("这不是HOS办公平台实例，继续尝试下一个端口")
        
        # 尝试下一个端口
        use_port += 1
    else:
        print(f"尝试了 {max_attempts} 个端口，均被占用，程序退出")
        sys.exit(1)
    
    print(f"\n启动HOS办公平台服务...")
    print(f"服务地址: http://127.0.0.1:{use_port}")
    print("按 Ctrl+C 停止服务\n")
    
    # 启动Flask应用
    app.run(host='127.0.0.1', port=use_port, debug=False, threaded=True)

if __name__ == '__main__':
    main()
