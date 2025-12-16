// 全局变量
let currentFilename = null;
let currentTemplateId = null;
let currentWorkflowId = null;
let isAppSelectionMode = false;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化事件监听
    initEventListeners();
    
    // 加载API配置
    loadAPIConfig();
    
    // 加载模板配置
    loadTemplateSettings();
    
    // 加载工作流列表
    loadWorkflows();
    
    // 加载自定义模块
    loadCustomModules();
    
    // 加载模板列表
    loadTemplatesForSelection();
    
    // 初始化文档管理功能
    initDocumentManagement();
    
    // 初始化DOCX上传功能
    initDocxUpload();
});

// 初始化事件监听器
function initEventListeners() {
    // API来源切换
    const apiSourceSelect = document.getElementById('api-source');
    if (apiSourceSelect) {
        apiSourceSelect.addEventListener('change', switchAPISource);
    }
    
    // 单文档生成
const generateBtn = document.getElementById('generate-btn');
if (generateBtn) {
    generateBtn.addEventListener('click', () => {
        if (validatePrompt()) {
            generateReport();
        }
    });
}
    
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveReport);
    }
    
    // 批量文档生成
    const batchGenerateBtn = document.getElementById('batch-generate-btn');
    if (batchGenerateBtn) {
        batchGenerateBtn.addEventListener('click', batchGenerateReports);
    }
    
    const batchSaveBtn = document.getElementById('batch-save-btn');
    if (batchSaveBtn) {
        batchSaveBtn.addEventListener('click', batchSaveReports);
    }
    
    // 批量提示词Excel导入
    const importPromptsExcelBtn = document.getElementById('import-prompts-excel');
    if (importPromptsExcelBtn) {
        importPromptsExcelBtn.addEventListener('click', () => {
            document.getElementById('prompts-excel-input').click();
        });
    }
    
    const promptsExcelInput = document.getElementById('prompts-excel-input');
    if (promptsExcelInput) {
        promptsExcelInput.addEventListener('change', handlePromptsExcelFileSelect);
    }
    
    // 清空提示词
    const clearPromptsBtn = document.getElementById('clear-prompts');
    if (clearPromptsBtn) {
        clearPromptsBtn.addEventListener('click', clearPrompts);
    }
    
    // 定期更新任务列表
    setInterval(updateTasksList, 3000);
    // 初始加载任务列表
    updateTasksList();
    
    // 文档管理 - 这些按钮可能在文档管理页面才存在
    // 它们的事件监听器在initDocumentManagement函数中绑定
    
    // API设置表单提交
    const deepseekForm = document.getElementById('deepseek-form');
    if (deepseekForm) {
        deepseekForm.addEventListener('submit', saveDeepSeekConfig);
    }
    
    const ollamaForm = document.getElementById('ollama-form');
    if (ollamaForm) {
        ollamaForm.addEventListener('submit', saveOllamaConfig);
    }
    
    // 模板配置表单提交
    const outputBeforeForm = document.getElementById('output-before-form');
    if (outputBeforeForm) {
        outputBeforeForm.addEventListener('submit', saveOutputBeforeSettings);
    }
    
    const docxSettingsForm = document.getElementById('docx-settings-form');
    if (docxSettingsForm) {
        docxSettingsForm.addEventListener('submit', saveOutputSettings);
    }
    
    const pdfSettingsForm = document.getElementById('pdf-settings-form');
    if (pdfSettingsForm) {
        pdfSettingsForm.addEventListener('submit', saveOutputSettings);
    }
    
    const outputAfterForm = document.getElementById('output-after-form');
    if (outputAfterForm) {
        outputAfterForm.addEventListener('submit', saveOutputAfterSettings);
    }
    
    // 工作流表单提交
    const workflowForm = document.getElementById('workflow-form');
    if (workflowForm) {
        workflowForm.addEventListener('submit', saveWorkflow);
    }
    
    // 侧边栏切换
    const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', toggleSidebar);
    }
    
    // 导航模式切换
    const navModeToggle = document.getElementById('nav-mode-toggle');
    if (navModeToggle) {
        navModeToggle.addEventListener('click', toggleNavigationMode);
    }
    
    const exitAppSelectionBtn = document.getElementById('exit-app-selection-btn');
    if (exitAppSelectionBtn) {
        exitAppSelectionBtn.addEventListener('click', toggleNavigationMode);
    }
    
    // 模板选择
    const templateSelect = document.getElementById('template-select');
    if (templateSelect) {
        templateSelect.addEventListener('change', function() {
            currentTemplateId = this.value || null;
        });
    }
    
    const batchTemplateSelect = document.getElementById('batch-template-select');
    if (batchTemplateSelect) {
        batchTemplateSelect.addEventListener('change', function() {
            currentTemplateId = this.value || null;
        });
    }
}

// 切换API Key可见性
function toggleApiKeyVisibility(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    }
}

// 侧边栏切换
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    sidebar.classList.toggle('open');
    mainContent.classList.toggle('shifted');
}

// 应用式导航界面切换
function toggleNavigationMode() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const appSelectionMode = document.getElementById('app-selection-mode');
    
    isAppSelectionMode = !isAppSelectionMode;
    
    if (isAppSelectionMode) {
        // 显示应用式选择界面
        appSelectionMode.style.display = 'flex';
        sidebar.style.display = 'none';
        mainContent.style.display = 'none';
    } else {
        // 显示正常导航界面
        appSelectionMode.style.display = 'none';
        sidebar.style.display = 'block';
        mainContent.style.display = 'block';
    }
}

// 页面切换
function showPage(pageId) {
    // 隐藏所有页面
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        page.classList.remove('active');
    });
    
    // 显示目标页面
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    // 更新菜单项状态
    const menuItems = document.querySelectorAll('.sidebar-nav .nav-link');
    menuItems.forEach(item => {
        item.classList.remove('active');
    });
    
    const targetMenuItem = document.getElementById(`menu-${pageId}`);
    if (targetMenuItem) {
        targetMenuItem.classList.add('active');
    }
}

// API来源切换
function switchAPISource() {
    const apiSource = document.getElementById('api-source').value;
    const apiStatus = document.getElementById('api-status');
    
    // 显示加载状态
    apiStatus.textContent = '正在切换API...';
    
    // 发送请求
    fetch('/api/switch_api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ api_source: apiSource })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            apiStatus.textContent = data.status;
        } else {
            apiStatus.textContent = `切换失败: ${data.message}`;
        }
    })
    .catch(error => {
        apiStatus.textContent = `切换失败: ${error.message}`;
    });
}

// 加载API配置
function loadAPIConfig() {
    // 从后端获取API Key
    fetch('/api/get_api_key')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('deepseek-api-key').value = data.api_key;
            } else {
                console.error('获取API Key失败:', data.message);
            }
        })
        .catch(error => {
            console.error('获取API Key失败:', error);
        });
    
    // 设置其他默认值
    document.getElementById('deepseek-base-url').value = localStorage.getItem('deepseek-base-url') || 'https://api.deepseek.com/v1/chat/completions';
    document.getElementById('deepseek-model').value = localStorage.getItem('deepseek-model') || 'deepseek-chat';
    document.getElementById('deepseek-temperature').value = localStorage.getItem('deepseek-temperature') || '0.7';
    document.getElementById('deepseek-max-tokens').value = localStorage.getItem('deepseek-max-tokens') || '2000';
    
    // Ollama默认配置
    document.getElementById('ollama-base-url').value = localStorage.getItem('ollama-base-url') || 'http://localhost:11434/v1/chat/completions';
    document.getElementById('ollama-model').value = localStorage.getItem('ollama-model') || 'llama3';
    document.getElementById('ollama-temperature').value = localStorage.getItem('ollama-temperature') || '0.7';
    document.getElementById('ollama-max-tokens').value = localStorage.getItem('ollama-max-tokens') || '2000';
}

// 保存DeepSeek配置
function saveDeepSeekConfig(e) {
    e.preventDefault();
    
    const config = {
        api_key: document.getElementById('deepseek-api-key').value,
        base_url: document.getElementById('deepseek-base-url').value,
        model: document.getElementById('deepseek-model').value,
        temperature: document.getElementById('deepseek-temperature').value,
        max_tokens: document.getElementById('deepseek-max-tokens').value
    };
    
    // 保存到localStorage
    localStorage.setItem('deepseek-api-key', config.api_key);
    localStorage.setItem('deepseek-base-url', config.base_url);
    localStorage.setItem('deepseek-model', config.model);
    localStorage.setItem('deepseek-temperature', config.temperature);
    localStorage.setItem('deepseek-max-tokens', config.max_tokens);
    
    // 保存API Key到后端
    fetch('/api/update_api_key', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ api_key: config.api_key })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('DeepSeek配置已保存');
        } else {
            alert('保存配置失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('保存API Key失败:', error);
        alert('保存配置失败: ' + error.message);
    });
}

// 保存Ollama配置
function saveOllamaConfig(e) {
    e.preventDefault();
    
    const config = {
        base_url: document.getElementById('ollama-base-url').value,
        model: document.getElementById('ollama-model').value,
        temperature: document.getElementById('ollama-temperature').value,
        max_tokens: document.getElementById('ollama-max-tokens').value
    };
    
    // 保存到localStorage
    localStorage.setItem('ollama-base-url', config.base_url);
    localStorage.setItem('ollama-model', config.model);
    localStorage.setItem('ollama-temperature', config.temperature);
    localStorage.setItem('ollama-max-tokens', config.max_tokens);
    
    alert('Ollama配置已保存');
}

// 测试Ollama连接
function testOllamaConnection() {
    const testBtn = document.getElementById('test-ollama-connection');
    const statusSpan = document.getElementById('ollama-connection-status');
    
    // 显示加载状态
    testBtn.disabled = true;
    testBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 测试中...';
    statusSpan.innerHTML = '<span class="text-info"><i class="bi bi-hourglass-split"></i> 正在测试连接...</span>';
    
    // 获取当前Ollama配置
    const baseUrl = document.getElementById('ollama-base-url').value;
    const model = document.getElementById('ollama-model').value;
    
    // 发送测试请求
    fetch('/api/test_ollama_connection', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            base_url: baseUrl,
            model: model
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            statusSpan.innerHTML = '<span class="text-success"><i class="bi bi-check-circle"></i> 连接成功</span>';
        } else {
            statusSpan.innerHTML = `<span class="text-danger"><i class="bi bi-x-circle"></i> 连接失败: ${data.message}</span>`;
        }
    })
    .catch(error => {
        statusSpan.innerHTML = `<span class="text-danger"><i class="bi bi-x-circle"></i> 连接失败: ${error.message}</span>`;
    })
    .finally(() => {
        // 恢复按钮状态
        testBtn.disabled = false;
        testBtn.innerHTML = '测试连接';
    });
}

// 模板配置功能

// 加载模板设置
function loadTemplateSettings() {
    fetch('/api/system/template-settings')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const settings = data.settings;
            
            // 填充输出前设置
            document.getElementById('output-format').value = settings.output_before.format || 'txt';
            document.getElementById('output-encoding').value = settings.output_before.encoding || 'utf-8';
            
            // 填充输出时设置
            if (settings.output_during.docx) {
                document.getElementById('docx-font-name').value = settings.output_during.docx.font_name || '微软雅黑';
                document.getElementById('docx-font-size').value = settings.output_during.docx.font_size || 12;
                document.getElementById('docx-line-spacing').value = settings.output_during.docx.line_spacing || 1.5;
                document.getElementById('docx-margin-top').value = settings.output_during.docx.margin?.top || 2.54;
                document.getElementById('docx-margin-right').value = settings.output_during.docx.margin?.right || 2.54;
                document.getElementById('docx-margin-bottom').value = settings.output_during.docx.margin?.bottom || 2.54;
                document.getElementById('docx-margin-left').value = settings.output_during.docx.margin?.left || 2.54;
            }
            
            if (settings.output_during.pdf) {
                document.getElementById('pdf-page-size').value = settings.output_during.pdf.page_size || 'A4';
                document.getElementById('pdf-orientation').value = settings.output_during.pdf.orientation || 'portrait';
            }
            
            // 填充输出后设置
            document.getElementById('default-save-location').value = settings.output_after.default_save_location || '';
            document.getElementById('naming-rule').value = settings.output_after.naming_rule || '{date}_{user}_{type}.{format}';
            document.getElementById('auto-save').checked = settings.output_after.auto_save || true;
        } else {
            console.error('加载模板配置失败:', data.message);
        }
    })
    .catch(error => {
        console.error('加载模板配置失败:', error);
    });
}

// 加载模板列表用于选择
function loadTemplatesForSelection() {
    fetch('/api/templates')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const templates = data.templates;
            
            // 填充单文档生成模板选择
            const templateSelect = document.getElementById('template-select');
            if (templateSelect) {
                // 保存当前选中的值
                const currentValue = templateSelect.value;
                
                // 清空现有选项，保留默认选项
                templateSelect.innerHTML = '<option value="">使用默认模板</option>';
                
                // 添加模板选项
                templates.forEach(template => {
                    const option = document.createElement('option');
                    option.value = template.id;
                    option.textContent = template.name;
                    if (template.is_default) {
                        option.textContent += ' (默认)';
                    }
                    templateSelect.appendChild(option);
                });
                
                // 恢复当前选中的值
                templateSelect.value = currentValue;
            }
            
            // 填充批量生成模板选择
            const batchTemplateSelect = document.getElementById('batch-template-select');
            if (batchTemplateSelect) {
                // 保存当前选中的值
                const currentValue = batchTemplateSelect.value;
                
                // 清空现有选项，保留默认选项
                batchTemplateSelect.innerHTML = '<option value="">使用默认模板</option>';
                
                // 添加模板选项
                templates.forEach(template => {
                    const option = document.createElement('option');
                    option.value = template.id;
                    option.textContent = template.name;
                    if (template.is_default) {
                        option.textContent += ' (默认)';
                    }
                    batchTemplateSelect.appendChild(option);
                });
                
                // 恢复当前选中的值
                batchTemplateSelect.value = currentValue;
            }
        } else {
            console.error('加载模板列表失败:', data.message);
        }
    })
    .catch(error => {
        console.error('加载模板列表失败:', error);
    });
}

// 保存输出前设置
function saveOutputBeforeSettings(e) {
    e.preventDefault();
    saveOutputSettings();
}

// 保存输出时设置
function saveOutputSettings(e) {
    if (e) e.preventDefault();
    
    const settings = {
        output_before: {
            format: document.getElementById('output-format').value,
            encoding: document.getElementById('output-encoding').value
        },
        output_during: {
            docx: {
                font_name: document.getElementById('docx-font-name').value,
                font_size: parseInt(document.getElementById('docx-font-size').value),
                margin: {
                    top: parseFloat(document.getElementById('docx-margin-top').value),
                    right: parseFloat(document.getElementById('docx-margin-right').value),
                    bottom: parseFloat(document.getElementById('docx-margin-bottom').value),
                    left: parseFloat(document.getElementById('docx-margin-left').value)
                },
                line_spacing: parseFloat(document.getElementById('docx-line-spacing').value)
            },
            pdf: {
                page_size: document.getElementById('pdf-page-size').value,
                orientation: document.getElementById('pdf-orientation').value
            }
        },
        output_after: {
            default_save_location: document.getElementById('default-save-location').value,
            naming_rule: document.getElementById('naming-rule').value,
            auto_save: document.getElementById('auto-save').checked
        }
    };
    
    fetch('/api/system/template-settings', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('输出设置已保存');
        } else {
            alert('保存输出设置失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('保存输出设置失败: ' + error.message);
    });
}

// 保存输出后设置
function saveOutputAfterSettings(e) {
    e.preventDefault();
    saveOutputSettings();
}

// 模板管理功能

// 页面切换时加载模板列表
document.addEventListener('DOMContentLoaded', function() {
    // 监听模板配置页面显示
    const templatePage = document.getElementById('template-settings');
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'class') {
                if (templatePage.classList.contains('active')) {
                    loadTemplates();
                }
            }
        });
    });
    
    observer.observe(templatePage, { attributes: true });
});

// 加载模板列表
function loadTemplates() {
    fetch('/api/templates')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            renderTemplatesList(data.templates);
        } else {
            alert('加载模板列表失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('加载模板列表失败: ' + error.message);
    });
}

// 渲染模板列表
function renderTemplatesList(templates) {
    const templatesList = document.getElementById('templates-list');
    templatesList.innerHTML = '';
    
    templates.forEach(template => {
        const listItem = document.createElement('a');
        listItem.className = 'list-group-item list-group-item-action';
        listItem.setAttribute('data-template-id', template.id);
        listItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6>${template.name}</h6>
                    <small class="text-muted">${template.description || '无描述'}</small>
                </div>
                <div>
                    ${template.is_default ? '<span class="badge bg-primary">默认</span>' : ''}
                    ${template.id === currentTemplateId ? '<span class="badge bg-success">当前</span>' : ''}
                </div>
            </div>
        `;
        
        listItem.addEventListener('click', function() {
            loadTemplateDetails(template.id);
        });
        
        templatesList.appendChild(listItem);
    });
}

// 加载模板详情
function loadTemplateDetails(templateId) {
    fetch(`/api/templates/${templateId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const template = data.template;
            currentTemplateId = template.id;
            
            // 填充表单
            document.getElementById('template-id').value = template.id;
            document.getElementById('template-name').value = template.name;
            document.getElementById('template-description').value = template.description || '';
            document.getElementById('template-content').value = template.content || '';
            
            // 更新标题
            document.getElementById('template-editor-title').textContent = `编辑模板: ${template.name}`;
            
            // 更新列表项的激活状态
            updateTemplatesListActive(templateId);
        } else {
            alert('加载模板失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('加载模板失败: ' + error.message);
    });
}

// 更新模板列表的激活状态
function updateTemplatesListActive(templateId) {
    const items = document.querySelectorAll('#templates-list .list-group-item');
    items.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-template-id') === templateId) {
            item.classList.add('active');
        }
    });
}

// 新建模板
function createNewTemplate() {
    currentTemplateId = null;
    
    // 清空表单
    document.getElementById('template-id').value = '';
    document.getElementById('template-name').value = '';
    document.getElementById('template-description').value = '';
    document.getElementById('template-content').value = '';
    
    // 更新标题
    document.getElementById('template-editor-title').textContent = '新建模板';
    
    // 清除列表激活状态
    const items = document.querySelectorAll('#templates-list .list-group-item');
    items.forEach(item => {
        item.classList.remove('active');
    });
}

// 保存模板
function saveTemplate() {
    const templateId = document.getElementById('template-id').value;
    const name = document.getElementById('template-name').value;
    const description = document.getElementById('template-description').value;
    const content = document.getElementById('template-content').value;
    
    if (!name.trim()) {
        alert('请输入模板名称');
        return;
    }
    
    if (!content.trim()) {
        alert('请输入模板内容');
        return;
    }
    
    const url = templateId ? `/api/templates/${templateId}` : '/api/templates';
    const method = templateId ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            description: description,
            content: content
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('模板保存成功');
            loadTemplates();
            if (data.template) {
                loadTemplateDetails(data.template.id);
            }
        } else {
            alert('保存模板失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('保存模板失败: ' + error.message);
    });
}

// 设置为当前模板
function setAsCurrentTemplate() {
    if (!currentTemplateId) {
        alert('请先选择或创建一个模板');
        return;
    }
    
    fetch('/api/templates/current', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            template_id: currentTemplateId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('已设为当前模板');
            loadTemplates();
        } else {
            alert('设置当前模板失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('设置当前模板失败: ' + error.message);
    });
}

// 导出模板
function exportTemplate() {
    if (!currentTemplateId) {
        alert('请先选择一个模板');
        return;
    }
    
    fetch(`/api/templates/${currentTemplateId}/export`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const template = data.template;
            const content = JSON.stringify(template, null, 2);
            const blob = new Blob([content], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${template.name}.json`;
            a.click();
            URL.revokeObjectURL(url);
        } else {
            alert('导出模板失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('导出模板失败: ' + error.message);
    });
}

// 派生模板
function deriveTemplate() {
    if (!currentTemplateId) {
        alert('请先选择一个模板');
        return;
    }
    
    const newName = prompt('请输入新模板名称:');
    if (!newName || !newName.trim()) {
        alert('模板名称不能为空');
        return;
    }
    
    const newDescription = prompt('请输入新模板描述 (可选):');
    
    fetch(`/api/templates/${currentTemplateId}/derive`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: newName.trim(),
            description: newDescription || ''
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('模板派生成功！');
            loadTemplates();
            // 加载新派生的模板
            loadTemplateDetails(data.template.id);
        } else {
            alert('派生模板失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('派生模板失败: ' + error.message);
    });
}

// 删除模板
function deleteTemplate() {
    if (!currentTemplateId) {
        alert('请先选择一个模板');
        return;
    }
    
    if (!confirm('确定要删除这个模板吗？')) {
        return;
    }
    
    fetch(`/api/templates/${currentTemplateId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('模板删除成功');
            createNewTemplate();
            loadTemplates();
        } else {
            alert('删除模板失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('删除模板失败: ' + error.message);
    });
}

// 导入模板
function importTemplate() {
    const name = document.getElementById('import-template-name').value;
    const content = document.getElementById('import-template-content').value;
    
    if (!name.trim()) {
        alert('请输入模板名称');
        return;
    }
    
    if (!content.trim()) {
        alert('请输入模板内容');
        return;
    }
    
    fetch('/api/templates/import', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            content: content,
            description: '导入的模板'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('模板导入成功');
            loadTemplates();
            // 清空导入表单
            document.getElementById('import-template-name').value = '';
            document.getElementById('import-template-content').value = '';
        } else {
            alert('导入模板失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('导入模板失败: ' + error.message);
    });
}

// 初始化DOCX文件上传事件
function initDocxUpload() {
    const docxFileUpload = document.getElementById('docx-file-upload');
    if (docxFileUpload) {
        docxFileUpload.addEventListener('change', handleDocxUpload);
    }
}

// 处理DOCX模板上传
function handleDocxUpload(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }
    
    // 显示文件名
    const fileName = file.name;
    const confirmUpload = confirm(`确定要导入DOCX模板：${fileName}吗？`);
    
    if (!confirmUpload) {
        // 清空文件选择
        event.target.value = '';
        return;
    }
    
    // 创建FormData对象
    const formData = new FormData();
    formData.append('file', file);
    
    // 可以添加其他参数
    formData.append('name', fileName.replace('.docx', ''));
    formData.append('description', `从DOCX导入的模板: ${fileName}`);
    
    // 显示加载状态
    const importBtn = document.querySelector('[onclick="document.getElementById(\'docx-file-upload\').click()"]');
    importBtn.disabled = true;
    importBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 导入中...';
    
    // 发送请求
    fetch('/api/templates/import_docx', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('DOCX模板导入成功！');
            loadTemplates();
            // 清空文件选择
            event.target.value = '';
        } else {
            alert('导入DOCX模板失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('导入DOCX模板失败: ' + error.message);
    })
    .finally(() => {
        // 恢复按钮状态
        importBtn.disabled = false;
        importBtn.innerHTML = '<i class="bi bi-file-earmark-word"></i> 导入DOCX模板';
    });
}

// 预览模板
function previewTemplate(templateId) {
    fetch(`/api/templates/${templateId}/structure`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const structure = data.structure;
            const previewContainer = document.getElementById('template-preview');
            
            // 生成预览HTML
            let previewHtml = '<h6>模板结构预览</h6>';
            
            // 添加表格信息
            if (structure.tables && structure.tables.length > 0) {
                previewHtml += `
                    <div class="mt-3">
                        <h7>表格信息:</h7>
                        <ul class="list-unstyled mt-1">
                `;
                structure.tables.forEach((table, index) => {
                    previewHtml += `<li><i class="bi bi-table"></i> 表格 ${index + 1}: ${table.rows}行 × ${table.cols}列</li>`;
                });
                previewHtml += '</ul></div>';
            }
            
            // 添加图片信息
            if (structure.images && structure.images.length > 0) {
                previewHtml += `
                    <div class="mt-3">
                        <h7>图片信息:</h7>
                        <ul class="list-unstyled mt-1">
                `;
                structure.images.forEach((image, index) => {
                    previewHtml += `<li><i class="bi bi-image"></i> 图片 ${index + 1}: ${image.width.toFixed(1)}×${image.height.toFixed(1)}英寸</li>`;
                });
                previewHtml += '</ul></div>';
            }
            
            // 添加段落信息
            if (structure.paragraphs && structure.paragraphs.length > 0) {
                previewHtml += `
                    <div class="mt-3">
                        <h7>段落信息:</h7>
                        <ul class="list-unstyled mt-1">
                            <li><i class="bi bi-text-paragraph"></i> 总段落数: ${structure.paragraphs.length}</li>
                `;
                
                // 统计不同类型的段落
                const titleCount = structure.paragraphs.filter(p => p.is_title).length;
                const listCount = structure.paragraphs.filter(p => p.is_list).length;
                
                if (titleCount > 0) {
                    previewHtml += `<li><i class="bi bi-type-h1"></i> 标题段落: ${titleCount}</li>`;
                }
                if (listCount > 0) {
                    previewHtml += `<li><i class="bi bi-list-ul"></i> 列表段落: ${listCount}</li>`;
                }
                
                previewHtml += '</ul></div>';
            }
            
            // 添加占位符信息
            if (structure.placeholders && structure.placeholders.length > 0) {
                previewHtml += `
                    <div class="mt-3">
                        <h7>占位符:</h7>
                        <div class="d-flex flex-wrap gap-2 mt-1">
                `;
                structure.placeholders.forEach(placeholder => {
                    previewHtml += `<span class="badge bg-secondary">${placeholder.placeholder}</span>`;
                });
                previewHtml += '</div></div>';
            }
            
            previewContainer.innerHTML = previewHtml;
        } else {
            alert('获取模板结构失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('预览模板失败: ' + error.message);
    });
}

// 更新模板列表项，添加预览功能
function updateTemplatesListActive(templateId) {
    const items = document.querySelectorAll('#templates-list .list-group-item');
    items.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-template-id') === templateId) {
            item.classList.add('active');
            // 预览选中的模板
            previewTemplate(templateId);
        }
    });
}

// 搜索模板
function searchTemplates(keyword) {
    const items = document.querySelectorAll('#templates-list .list-group-item');
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(keyword.toLowerCase())) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// 工作流管理功能

// 加载工作流列表
function loadWorkflows() {
    fetch('/api/workflows')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            renderWorkflowsList(data.workflows);
        } else {
            console.error('加载工作流列表失败:', data.message);
        }
    })
    .catch(error => {
        console.error('加载工作流列表失败:', error);
    });
}

// 渲染工作流列表
function renderWorkflowsList(workflows) {
    const workflowsList = document.getElementById('workflows-list');
    workflowsList.innerHTML = '';
    
    workflows.forEach(workflow => {
        const listItem = document.createElement('a');
        listItem.className = 'list-group-item list-group-item-action';
        listItem.setAttribute('data-workflow-id', workflow.id);
        listItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6>${workflow.name}</h6>
                    <small class="text-muted">${workflow.description || '无描述'}</small>
                </div>
                <div>
                    <small class="text-muted">${workflow.created_at}</small>
                </div>
            </div>
        `;
        
        listItem.addEventListener('click', function() {
            loadWorkflowDetails(workflow.id);
        });
        
        workflowsList.appendChild(listItem);
    });
}

// 加载工作流详情
function loadWorkflowDetails(workflowId) {
    fetch(`/api/workflows/${workflowId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const workflow = data.workflow;
            currentWorkflowId = workflow.id;
            
            // 填充表单
            document.getElementById('workflow-id').value = workflow.id;
            document.getElementById('workflow-name').value = workflow.name;
            document.getElementById('workflow-description').value = workflow.description || '';
            document.getElementById('workflow-steps').value = JSON.stringify(workflow.steps || [], null, 2);
            
            // 更新标题
            document.getElementById('workflow-editor-title').textContent = `编辑工作流: ${workflow.name}`;
            
            // 更新列表项的激活状态
            updateWorkflowsListActive(workflowId);
        } else {
            alert('加载工作流失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('加载工作流失败: ' + error.message);
    });
}

// 更新工作流列表的激活状态
function updateWorkflowsListActive(workflowId) {
    const items = document.querySelectorAll('#workflows-list .list-group-item');
    items.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-workflow-id') === workflowId) {
            item.classList.add('active');
        }
    });
}

// 新建工作流
function createNewWorkflow() {
    currentWorkflowId = null;
    
    // 清空表单
    document.getElementById('workflow-id').value = '';
    document.getElementById('workflow-name').value = '';
    document.getElementById('workflow-description').value = '';
    document.getElementById('workflow-steps').value = '[]';
    
    // 更新标题
    document.getElementById('workflow-editor-title').textContent = '新建工作流';
    
    // 清除列表激活状态
    const items = document.querySelectorAll('#workflows-list .list-group-item');
    items.forEach(item => {
        item.classList.remove('active');
    });
}

// 保存工作流
function saveWorkflow(e) {
    if (e) e.preventDefault();
    
    const workflowId = document.getElementById('workflow-id').value;
    const name = document.getElementById('workflow-name').value;
    const description = document.getElementById('workflow-description').value;
    const steps = document.getElementById('workflow-steps').value;
    
    if (!name.trim()) {
        alert('请输入工作流名称');
        return;
    }
    
    let stepsJson;
    try {
        stepsJson = JSON.parse(steps);
    } catch (error) {
        alert('工作流步骤格式错误，请检查JSON格式');
        return;
    }
    
    const workflowData = {
        name: name,
        description: description,
        steps: stepsJson
    };
    
    const url = workflowId ? `/api/workflows/${workflowId}` : '/api/workflows';
    const method = workflowId ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(workflowData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('工作流保存成功');
            loadWorkflows();
            if (data.workflow) {
                loadWorkflowDetails(data.workflow.id);
            }
        } else {
            alert('保存工作流失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('保存工作流失败: ' + error.message);
    });
}

// 运行工作流
function runWorkflow() {
    if (!currentWorkflowId) {
        alert('请先选择一个工作流');
        return;
    }
    
    alert('工作流运行功能正在开发中');
}

// AI生成工作流
function generateWorkflowByAI() {
    const promptInput = document.getElementById('workflow-prompt');
    const workflowSteps = document.getElementById('workflow-steps');
    const generateBtn = document.querySelector('[onclick="generateWorkflowByAI()"]');
    
    const prompt = promptInput.value;
    
    if (!prompt.trim()) {
        alert('请输入工作流需求描述');
        return;
    }
    
    // 显示加载状态
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 生成中...';
    
    // 发送请求
    fetch('/api/workflows/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: prompt })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 将生成的工作流步骤填充到文本域
            workflowSteps.value = JSON.stringify(data.workflow.steps, null, 2);
            
            // 如果工作流名称为空，自动填充
            const workflowName = document.getElementById('workflow-name');
            if (!workflowName.value.trim()) {
                workflowName.value = data.workflow.name || 'AI生成工作流';
            }
            
            // 如果工作流描述为空，自动填充
            const workflowDescription = document.getElementById('workflow-description');
            if (!workflowDescription.value.trim()) {
                workflowDescription.value = data.workflow.description || 'AI生成的工作流';
            }
            
            alert('工作流生成成功！');
        } else {
            alert('生成工作流失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('生成工作流失败: ' + error.message);
    })
    .finally(() => {
        // 恢复按钮状态
        generateBtn.disabled = false;
        generateBtn.innerHTML = '生成工作流';
    });
}

// 将工作流转换为正式模块
function convertToModule() {
    if (!currentWorkflowId) {
        alert('请先选择或创建一个工作流');
        return;
    }
    
    const workflowName = document.getElementById('workflow-name').value;
    
    if (!workflowName.trim()) {
        alert('请先输入工作流名称');
        return;
    }
    
    if (!confirm('确定要将此工作流转换为正式模块吗？')) {
        return;
    }
    
    // 发送请求
    fetch(`/api/workflows/${currentWorkflowId}/convert_to_module`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('工作流已成功转换为正式模块！');
            // 刷新自定义模块列表
            loadCustomModules();
        } else {
            alert('转换模块失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('转换模块失败: ' + error.message);
    });
}

// 可视化工作流编辑器相关功能
let currentEditMode = 'code';
let workflowNodes = [];
let workflowConnections = [];
let selectedNode = null;
let draggingNode = null;
let isConnecting = false;
let connectStartNode = null;

// 切换编辑模式
function switchEditMode(mode) {
    const visualEditor = document.getElementById('visual-workflow-editor');
    const codeEditor = document.getElementById('code-workflow-editor');
    const visualEditBtn = document.getElementById('visual-edit-btn');
    const codeEditBtn = document.getElementById('code-edit-btn');
    
    if (mode === 'visual') {
        currentEditMode = 'visual';
        visualEditor.style.display = 'block';
        codeEditor.style.display = 'none';
        visualEditBtn.classList.remove('btn-secondary');
        visualEditBtn.classList.add('btn-primary');
        codeEditBtn.classList.remove('btn-primary');
        codeEditBtn.classList.add('btn-secondary');
        
        // 从JSON加载工作流到可视化编辑器
        loadWorkflowToVisual();
    } else {
        currentEditMode = 'code';
        visualEditor.style.display = 'none';
        codeEditor.style.display = 'block';
        visualEditBtn.classList.remove('btn-primary');
        visualEditBtn.classList.add('btn-secondary');
        codeEditBtn.classList.remove('btn-secondary');
        codeEditBtn.classList.add('btn-primary');
    }
}

// 从JSON加载工作流到可视化编辑器
function loadWorkflowToVisual() {
    const workflowSteps = document.getElementById('workflow-steps').value;
    
    try {
        const steps = JSON.parse(workflowSteps);
        if (Array.isArray(steps)) {
            // 清空现有节点
            workflowNodes = [];
            workflowConnections = [];
            
            // 简单布局：垂直排列节点
            steps.forEach((step, index) => {
                const node = {
                    id: step.id,
                    type: step.action,
                    name: step.name,
                    x: 200,
                    y: 100 + index * 120,
                    params: step.params || {},
                    next_step: step.next_step
                };
                workflowNodes.push(node);
                
                // 添加连线
                if (step.next_step) {
                    workflowConnections.push({
                        id: `conn_${step.id}_${step.next_step}`,
                        from: step.id,
                        to: step.next_step
                    });
                }
            });
            
            // 绘制画布
            drawCanvas();
        }
    } catch (error) {
        console.error('加载工作流到可视化编辑器失败:', error);
    }
}

// 将可视化编辑器内容保存到JSON
function saveWorkflowFromVisual() {
    // 构建工作流步骤
    const steps = workflowNodes.map(node => {
        const step = {
            id: node.id,
            name: node.name,
            action: node.type,
            params: node.params || {}
        };
        
        // 添加next_step
        const connection = workflowConnections.find(conn => conn.from === node.id);
        if (connection) {
            step.next_step = connection.to;
        }
        
        return step;
    });
    
    // 更新JSON文本域
    const workflowSteps = document.getElementById('workflow-steps');
    workflowSteps.value = JSON.stringify(steps, null, 2);
    
    alert('可视化编辑已保存到代码编辑模式');
}

// 初始化可视化编辑器
function initVisualWorkflowEditor() {
    const canvas = document.getElementById('workflow-canvas');
    const ctx = canvas.getContext('2d');
    
    // 初始化拖拽事件
    const nodeItems = document.querySelectorAll('.node-item');
    nodeItems.forEach(item => {
        item.addEventListener('dragstart', handleDragStart);
    });
    
    canvas.addEventListener('dragover', handleDragOver);
    canvas.addEventListener('drop', handleDrop);
    canvas.addEventListener('click', handleCanvasClick);
    canvas.addEventListener('mousedown', handleCanvasMouseDown);
    canvas.addEventListener('mousemove', handleCanvasMouseMove);
    canvas.addEventListener('mouseup', handleCanvasMouseUp);
}

// 绘制画布
function drawCanvas() {
    const canvas = document.getElementById('workflow-canvas');
    const ctx = canvas.getContext('2d');
    
    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 绘制连线
    workflowConnections.forEach(connection => {
        drawConnection(connection, ctx);
    });
    
    // 绘制节点
    workflowNodes.forEach(node => {
        drawNode(node, ctx);
    });
}

// 绘制节点
function drawNode(node, ctx) {
    const isSelected = selectedNode && selectedNode.id === node.id;
    const nodeWidth = 200;
    const nodeHeight = 80;
    
    // 绘制节点背景
    ctx.fillStyle = isSelected ? '#e3f2fd' : 'white';
    ctx.strokeStyle = isSelected ? '#ffc107' : '#007bff';
    ctx.lineWidth = isSelected ? 3 : 2;
    ctx.fillRect(node.x, node.y, nodeWidth, nodeHeight);
    ctx.strokeRect(node.x, node.y, nodeWidth, nodeHeight);
    
    // 绘制节点标题
    ctx.fillStyle = '#333';
    ctx.font = '14px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(node.name, node.x + 15, node.y + 25);
    
    // 绘制节点类型
    ctx.fillStyle = '#666';
    ctx.font = '12px Arial';
    ctx.fillText(node.type, node.x + 15, node.y + 45);
    
    // 绘制端口
    const inPortX = node.x;
    const outPortX = node.x + nodeWidth;
    const portY = node.y + nodeHeight / 2;
    
    // 输入端口
    ctx.fillStyle = '#28a745';
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(inPortX, portY, 6, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
    
    // 输出端口
    ctx.fillStyle = '#dc3545';
    ctx.beginPath();
    ctx.arc(outPortX, portY, 6, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
}

// 绘制连线
function drawConnection(connection, ctx) {
    const fromNode = workflowNodes.find(node => node.id === connection.from);
    const toNode = workflowNodes.find(node => node.id === connection.to);
    
    if (fromNode && toNode) {
        const startX = fromNode.x + 200;
        const startY = fromNode.y + 40;
        const endX = toNode.x;
        const endY = toNode.y + 40;
        
        ctx.strokeStyle = '#6c757d';
        ctx.lineWidth = 2;
        ctx.setLineDash([]);
        
        // 绘制箭头
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
        
        // 绘制箭头头
        const arrowSize = 6;
        const angle = Math.atan2(endY - startY, endX - startX);
        ctx.beginPath();
        ctx.moveTo(endX, endY);
        ctx.lineTo(endX - arrowSize * Math.cos(angle - Math.PI / 6), endY - arrowSize * Math.sin(angle - Math.PI / 6));
        ctx.lineTo(endX - arrowSize * Math.cos(angle + Math.PI / 6), endY - arrowSize * Math.sin(angle + Math.PI / 6));
        ctx.closePath();
        ctx.fill();
    }
}

// 处理拖拽开始
function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.nodeType);
    e.target.style.opacity = '0.5';
}

// 处理拖拽经过
function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
}

// 处理放置
function handleDrop(e) {
    e.preventDefault();
    const canvas = document.getElementById('workflow-canvas');
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const nodeType = e.dataTransfer.getData('text/plain');
    
    // 创建新节点
    const newNode = {
        id: `node_${Date.now()}`,
        type: nodeType,
        name: getNodeTypeName(nodeType),
        x: x - 100,
        y: y - 40,
        params: {},
        next_step: null
    };
    
    workflowNodes.push(newNode);
    drawCanvas();
    
    // 恢复节点透明度
    const nodeItems = document.querySelectorAll('.node-item');
    nodeItems.forEach(item => {
        item.style.opacity = '1';
    });
}

// 获取节点类型名称
function getNodeTypeName(type) {
    const typeMap = {
        collect_data: '数据收集',
        process_data: '数据处理',
        ai_analysis: 'AI分析',
        generate_report: '生成报告',
        distribute_report: '报告分发'
    };
    return typeMap[type] || type;
}

// 处理画布点击
function handleCanvasClick(e) {
    const canvas = document.getElementById('workflow-canvas');
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // 检查是否点击了节点
    let clickedNode = null;
    workflowNodes.forEach(node => {
        if (x >= node.x && x <= node.x + 200 && y >= node.y && y <= node.y + 80) {
            clickedNode = node;
        }
    });
    
    if (clickedNode) {
        selectNode(clickedNode);
    } else {
        deselectNode();
    }
    
    drawCanvas();
}

// 选择节点
function selectNode(node) {
    selectedNode = node;
    updateNodeProperties();
}

// 取消选择节点
function deselectNode() {
    selectedNode = null;
    updateNodeProperties();
}

// 更新节点属性面板
function updateNodeProperties() {
    const propertiesContent = document.getElementById('node-properties-content');
    
    if (selectedNode) {
        propertiesContent.innerHTML = `
            <div class="mb-2">
                <label class="form-label">节点名称</label>
                <input type="text" class="form-control form-control-sm" value="${selectedNode.name}" onchange="updateNodeProperty('name', this.value)">
            </div>
            <div class="mb-2">
                <label class="form-label">节点类型</label>
                <input type="text" class="form-control form-control-sm" value="${selectedNode.type}" disabled>
            </div>
            <div class="mb-2">
                <label class="form-label">X坐标</label>
                <input type="number" class="form-control form-control-sm" value="${selectedNode.x}" onchange="updateNodeProperty('x', parseInt(this.value))">
            </div>
            <div class="mb-2">
                <label class="form-label">Y坐标</label>
                <input type="number" class="form-control form-control-sm" value="${selectedNode.y}" onchange="updateNodeProperty('y', parseInt(this.value))">
            </div>
            <div class="mt-3">
                <button class="btn btn-sm btn-danger" onclick="deleteSelectedNode()">删除节点</button>
            </div>
        `;
    } else {
        propertiesContent.innerHTML = '<p>选择节点查看和编辑属性</p>';
    }
}

// 更新节点属性
function updateNodeProperty(property, value) {
    if (selectedNode) {
        selectedNode[property] = value;
        drawCanvas();
    }
}

// 删除选中节点
function deleteSelectedNode() {
    if (selectedNode) {
        // 删除相关连线
        workflowConnections = workflowConnections.filter(conn => 
            conn.from !== selectedNode.id && conn.to !== selectedNode.id
        );
        
        // 删除节点
        workflowNodes = workflowNodes.filter(node => node.id !== selectedNode.id);
        
        deselectNode();
        drawCanvas();
    }
}

// 处理画布鼠标按下
function handleCanvasMouseDown(e) {
    const canvas = document.getElementById('workflow-canvas');
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // 检查是否点击了节点
    for (let i = workflowNodes.length - 1; i >= 0; i--) {
        const node = workflowNodes[i];
        if (x >= node.x && x <= node.x + 200 && y >= node.y && y <= node.y + 80) {
            draggingNode = node;
            break;
        }
    }
}

// 处理画布鼠标移动
function handleCanvasMouseMove(e) {
    const canvas = document.getElementById('workflow-canvas');
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    if (draggingNode) {
        // 更新节点位置
        draggingNode.x = x - 100;
        draggingNode.y = y - 40;
        drawCanvas();
    }
}

// 处理画布鼠标抬起
function handleCanvasMouseUp(e) {
    draggingNode = null;
}

// 清空画布
function clearCanvas() {
    if (confirm('确定要清空画布吗？')) {
        workflowNodes = [];
        workflowConnections = [];
        deselectNode();
        drawCanvas();
    }
}

// 页面加载完成后初始化可视化编辑器
document.addEventListener('DOMContentLoaded', function() {
    initVisualWorkflowEditor();
});

// 添加到现有的DOMContentLoaded事件
if (window.addEventListener) {
    window.addEventListener('load', initVisualWorkflowEditor, false);
} else if (window.attachEvent) {
    window.attachEvent('onload', initVisualWorkflowEditor);
}

// 删除工作流
function deleteWorkflow() {
    if (!currentWorkflowId) {
        alert('请先选择一个工作流');
        return;
    }
    
    if (!confirm('确定要删除这个工作流吗？')) {
        return;
    }
    
    fetch(`/api/workflows/${currentWorkflowId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('工作流删除成功');
            createNewWorkflow();
            loadWorkflows();
        } else {
            alert('删除工作流失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('删除工作流失败: ' + error.message);
    });
}

// 自定义模块管理

// 加载自定义模块
function loadCustomModules() {
    fetch('/api/modules')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            renderCustomModules(data.modules);
        } else {
            console.error('加载自定义模块失败:', data.message);
        }
    })
    .catch(error => {
        console.error('加载自定义模块失败:', error);
    });
}

// 渲染自定义模块
function renderCustomModules(modules) {
    const customModulesDropdown = document.getElementById('custom-modules-dropdown');
    customModulesDropdown.innerHTML = '';
    
    if (modules.length === 0) {
        const noModulesItem = document.createElement('li');
        noModulesItem.innerHTML = '<a class="dropdown-item text-muted" href="#" disabled>暂无自定义模块</a>';
        customModulesDropdown.appendChild(noModulesItem);
        return;
    }
    
    modules.forEach(module => {
        const moduleItem = document.createElement('li');
        moduleItem.innerHTML = `<a class="dropdown-item" href="#" onclick="showCustomModule('${module.id}')">${module.name}</a>`;
        customModulesDropdown.appendChild(moduleItem);
    });
}

// 显示自定义模块
function showCustomModule(moduleId) {
    alert(`显示自定义模块: ${moduleId}`);
}

// 生成文档
function generateReport() {
    const promptInput = document.getElementById('prompt-input');
    const reportOutput = document.getElementById('report-output');
    const generateBtn = document.getElementById('generate-btn');
    
    const prompt = promptInput.value;
    
    if (!prompt.trim()) {
        alert('请输入提示词');
        return;
    }
    
    // 添加或显示进度条
    let progressContainer = document.getElementById('progress-container');
    if (!progressContainer) {
        progressContainer = document.createElement('div');
        progressContainer.id = 'progress-container';
        progressContainer.innerHTML = `
            <div class="progress mb-3">
                <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                    0%
                </div>
            </div>
            <div class="text-center mb-3" id="progress-message">准备开始生成...</div>
        `;
        const saveBtn = document.getElementById('save-btn');
        saveBtn.parentNode.insertBefore(progressContainer, saveBtn.nextSibling);
    }
    
    // 显示加载状态
    generateBtn.disabled = true;
    generateBtn.textContent = '生成中...';
    reportOutput.value = '正在生成文档，请稍候...';
    
    // 发送请求
    fetch('/api/generate', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: prompt, template_id: currentTemplateId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 获取progress_id并监听进度
            const progressId = data.progress_id;
            startSingleReportProgressTracking(progressId, reportOutput, generateBtn, progressContainer);
        } else {
            reportOutput.value = data.message;
            document.getElementById('download-link').style.display = 'none';
            generateBtn.disabled = false;
            generateBtn.textContent = '生成';
            // 隐藏进度条
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
        }
    })
    .catch(error => {
        reportOutput.value = `生成失败: ${error.message}`;
        document.getElementById('download-link').style.display = 'none';
        generateBtn.disabled = false;
        generateBtn.textContent = '生成';
        // 隐藏进度条
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
    });
}

// 快速生成提示词
function generateQuickPrompt() {
    // 获取表单数据
    const docType = document.getElementById('quick-doc-type').value;
    const coreContent = document.getElementById('quick-core-content').value;
    const keywords = document.getElementById('quick-keywords').value;
    const details = document.getElementById('quick-details').value;
    
    // 验证核心内容
    if (!coreContent.trim()) {
        alert('请输入核心内容');
        return;
    }
    
    // 构建提示词
    let prompt = `请生成一份${docType}，`;
    prompt += `核心内容包括${coreContent}。`;
    
    if (keywords.trim()) {
        prompt += ` 关键词：${keywords}。`;
    }
    
    if (details.trim()) {
        prompt += ` 详细要求：${details}。`;
    }
    
    prompt += ` 请确保内容详细、专业，符合${docType}的格式要求。`;
    
    // 将生成的提示词填入提示词输入框
    document.getElementById('prompt-input').value = prompt;
    
    alert('提示词生成成功！');
}

// 清空快速提示词表单
function clearQuickPromptForm() {
    document.getElementById('quick-doc-type').value = '周报';
    document.getElementById('quick-core-content').value = '';
    document.getElementById('quick-keywords').value = '';
    document.getElementById('quick-details').value = '';
}

// 提示词验证
function validatePrompt(prompt) {
    if (!prompt || !prompt.trim()) {
        return { valid: false, message: '提示词不能为空' };
    }
    
    if (prompt.length < 10) {
        return { valid: false, message: '提示词长度不能少于10个字符' };
    }
    
    return { valid: true, message: '提示词有效' };
}

// 开始单文档生成进度跟踪
function startSingleReportProgressTracking(progressId, reportOutput, generateBtn, progressContainer) {
    // 创建SSE连接
    const eventSource = new EventSource(`/api/generate/progress/${progressId}`);
    
    // 显示进度条
    progressContainer.style.display = 'block';
    
    // 监听消息事件
    eventSource.onmessage = function(event) {
        try {
            const progress = JSON.parse(event.data);
            const percentage = progress.percentage;
            const message = progress.message;
            
            // 更新进度条
            const progressBar = progressContainer.querySelector('.progress-bar');
            const progressMessage = progressContainer.querySelector('#progress-message');
            
            if (progressBar && progressMessage) {
                progressBar.style.width = `${percentage}%`;
                progressBar.setAttribute('aria-valuenow', percentage);
                progressBar.textContent = `${percentage}%`;
                progressMessage.textContent = message;
            }
            
            // 检查是否完成
            if (percentage >= 100) {
                eventSource.close();
                generateBtn.disabled = false;
                generateBtn.textContent = '生成';
                progressMessage.textContent = '生成完成！';
                // 隐藏进度条（可选）
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                }, 2000);
            }
        } catch (error) {
            console.error('处理进度更新失败:', error);
        }
    };
    
    // 监听错误事件
    eventSource.onerror = function(error) {
        console.error('SSE连接错误:', error);
        eventSource.close();
        generateBtn.disabled = false;
        generateBtn.textContent = '生成';
        // 隐藏进度条
        progressContainer.style.display = 'none';
    };
}

// 保存文档
function saveReport() {
    const reportOutput = document.getElementById('report-output');
    const filenameInput = document.getElementById('filename-input');
    const fileFormatSelect = document.getElementById('file-format');
    const saveBtn = document.getElementById('save-btn');
    
    const content = reportOutput.value;
    const filename = filenameInput.value;
    const fileFormat = fileFormatSelect.value || 'txt';
    
    if (!content.trim()) {
        alert('请先生成文档内容');
        return;
    }
    
    // 显示加载状态
    saveBtn.disabled = true;
    saveBtn.textContent = '保存中...';
    
    // 发送请求
    fetch('/api/save', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            content: content, 
            filename: filename,
            file_format: fileFormat
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`文档已保存: ${data.filename}`);
            currentFilename = data.filename;
            // 更新下载链接
            document.getElementById('download-link').href = `/api/download/${data.filename}`;
            document.getElementById('download-link').style.display = 'inline-block';
            // 刷新历史列表
            loadReportsList();
        } else {
            alert(`保存失败: ${data.message}`);
        }
    })
    .catch(error => {
        alert(`保存失败: ${error.message}`);
    })
    .finally(() => {
        // 恢复按钮状态
        saveBtn.disabled = false;
        saveBtn.textContent = '保存';
    });
}

// 批量生成文档
function batchGenerateReports() {
    const batchPrompts = document.getElementById('batch-prompts');
    const batchResultsBody = document.getElementById('batch-results-body');
    const batchGenerateBtn = document.getElementById('batch-generate-btn');
    const batchFileFormat = document.getElementById('batch-file-format');
    
    const prompts = batchPrompts.value;
    const fileFormat = batchFileFormat.value || 'txt';
    
    if (!prompts.trim()) {
        alert('请输入提示词');
        return;
    }
    
    // 显示加载状态
    batchGenerateBtn.disabled = true;
    batchGenerateBtn.textContent = '生成中...';
    batchResultsBody.innerHTML = '<tr><td colspan="4" class="text-center">正在生成，请稍候...</td></tr>';
    
    // 发送请求
    fetch('/api/batch_generate', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompts: prompts, template_id: currentTemplateId, file_format: fileFormat })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 获取progress_id并监听进度
            const progressId = data.progress_id;
            startProgressTracking(progressId, batchResultsBody, batchGenerateBtn, prompts);
        } else {
            batchResultsBody.innerHTML = `<tr><td colspan="4" class="text-center text-danger">${data.message}</td></tr>`;
            batchGenerateBtn.disabled = false;
            batchGenerateBtn.textContent = '批量生成';
        }
    })
    .catch(error => {
        batchResultsBody.innerHTML = `<tr><td colspan="4" class="text-center text-danger">批量生成失败: ${error.message}</td></tr>`;
        batchGenerateBtn.disabled = false;
        batchGenerateBtn.textContent = '批量生成';
    });
}

// 开始进度跟踪
function startProgressTracking(progressId, resultsBody, generateBtn, originalPrompts, type = 'generate') {
    // 创建SSE连接
    const eventSource = new EventSource(`/api/generate/progress/${progressId}`);
    
    let progressBar, progressMessage;
    
    if (type === 'generate') {
        // 解析原始提示词列表
        const promptsList = originalPrompts.split('\n').filter(p => p.trim());
        
        // 初始化结果表格
        resultsBody.innerHTML = '';
        promptsList.forEach((prompt, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${prompt}</td>
                <td><span class="badge bg-secondary">等待中</span></td>
                <td></td>
            `;
            row.id = `batch-row-${index + 1}`;
            resultsBody.appendChild(row);
        });
        
        // 添加进度条行
        const progressRow = document.createElement('tr');
        progressRow.id = 'progress-row';
        progressRow.innerHTML = `
            <td colspan="4">
                <div class="progress">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                        0%
                    </div>
                </div>
                <div class="mt-1 text-center" id="progress-message">准备开始生成...</div>
            </td>
        `;
        resultsBody.appendChild(progressRow);
        
        progressBar = document.querySelector('.progress-bar');
        progressMessage = document.getElementById('progress-message');
    } else if (type === 'delete') {
        // 删除操作的进度条
        progressBar = document.querySelector('#delete-progress-container .progress-bar');
        progressMessage = document.getElementById('delete-progress-message');
    }
    
    // 监听消息事件
    eventSource.onmessage = function(event) {
        try {
            const progress = JSON.parse(event.data);
            const percentage = progress.percentage;
            const message = progress.message;
            const current = progress.current;
            const total = progress.total;
            
            // 更新进度条
            if (progressBar && progressMessage) {
                progressBar.style.width = `${percentage}%`;
                progressBar.setAttribute('aria-valuenow', percentage);
                progressBar.textContent = `${percentage}%`;
                progressMessage.textContent = message;
            }
            
            if (type === 'generate') {
                // 更新当前任务的状态
                if (current > 0) {
                    // 更新当前任务为"生成中"
                    const currentRow = document.getElementById(`batch-row-${current}`);
                    if (currentRow) {
                        const statusCell = currentRow.cells[2];
                        if (statusCell) {
                            statusCell.innerHTML = '<span class="badge bg-primary">生成中</span>';
                        }
                    }
                    
                    // 更新之前任务为"已完成"
                    if (current > 1) {
                        const prevRow = document.getElementById(`batch-row-${current - 1}`);
                        if (prevRow) {
                            const statusCell = prevRow.cells[2];
                            if (statusCell) {
                                statusCell.innerHTML = '<span class="badge bg-success">已完成</span>';
                            }
                        }
                    }
                }
            }
            
            // 检查是否完成
            if (percentage >= 100) {
                if (type === 'generate') {
                    // 解析原始提示词列表
                    const promptsList = originalPrompts.split('\n').filter(p => p.trim());
                    
                    // 更新所有任务为"已完成"
                    promptsList.forEach((prompt, index) => {
                        const row = document.getElementById(`batch-row-${index + 1}`);
                        if (row) {
                            const statusCell = row.cells[2];
                            if (statusCell) {
                                statusCell.innerHTML = '<span class="badge bg-success">已完成</span>';
                            }
                        }
                    });
                    
                    eventSource.close();
                    generateBtn.disabled = false;
                    generateBtn.textContent = '批量生成';
                    progressMessage.textContent = '生成完成！';
                    
                    // 刷新文档管理列表
                    loadReportsList();
                } else if (type === 'delete') {
                    eventSource.close();
                    progressMessage.textContent = '删除完成！';
                    
                    // 刷新文档管理列表
                    loadReportsList();
                    
                    // 清空选择
                    document.getElementById('select-all-checkbox').checked = false;
                    updateBatchDeleteButton();
                    
                    // 2秒后移除进度条
                    setTimeout(() => {
                        document.getElementById('delete-progress-container').remove();
                    }, 2000);
                }
            }
        } catch (error) {
            console.error('处理进度更新失败:', error);
        }
    };
    
    // 监听错误事件
    eventSource.onerror = function(error) {
        console.error('SSE连接错误:', error);
        eventSource.close();
        
        if (type === 'generate') {
            generateBtn.disabled = false;
            generateBtn.textContent = '批量生成';
            
            if (progressMessage) {
                progressMessage.textContent = '生成过程中发生错误';
            }
        } else if (type === 'delete') {
            if (progressMessage) {
                progressMessage.textContent = '删除过程中发生错误';
            }
        }
    };
}

// 批量保存文档
function batchSaveReports() {
    alert('批量保存功能正在开发中');
}

// 全局变量
let currentDocument = null;

// 加载历史文档列表到表格
function loadReportsList() {
    const documentsTableBody = document.getElementById('documents-table-body');
    const refreshBtn = document.getElementById('refresh-btn');
    
    // 显示加载状态
    refreshBtn.disabled = true;
    refreshBtn.textContent = '刷新中...';
    documentsTableBody.innerHTML = '<tr><td colspan="6" class="text-center">正在加载文档列表，请稍候...</td></tr>';
    
    // 添加或显示进度条
    let progressContainer = document.getElementById('refresh-progress-container');
    if (!progressContainer) {
        progressContainer = document.createElement('div');
        progressContainer.id = 'refresh-progress-container';
        progressContainer.className = 'mt-2 mb-2';
        progressContainer.innerHTML = `
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                    0%
                </div>
            </div>
            <div class="mt-1 text-center" id="refresh-progress-message">正在准备刷新...</div>
        `;
        const tableContainer = document.getElementById('documents-table-container');
        tableContainer.parentNode.insertBefore(progressContainer, tableContainer);
    } else {
        progressContainer.style.display = 'block';
    }
    
    // 更新进度函数
    const updateProgress = (percentage, message) => {
        const progressBar = progressContainer.querySelector('.progress-bar');
        const progressMessage = progressContainer.querySelector('#refresh-progress-message');
        
        if (progressBar && progressMessage) {
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
            progressBar.textContent = `${percentage}%`;
            progressMessage.textContent = message;
        }
    };
    
    // 模拟进度更新
    let currentProgress = 0;
    const progressInterval = setInterval(() => {
        currentProgress += 10;
        if (currentProgress < 90) {
            updateProgress(currentProgress, `正在刷新文档列表... ${currentProgress}%`);
        }
    }, 200);
    
    // 先加载批次列表，再加载文档列表
    Promise.all([
        fetch('/api/batches').then(res => res.json()),
        fetch('/api/load_reports').then(res => res.json())
    ])
    .then(([batchesRes, reportsRes]) => {
        clearInterval(progressInterval);
        updateProgress(100, '刷新完成！');
        
        const batches = batchesRes.success ? batchesRes.batches : [];
        
        if (reportsRes.success) {
            // 按批次分组文档
            const docsByBatch = {};
            
            // 初始化批次分组
            batches.forEach(batch => {
                docsByBatch[batch.id] = {
                    batch: batch,
                    documents: []
                };
            });
            
            // 未分配批次
            docsByBatch['unassigned'] = {
                batch: { id: 'unassigned', name: '未分配', total: 0 },
                documents: []
            };
            
            // 将文档分配到对应批次
            reportsRes.reports.forEach(report => {
                let assignedToBatch = false;
                for (const batch of batches) {
                    if (batch.files.includes(report.filename)) {
                        docsByBatch[batch.id].documents.push(report);
                        assignedToBatch = true;
                        break;
                    }
                }
                if (!assignedToBatch) {
                    docsByBatch['unassigned'].documents.push(report);
                }
            });
            
            // 更新每个批次的文档数量
            for (const batchId in docsByBatch) {
                docsByBatch[batchId].batch.total = docsByBatch[batchId].documents.length;
            }
            
            // 更新表格
            documentsTableBody.innerHTML = '';
            
            // 遍历所有批次，显示文档
            for (const batchId in docsByBatch) {
                const batchData = docsByBatch[batchId];
                const batch = batchData.batch;
                
                // 跳过没有文档的批次（除了未分配批次）
                if (batch.id !== 'unassigned' && batchData.documents.length === 0) {
                    continue;
                }
                
                batchData.documents.forEach(report => {
                    const fileExt = report.filename.split('.').pop().toLowerCase();
                    
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><input type="checkbox" class="document-checkbox" data-filename="${report.filename}"></td>
                        <td>${report.filename}</td>
                        <td>${fileExt.toUpperCase()}</td>
                        <td>${report.date}</td>
                        <td data-batch-id="${batch.id}">${batch.name}</td>
                        <td>
                            <button type="button" class="btn btn-primary btn-xs" onclick="loadDocument('${report.filename}')">加载</button>
                            <button type="button" class="btn btn-danger btn-xs" onclick="deleteDocument('${report.filename}')">删除</button>
                            <button type="button" class="btn btn-secondary btn-xs" onclick="downloadDocument('${report.filename}')">下载</button>
                        </td>
                    `;
                    documentsTableBody.appendChild(row);
                });
            }
            
            // 应用当前批次筛选
            filterByBatch();
        } else {
            documentsTableBody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">加载失败: ${reportsRes.message}</td></tr>`;
        }
        
        // 2秒后隐藏进度条
        setTimeout(() => {
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
        }, 2000);
    })
    .catch(error => {
        clearInterval(progressInterval);
        updateProgress(0, `刷新失败: ${error.message}`);
        documentsTableBody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">加载失败: ${error.message}</td></tr>`;
        
        // 2秒后隐藏进度条
        setTimeout(() => {
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
        }, 2000);
    })
    .finally(() => {
        // 恢复按钮状态
        refreshBtn.disabled = false;
        refreshBtn.textContent = '刷新';
        // 更新批量按钮状态
        updateBatchButtons();
    });
}

// 加载文档内容
function loadDocument(filename) {
    const documentContent = document.getElementById('document-content');
    
    if (!filename) {
        alert('请选择要加载的文档');
        return;
    }
    
    // 显示加载状态
    documentContent.value = '正在加载文档，请稍候...';
    
    // 发送请求
    fetch(`/api/load_report/${encodeURIComponent(filename)}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            documentContent.value = data.content;
            currentDocument = filename;
            // 更新下载按钮
            document.getElementById('download-content-btn').style.display = 'inline-block';
        } else {
            documentContent.value = `加载失败: ${data.message}`;
            currentDocument = null;
            document.getElementById('download-content-btn').style.display = 'none';
        }
    })
    .catch(error => {
        documentContent.value = `加载失败: ${error.message}`;
        currentDocument = null;
        document.getElementById('download-content-btn').style.display = 'none';
    });
}

// 删除单个文档
function deleteDocument(filename) {
    if (!filename) {
        alert('请选择要删除的文档');
        return;
    }
    
    if (!confirm(`确定要删除文档: ${filename}吗？`)) {
        return;
    }
    
    // 发送请求
    fetch(`/api/delete_report/${encodeURIComponent(filename)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('文档已删除');
            // 刷新列表
            loadReportsList();
            // 如果当前正在查看的文档被删除，清空内容
            if (currentDocument === filename) {
                document.getElementById('document-content').value = '';
                currentDocument = null;
                document.getElementById('download-content-btn').style.display = 'none';
            }
        } else {
            alert(`删除失败: ${data.message}`);
        }
    })
    .catch(error => {
        alert(`删除失败: ${error.message}`);
    });
}

// 批量删除文档
function batchDeleteDocuments() {
    const checkboxes = document.querySelectorAll('.document-checkbox:checked');
    const filenames = Array.from(checkboxes).map(cb => cb.dataset.filename);
    
    if (filenames.length === 0) {
        alert('请选择要删除的文档');
        return;
    }
    
    if (!confirm(`确定要删除选中的 ${filenames.length} 个文档吗？`)) {
        return;
    }
    
    // 显示进度条
    const progressContainer = document.createElement('div');
    progressContainer.id = 'delete-progress-container';
    progressContainer.className = 'mt-3';
    progressContainer.innerHTML = `
        <div class="progress">
            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                0%
            </div>
        </div>
        <div class="mt-1 text-center" id="delete-progress-message">准备开始删除...</div>
    `;
    
    const documentsTable = document.getElementById('documents-table');
    documentsTable.parentNode.insertBefore(progressContainer, documentsTable.nextSibling);
    
    // 发送请求
    fetch('/api/batch_delete_reports', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filenames: filenames })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 获取progress_id并监听进度
            const progressId = data.progress_id;
            startProgressTracking(progressId, null, null, null, 'delete');
        } else {
            alert(`批量删除失败: ${data.message}`);
            // 移除进度条
            progressContainer.remove();
        }
    })
    .catch(error => {
        alert(`批量删除失败: ${error.message}`);
        // 移除进度条
        progressContainer.remove();
    });
}

// 下载文档
function downloadDocument(filename) {
    if (!filename) {
        alert('请选择要下载的文档');
        return;
    }
    
    // 打开下载链接
    window.location.href = `/api/download/${encodeURIComponent(filename)}`;
}

// 保存文档内容
function saveDocumentContent() {
    const documentContent = document.getElementById('document-content');
    
    if (!currentDocument) {
        alert('请先加载一个文档');
        return;
    }
    
    const content = documentContent.value;
    
    // 发送请求
    fetch('/api/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            content: content,
            filename: currentDocument,
            file_format: currentDocument.split('.').pop().toLowerCase()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('文档内容已保存');
            // 刷新列表
            loadReportsList();
        } else {
            alert(`保存失败: ${data.message}`);
        }
    })
    .catch(error => {
        alert(`保存失败: ${error.message}`);
    });
}

// 更新批量删除按钮状态
function updateBatchDeleteButton() {
    const checkboxes = document.querySelectorAll('.document-checkbox:checked');
    const batchDeleteBtn = document.getElementById('batch-delete-btn');
    
    if (checkboxes.length > 0) {
        batchDeleteBtn.disabled = false;
        batchDeleteBtn.textContent = `批量删除 (${checkboxes.length})`;
    } else {
        batchDeleteBtn.disabled = true;
        batchDeleteBtn.textContent = '批量删除';
    }
}

// 全选/取消全选
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    const checkboxes = document.querySelectorAll('.document-checkbox');
    
    checkboxes.forEach(cb => {
        cb.checked = selectAllCheckbox.checked;
    });
    
    // 更新批量删除按钮状态
    updateBatchDeleteButton();
}

// 搜索文档
function searchDocuments() {
    const searchInput = document.getElementById('document-search');
    const searchTerm = searchInput.value.toLowerCase();
    const rows = document.querySelectorAll('#documents-table-body tr');
    
    rows.forEach(row => {
        const filename = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        if (filename.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// 初始化文档管理功能
function initDocumentManagement() {
    // 绑定事件监听器
    document.getElementById('refresh-btn').addEventListener('click', loadReportsList);
    document.getElementById('batch-delete-btn').addEventListener('click', batchDeleteDocuments);
    document.getElementById('batch-download-btn').addEventListener('click', batchDownloadDocuments);
    document.getElementById('save-content-btn').addEventListener('click', saveDocumentContent);
    document.getElementById('download-content-btn').addEventListener('click', () => {
        if (currentDocument) {
            downloadDocument(currentDocument);
        }
    });
    document.getElementById('document-search').addEventListener('input', searchDocuments);
    document.getElementById('select-all-checkbox').addEventListener('change', toggleSelectAll);
    
    // 绑定Excel导入事件
    document.getElementById('import-excel-btn').addEventListener('click', () => {
        document.getElementById('excel-file-input').click();
    });
    
    document.getElementById('excel-file-input').addEventListener('change', handleExcelFileSelect);
    
    // 监听文档复选框变化
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('document-checkbox')) {
            updateBatchButtons();
        }
    });
    
    // 绑定批次选择事件
    const batchSelect = document.getElementById('batch-select');
    if (batchSelect) {
        batchSelect.addEventListener('change', filterByBatch);
    }
    
    // 初始化加载文档列表和批次列表
    loadReportsList();
    loadBatchesList();
}

// 加载批次列表
function loadBatchesList() {
    fetch('/api/batches')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const batches = data.batches;
            const batchSelect = document.getElementById('batch-select');
            if (batchSelect) {
                // 保存当前选中的值
                const currentValue = batchSelect.value;
                
                // 清空现有选项，保留默认选项
                batchSelect.innerHTML = '<option value="">所有批次</option>';
                
                // 添加批次选项
                batches.forEach(batch => {
                    const option = document.createElement('option');
                    option.value = batch.id;
                    option.textContent = `${batch.name} (${batch.total}个文件)`;
                    batchSelect.appendChild(option);
                });
                
                // 恢复当前选中的值
                batchSelect.value = currentValue;
            }
        }
    })
    .catch(error => {
        console.error('加载批次列表失败:', error);
    });
}

// 按批次筛选文档
function filterByBatch() {
    const batchSelect = document.getElementById('batch-select');
    const selectedBatchId = batchSelect.value;
    const rows = document.querySelectorAll('#documents-table-body tr');
    
    if (!selectedBatchId) {
        // 显示所有行
        rows.forEach(row => {
            row.style.display = '';
        });
    } else {
        // 只显示选中批次的行
        rows.forEach(row => {
            const batchCell = row.querySelector('td:nth-child(5)');
            if (batchCell && batchCell.dataset.batchId === selectedBatchId) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
}

// 更新批量操作按钮状态
function updateBatchButtons() {
    const checkboxes = document.querySelectorAll('.document-checkbox:checked');
    const filenames = Array.from(checkboxes).map(cb => cb.dataset.filename);
    
    const batchDeleteBtn = document.getElementById('batch-delete-btn');
    const batchDownloadBtn = document.getElementById('batch-download-btn');
    
    if (filenames.length > 0) {
        batchDeleteBtn.disabled = false;
        batchDeleteBtn.textContent = `批量删除 (${filenames.length})`;
        batchDownloadBtn.disabled = false;
        batchDownloadBtn.textContent = `批量下载 (${filenames.length})`;
    } else {
        batchDeleteBtn.disabled = true;
        batchDeleteBtn.textContent = '批量删除';
        batchDownloadBtn.disabled = true;
        batchDownloadBtn.textContent = '批量下载';
    }
}

// 更新批量删除按钮状态（兼容旧函数）
function updateBatchDeleteButton() {
    updateBatchButtons();
}

// 批量下载文档
function batchDownloadDocuments() {
    const checkboxes = document.querySelectorAll('.document-checkbox:checked');
    const filenames = Array.from(checkboxes).map(cb => cb.dataset.filename);
    
    if (filenames.length === 0) {
        alert('请选择要下载的文档');
        return;
    }
    
    // 显示加载状态
    const batchDownloadBtn = document.getElementById('batch-download-btn');
    const originalText = batchDownloadBtn.textContent;
    batchDownloadBtn.disabled = true;
    batchDownloadBtn.textContent = '下载中...';
    
    // 发送请求
    fetch('/api/batch_download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filenames: filenames })
    })
    .then(response => {
        if (response.ok) {
            // 获取文件名
            const contentDisposition = response.headers.get('content-disposition');
            let filename = 'batch_download.zip';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?([^";]+)"?/);
                if (match && match[1]) {
                    filename = match[1];
                }
            }
            // 处理文件下载
            return response.blob().then(blob => ({ blob, filename }));
        }
        throw new Error('批量下载失败');
    })
    .then(({ blob, filename }) => {
        // 创建下载链接
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        alert(`批量下载失败: ${error.message}`);
        console.error('批量下载失败:', error);
    })
    .finally(() => {
        // 恢复按钮状态
        batchDownloadBtn.disabled = false;
        batchDownloadBtn.textContent = originalText;
    });
}

// 批次下载文档
function downloadBatchDocuments(batchId) {
    // 显示加载状态
    const batchDownloadBtn = document.getElementById('batch-download-btn');
    const originalText = batchDownloadBtn.textContent;
    batchDownloadBtn.disabled = true;
    batchDownloadBtn.textContent = '下载中...';
    
    // 发送请求
    fetch('/api/batch_download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ batch_id: batchId })
    })
    .then(response => {
        if (response.ok) {
            // 获取文件名
            const contentDisposition = response.headers.get('content-disposition');
            let filename = 'batch_download.zip';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?([^";]+)"?/);
                if (match && match[1]) {
                    filename = match[1];
                }
            }
            // 处理文件下载
            return response.blob().then(blob => ({ blob, filename }));
        }
        throw new Error('批次下载失败');
    })
    .then(({ blob, filename }) => {
        // 创建下载链接
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        alert(`批次下载失败: ${error.message}`);
        console.error('批次下载失败:', error);
    })
    .finally(() => {
        // 恢复按钮状态
        batchDownloadBtn.disabled = false;
        batchDownloadBtn.textContent = originalText;
    });
}

// 处理Excel文件选择
function handleExcelFileSelect(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }
    
    // 检查文件类型
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        alert('请选择Excel文件（.xlsx或.xls格式）');
        return;
    }
    
    // 提示用户确认
    if (!confirm(`确定要导入文件：${file.name}吗？`)) {
        return;
    }
    
    // 显示加载状态
    const importBtn = document.getElementById('import-excel-btn');
    importBtn.disabled = true;
    importBtn.textContent = '导入中...';
    
    // 创建进度条
    const progressContainer = document.createElement('div');
    progressContainer.id = 'excel-import-progress-container';
    progressContainer.className = 'mt-3';
    progressContainer.innerHTML = `
        <div class="progress">
            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                0%
            </div>
        </div>
        <div class="mt-1 text-center" id="excel-import-progress-message">准备开始导入...</div>
    `;
    
    const importSection = document.getElementById('excel-import-section');
    importSection.parentNode.insertBefore(progressContainer, importSection.nextSibling);
    
    // 创建FormData对象
    const formData = new FormData();
    formData.append('file', file);
    
    // 发送请求
    fetch('/api/import_excel', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 获取progress_id并监听进度
            const progressId = data.progress_id;
            startExcelImportProgressTracking(progressId, progressContainer, importBtn, event.target);
        } else {
            updateExcelProgress(0, `导入失败：${data.message}`);
            alert(`导入失败：${data.message}`);
            // 恢复按钮状态
            importBtn.disabled = false;
            importBtn.textContent = 'Excel导入';
            // 清空文件输入
            event.target.value = '';
            // 2秒后移除进度条
            setTimeout(() => {
                if (progressContainer.parentNode) {
                    progressContainer.parentNode.removeChild(progressContainer);
                }
            }, 2000);
        }
    })
    .catch(error => {
        updateExcelProgress(0, `导入失败：${error.message}`);
        alert(`导入失败：${error.message}`);
        // 恢复按钮状态
        importBtn.disabled = false;
        importBtn.textContent = 'Excel导入';
        // 清空文件输入
        event.target.value = '';
        // 2秒后移除进度条
        setTimeout(() => {
            if (progressContainer.parentNode) {
                progressContainer.parentNode.removeChild(progressContainer);
            }
        }, 2000);
    });
}

// 更新Excel导入进度
function updateExcelProgress(percentage, message) {
    const progressBar = document.querySelector('#excel-import-progress-container .progress-bar');
    const progressMessage = document.getElementById('excel-import-progress-message');
    
    if (progressBar && progressMessage) {
        progressBar.style.width = `${percentage}%`;
        progressBar.setAttribute('aria-valuenow', percentage);
        progressBar.textContent = `${Math.round(percentage)}%`;
        progressMessage.textContent = message;
    }
}

// 开始Excel导入进度跟踪
function startExcelImportProgressTracking(progressId, progressContainer, importBtn, fileInput) {
    // 创建SSE连接
    const eventSource = new EventSource(`/api/generate/progress/${progressId}`);
    
    // 监听消息事件
    eventSource.onmessage = function(event) {
        try {
            const progress = JSON.parse(event.data);
            const percentage = progress.percentage;
            const message = progress.message;
            
            // 更新进度条
            updateExcelProgress(percentage, message);
            
            // 检查是否完成
            if (percentage >= 100) {
                eventSource.close();
                alert('Excel导入完成！');
                // 刷新文档列表
                loadReportsList();
                
                // 恢复按钮状态
                importBtn.disabled = false;
                importBtn.textContent = 'Excel导入';
                // 清空文件输入
                fileInput.value = '';
                
                // 2秒后移除进度条
                setTimeout(() => {
                    if (progressContainer.parentNode) {
                        progressContainer.parentNode.removeChild(progressContainer);
                    }
                }, 2000);
            }
        } catch (error) {
            console.error('处理进度更新失败:', error);
        }
    };
    
    // 监听错误事件
    eventSource.onerror = function(error) {
        console.error('SSE连接错误:', error);
        eventSource.close();
        
        // 恢复按钮状态
        importBtn.disabled = false;
        importBtn.textContent = 'Excel导入';
        // 清空文件输入
        fileInput.value = '';
        
        // 2秒后移除进度条
        setTimeout(() => {
            if (progressContainer.parentNode) {
                progressContainer.parentNode.removeChild(progressContainer);
            }
        }, 2000);
        
        alert('Excel导入过程中发生错误');
    };
}

// 工作流模板管理

// 加载工作流模板
function loadWorkflowTemplates() {
    fetch('/api/workflow-templates')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            renderWorkflowTemplates(data.templates);
        } else {
            console.error('加载工作流模板失败:', data.message);
        }
    })
    .catch(error => {
        console.error('加载工作流模板失败:', error);
    });
}

// 渲染工作流模板
function renderWorkflowTemplates(templates) {
    const templatesDropdown = document.getElementById('workflow-templates-dropdown');
    if (templatesDropdown) {
        templatesDropdown.innerHTML = '';
        
        templates.forEach(template => {
            const templateItem = document.createElement('a');
            templateItem.className = 'dropdown-item';
            templateItem.href = '#';
            templateItem.onclick = function() { useWorkflowTemplate(template.id); };
            templateItem.textContent = template.name;
            templatesDropdown.appendChild(templateItem);
        });
    }
}

// 使用工作流模板
function useWorkflowTemplate(templateId) {
    fetch(`/api/workflow-templates/${templateId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const template = data.template;
            // 填充工作流表单
            document.getElementById('workflow-name').value = template.name;
            document.getElementById('workflow-description').value = template.description || '';
            document.getElementById('workflow-steps').value = JSON.stringify(template.steps || [], null, 2);
            
            // 更新标题
            document.getElementById('workflow-editor-title').textContent = `基于模板创建工作流: ${template.name}`;
            
            alert('已加载工作流模板，请根据需要修改后保存');
        } else {
            alert('加载工作流模板失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('加载工作流模板失败: ' + error.message);
    });
}

// 在页面加载完成后初始化工作流模板
if (document.getElementById('workflow')) {
    loadWorkflowTemplates();
}

// 处理提示词Excel文件导入
function handlePromptsExcelFileSelect(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }
    
    // 检查文件类型
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        alert('请选择Excel文件（.xlsx或.xls格式）');
        return;
    }
    
    // 创建FormData对象
    const formData = new FormData();
    formData.append('file', file);
    
    // 显示加载状态
    const importBtn = document.getElementById('import-prompts-excel');
    importBtn.disabled = true;
    importBtn.textContent = '导入中...';
    
    // 发送请求
    fetch('/api/import_prompts_excel', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 将导入的提示词添加到文本区域
            const batchPrompts = document.getElementById('batch-prompts');
            const existingPrompts = batchPrompts.value.trim();
            const newPrompts = data.prompts.join('\n');
            
            if (existingPrompts) {
                batchPrompts.value = existingPrompts + '\n' + newPrompts;
            } else {
                batchPrompts.value = newPrompts;
            }
            
            alert('提示词导入成功！共导入 ' + data.prompts.length + ' 个提示词。');
        } else {
            alert('提示词导入失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('提示词导入失败: ' + error.message);
    })
    .finally(() => {
        // 恢复按钮状态
        importBtn.disabled = false;
        importBtn.textContent = 'Excel导入提示词';
        // 清空文件输入
        event.target.value = '';
    });
}

// 清空提示词
function clearPrompts() {
    if (confirm('确定要清空所有提示词吗？')) {
        document.getElementById('batch-prompts').value = '';
    }
}

// 更新任务列表
function updateTasksList() {
    fetch('/api/tasks')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const tasks = data.tasks;
            const tasksListBody = document.getElementById('tasks-list-body');
            
            if (tasksListBody) {
                tasksListBody.innerHTML = '';
                
                if (tasks.length === 0) {
                    tasksListBody.innerHTML = '<tr><td colspan="5" class="text-center">暂无任务</td></tr>';
                    return;
                }
                
                tasks.forEach(task => {
                    const row = document.createElement('tr');
                    
                    // 格式化创建时间
                    const createdAt = new Date(task.created_at).toLocaleString('zh-CN');
                    
                    // 根据任务状态显示不同的徽章
                    let statusBadge;
                    switch (task.status) {
                        case 'running':
                            statusBadge = '<span class="badge bg-primary">运行中</span>';
                            break;
                        case 'paused':
                            statusBadge = '<span class="badge bg-warning">已暂停</span>';
                            break;
                        case 'completed':
                            statusBadge = '<span class="badge bg-success">已完成</span>';
                            break;
                        case 'failed':
                            statusBadge = '<span class="badge bg-danger">失败</span>';
                            break;
                        case 'cancelled':
                            statusBadge = '<span class="badge bg-secondary">已取消</span>';
                            break;
                        default:
                            statusBadge = '<span class="badge bg-info">未知</span>';
                    }
                    
                    // 计算进度百分比
                    const progressPercentage = Math.round((task.current / task.total) * 100);
                    
                    // 操作按钮组
                    let actionButtons = '';
                    if (task.status === 'running') {
                        actionButtons = `
                            <button class="btn btn-warning btn-xs" onclick="pauseTask('${task.task_id}')">暂停</button>
                            <button class="btn btn-danger btn-xs" onclick="cancelTask('${task.task_id}')">取消</button>
                        `;
                    } else if (task.status === 'paused') {
                        actionButtons = `
                            <button class="btn btn-success btn-xs" onclick="resumeTask('${task.task_id}')">恢复</button>
                            <button class="btn btn-danger btn-xs" onclick="cancelTask('${task.task_id}')">取消</button>
                        `;
                    }
                    
                    row.innerHTML = `
                        <td>${task.task_id}</td>
                        <td>${statusBadge}</td>
                        <td>${createdAt}</td>
                        <td>
                            <div class="progress" style="height: 20px;">
                                <div class="progress-bar" role="progressbar" style="width: ${progressPercentage}%" aria-valuenow="${progressPercentage}" aria-valuemin="0" aria-valuemax="100">
                                    ${progressPercentage}%
                                </div>
                            </div>
                        </td>
                        <td>${actionButtons}</td>
                    `;
                    
                    tasksListBody.appendChild(row);
                });
            }
        }
    })
    .catch(error => {
        console.error('更新任务列表失败:', error);
    });
}

// 暂停任务
function pauseTask(taskId) {
    fetch(`/api/tasks/${taskId}/pause`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 立即更新任务列表
            updateTasksList();
            alert('任务已暂停');
        } else {
            alert('暂停任务失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('暂停任务失败: ' + error.message);
    });
}

// 恢复任务
function resumeTask(taskId) {
    fetch(`/api/tasks/${taskId}/resume`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 立即更新任务列表
            updateTasksList();
            alert('任务已恢复');
        } else {
            alert('恢复任务失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('恢复任务失败: ' + error.message);
    });
}

// 取消任务
function cancelTask(taskId) {
    if (confirm('确定要取消这个任务吗？')) {
        fetch(`/api/tasks/${taskId}/cancel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 立即更新任务列表
                updateTasksList();
                alert('任务已取消');
            } else {
                alert('取消任务失败: ' + data.message);
            }
        })
        .catch(error => {
            alert('取消任务失败: ' + error.message);
        });
    }
}