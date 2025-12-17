// 图片上传功能
let uploadedImages = [];

// 初始化图片上传功能
document.addEventListener('DOMContentLoaded', function() {
    const imageUpload = document.getElementById('image-upload');
    if (imageUpload) {
        imageUpload.addEventListener('change', handleImageUpload);
    }
});

// 处理图片上传
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }
    
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
        alert('请选择图片文件');
        return;
    }
    
    // 显示文件名
    document.getElementById('image-filename').value = file.name;
    
    // 创建图片预览
    const reader = new FileReader();
    reader.onload = function(e) {
        // 创建图片对象
        const imageData = {
            id: Date.now(),
            filename: file.name,
            data: e.target.result,
            ocrResult: null,
            ocrEnabled: document.getElementById('enable-ocr').checked
        };
        
        // 添加到已上传图片列表
        uploadedImages.push(imageData);
        
        // 显示图片预览
        displayImagePreview(imageData);
        
        // 如果启用了OCR，自动处理图片
        if (imageData.ocrEnabled) {
            performOCR(imageData);
        }
    };
    reader.readAsDataURL(file);
    
    // 清空文件选择，允许重新选择同一文件
    event.target.value = '';
}

// 显示图片预览
function displayImagePreview(imageData) {
    const container = document.getElementById('uploaded-images');
    
    const imagePreview = document.createElement('div');
    imagePreview.className = 'image-preview';
    imagePreview.style.cssText = `
        position: relative;
        width: 120px;
        height: 120px;
        border: 1px solid #ddd;
        border-radius: 4px;
        overflow: hidden;
        margin: 5px;
    `;
    
    imagePreview.innerHTML = `
        <img src="${imageData.data}" alt="${imageData.filename}" style="width: 100%; height: 100%; object-fit: cover;">
        <div style="position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.7); color: white; padding: 4px;">
            <small>${imageData.filename}</small>
        </div>
        <button type="button" class="btn btn-danger btn-sm" onclick="removeImage(${imageData.id})" style="position: absolute; top: 5px; right: 5px; padding: 2px 6px; font-size: 12px;">
            <i class="bi bi-x"></i>
        </button>
    `;
    
    container.appendChild(imagePreview);
}

// 移除图片
function removeImage(imageId) {
    // 从数组中移除
    uploadedImages = uploadedImages.filter(img => img.id !== imageId);
    
    // 从DOM中移除
    const container = document.getElementById('uploaded-images');
    const previews = container.querySelectorAll('.image-preview');
    previews.forEach(preview => {
        const removeBtn = preview.querySelector('button');
        if (removeBtn && removeBtn.onclick.toString().includes(imageId)) {
            preview.remove();
        }
    });
    
    // 更新文件名显示
    if (uploadedImages.length === 0) {
        document.getElementById('image-filename').value = '';
    }
}

// 执行OCR识别
function performOCR(imageData) {
    // 这里应该调用OCR API进行识别
    // 目前只是模拟OCR功能
    setTimeout(() => {
        imageData.ocrResult = {
            text: `OCR识别结果：这是图片 ${imageData.filename} 的文字内容示例。`,
            confidence: 0.95
        };
        
        // 更新图片状态
        updateImageStatus(imageData);
    }, 1000);
}

// 更新图片状态
function updateImageStatus(imageData) {
    // 更新DOM中的图片状态
    const container = document.getElementById('uploaded-images');
    const previews = container.querySelectorAll('.image-preview');
    previews.forEach(preview => {
        const removeBtn = preview.querySelector('button');
        if (removeBtn && removeBtn.onclick.toString().includes(imageData.id)) {
            if (imageData.ocrResult) {
                // 添加OCR结果标记
                let ocrBadge = preview.querySelector('.ocr-badge');
                if (!ocrBadge) {
                    ocrBadge = document.createElement('span');
                    ocrBadge.className = 'ocr-badge';
                    ocrBadge.style.cssText = `
                        position: absolute;
                        top: 5px;
                        left: 5px;
                        background: rgba(0, 128, 0, 0.8);
                        color: white;
                        padding: 2px 6px;
                        border-radius: 10px;
                        font-size: 10px;
                    `;
                    preview.appendChild(ocrBadge);
                }
                ocrBadge.textContent = 'OCR完成';
            }
        }
    });
}

// 获取已上传的图片
function getUploadedImages() {
    return uploadedImages;
}

// 清空所有已上传图片
function clearUploadedImages() {
    uploadedImages = [];
    const container = document.getElementById('uploaded-images');
    container.innerHTML = '';
    document.getElementById('image-filename').value = '';
}

// 检查是否启用了OCR
function isOCREnabled() {
    return document.getElementById('enable-ocr').checked;
}