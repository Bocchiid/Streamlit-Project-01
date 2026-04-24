import openai
import re
import streamlit as st
import os

class LLMHandler:
    '''LLM Constructor, 初始化LLM同步客户端'''
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def _get_system_prompt(self, df_schema: str = "") -> str:
        """
        从 skill_viz 目录下读取 Skill 定义并构建指令。
        """
        skill_dir = os.path.join(os.path.dirname(__file__), "skill_viz")
        skill_content = "# Skill Protocol: Visualization Iteration (Viz Skill)\n"
        
        # 1. 按照逻辑加载 .md 定义
        for file_name in ["description.md", "prompt.md"]:
            path = os.path.join(skill_dir, file_name)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    skill_content += f.read() + "\n"
        
        # 2. 注入硬性运行约束（防止警告并确保输出格式）
        skill_content += """
        ## 强制约束 (Mandatory Constraints)
        - 【格式要求】必须先输出 python 代码块，然后在代码块外部输出环节4的文字解读报告。
        - 【库限制】绝对禁止使用 matplotlib, seaborn, plt。仅允许使用 plotly。
        - 【安全】严禁调用 fig.show() 或 trendline 参数。
        """

        # 3. 注入数据集上下文
        if df_schema:
            skill_content += f"\n## Dataset Context\n{df_schema}\n"
        
        return skill_content

    def _extract_code_from_response(self, content: str) -> tuple:
        """从 LLM 响应中分离代码和解读报告"""
        # 匹配 Python 代码块
        code_match = re.search(r"```python\n(.*?)```", content, re.DOTALL)
        code = code_match.group(1) if code_match else None
        
        # 提取代码块之外的所有文字
        interpretation = re.sub(r"```python.*?```", "", content, flags=re.DOTALL).strip()
        
        # 兜底：如果模型没写报告，尝试从环节4的描述中找或给提示
        if not interpretation:
            interpretation = "模型未在代码块外生成解读报告。请检查 prompt.md 的输出格式要求。"
            
        return code, interpretation
    
    def chat_for_visualization(self, user_query: str, df, history: list = None) -> dict:
        """执行可视化生成请求"""
        # 精简 Schema 以提高速度
        df_schema = (
            f"Columns: {list(df.columns)}\n"
            f"Dtypes: {df.dtypes.to_dict()}\n"
            f"Sample:\n{df.head(2).to_dict()}"
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