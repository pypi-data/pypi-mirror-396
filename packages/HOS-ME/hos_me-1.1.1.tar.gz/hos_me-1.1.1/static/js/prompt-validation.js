// 提示词验证函数
function validatePrompt() {
    const promptInput = document.getElementById('prompt-input');
    const prompt = promptInput.value.trim();
    
    if (!prompt) {
        alert('提示词不能为空');
        promptInput.focus();
        return false;
    }
    
    if (prompt.length < 10) {
        alert('提示词长度不能少于10个字符');
        promptInput.focus();
        return false;
    }
    
    // 检查是否包含无效字符
    const invalidChars = /[<>"';&]/;
    if (invalidChars.test(prompt)) {
        alert('提示词包含无效字符，请移除<>"\';&等字符');
        promptInput.focus();
        return false;
    }
    
    return true;
}

// 快速创建提示词功能
function generateQuickPrompt() {
    const docType = document.getElementById('quick-doc-type').value;
    const coreContent = document.getElementById('quick-core-content').value.trim();
    const keywords = document.getElementById('quick-keywords').value.trim();
    const details = document.getElementById('quick-details').value.trim();
    
    if (!coreContent) {
        alert('请输入核心内容');
        return;
    }
    
    // 生成结构化提示词
    let prompt = `请生成一份${docType}，核心内容是：${coreContent}`;
    
    if (keywords) {
        prompt += `，关键词包括：${keywords}`;
    }
    
    if (details) {
        prompt += `，详细要求：${details}`;
    }
    
    prompt += '。请按照正式文档格式生成，内容要详细、专业。';
    
    // 将生成的提示词填入提示词输入框
    document.getElementById('prompt-input').value = prompt;
    
    // 显示成功提示
    alert('提示词生成成功！');
}

// 清空快速创建提示词表单
function clearQuickPromptForm() {
    document.getElementById('quick-doc-type').value = '周报';
    document.getElementById('quick-core-content').value = '';
    document.getElementById('quick-keywords').value = '';
    document.getElementById('quick-details').value = '';
}