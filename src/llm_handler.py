import openai
import re
import streamlit as st
import os

class LLMHandler:
    '''LLM Constructor, 初始化LLM同步客户端'''
    def __init__(self, api_key: str, base_url: str, model: str):
        # 这里只是简单的接入了API的同步客户端, 后期可改成异步客户端, 提高并发体验
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    '''读取visualization-skill'''
    def _get_system_prompt(self, df_schema: str = ""):
        skill_dir = os.path.join(os.path.dirname(__file__), "visualization-skill")
        skill_content = ""
        
        # 1. 加载SKILL.md
        skill_path = os.path.join(skill_dir, "SKILL.md")
        if os.path.exists(skill_path):
            with open(skill_path, "r", encoding="utf-8") as f:
                skill_content += f.read() + "\n"

        # 2. 注入数据集
        if df_schema:
            skill_content += f"\n## Dataset Context\n{df_schema}\n"
        
        return skill_content

    '''提取并分离代码块和可视化报告(正则匹配)'''
    def _extract_code_from_response(self, content: str):
        # 匹配Python代码块
        code_match = re.search(r"```python\n(.*?)```", content, re.DOTALL)
        code = code_match.group(1) if code_match else None
        
        # 提取代码块之外的所有文字
        interpretation = re.sub(r"```python.*?```", "", content, flags=re.DOTALL).strip()
            
        return code, interpretation
    
    def chat_for_visualization(self, user_query: str, data_info, sample_df, history: list = None):
        # 精简Schema以提高速度
        df_schema = (
            f"Columns: {list(data_info['dtypes'].index)}\n"
            f"Dtypes: {data_info['dtypes'].to_dict()}\n"
            f"Sample Preview:\n{sample_df.to_dict()}"
        )
        
        system_instructions = self._get_system_prompt(df_schema)
        
        messages = [{"role": "system", "content": system_instructions}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_query})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
            )
            full_content = response.choices[0].message.content
            code, interpretation = self._extract_code_from_response(full_content)
            
            return {
                "code": code, 
                "interpretation": interpretation, 
                "raw_response": full_content
            }
        except Exception as e:
            st.error(f"LLM 调用异常: {str(e)}")
            return None