from openai import OpenAI
import os

class APIClient:
    def __init__(self, api_key, api_source="deepseek"):
        self.api_key = api_key
        self.api_source = api_source
        self.config = {
            "deepseek": {
                "base_url": "https://api.deepseek.com",
                "model": "deepseek-chat"
            },
            "ollama": {
                "base_url": "http://localhost:11434",
                "model": "llama3"
            }
        }
        
        # 初始化OpenAI客户端
        self.set_api_source(api_source)
    
    def set_api_source(self, api_source):
        """切换API来源"""
        if api_source in self.config:
            self.api_source = api_source
            config = self.config[self.api_source]
            
            if api_source == "deepseek":
                # 使用DeepSeek API
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=config["base_url"]
                )
            else:
                # 使用本地Ollama
                self.client = OpenAI(
                    api_key="ollama",
                    base_url=config["base_url"]
                )
            
            self.model = config["model"]
            return True
        return False
    
    def generate_report(self, prompt):
        """调用API生成周报"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一名专业的周报撰写助手，请根据提供的提示词和模板，生成一份详细、专业的周报。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                stream=False
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"API调用失败: {str(e)}")
    
    def test_connection(self):
        """测试API连接是否正常"""
        try:
            # 发送一个简单的请求来测试连接
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "你好，测试连接是否正常"
                    }
                ],
                temperature=0,
                max_tokens=10,
                stream=False
            )
            # 确保我们收到了有效的回复
            if response and response.choices and response.choices[0].message and response.choices[0].message.content:
                return True, "连接正常"
            else:
                return False, "连接成功但未收到有效回复"
        except Exception as e:
            return False, f"连接失败: {str(e)}"
