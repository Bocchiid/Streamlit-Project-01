import openai
import re
import streamlit as st
from config import DEEPSEEK_MODEL

class LLMHandler:
    """
    LLM 交互处理器：负责与大模型通信，封装 Prompt 并解析响应。
    """
    def __init__(self, api_key: str, base_url: str, model: str = DEEPSEEK_MODEL):
        # 初始化客户端，兼容 OpenAI 格式的 API（如通义千问、DeepSeek等） [cite: 20]
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def _get_system_prompt(self, df_schema: str) -> str:
        """
        构建系统角色，明确可视化生成 Skill 的 5 段式逻辑要求 。
        """
        return f"""你是一个专业的数据可视化智能体。你具备以下 Skill 核心逻辑：
        1. 数据理解：分析字段含义与分布。
        2. 图表选择：根据数据特征选择最合适的图表（柱状图、折线图、散点图、饼图、热力图等）。
        3. 样式优化：配色符合 ColorBrewer 原则，设置清晰标题、图例、标签，剔除冗余网格线。
        4. 可解释输出：生成图表后提供结论解读。
        5. 多轮迭代：根据用户后续反馈修正图表, 生成代码时，除非用户明确要求，否则请勿使用 trendline 参数，以保持代码简洁和依赖最小化, 目前仅有numpy、pandas、matplotlib、seaborn、plotly、streamlit、folium、scikit-learn、openai、dotenv。

        当前数据集字段信息：
        {df_schema}

        要求：
        - 首先输出 Python 代码，代码必须包含在 ```python ``` 块中。
        - 绘图使用 plotly.express (px) 或 plotly.graph_objects (go)。
        - 假设 DataFrame 变量名为 'df'，最终图表对象变量名必须为 'fig'。
        - 代码块之外的文字部分作为图表解读报告，提供对图表的分析结论和洞察。
        - 生成的代码必须可直接运行，且不包含任何未声明的变量或函数。
        - 代码中请勿使用任何 trendline 参数，以保持代码简洁和依赖最小化。
        - 【绝对禁止】调用 fig.show() 或任何尝试打开新窗口的命令，只需构建 fig 对象。
        """

    def chat_for_visualization(self, user_query: str, df, history: list = None):
        """
        执行可视化生成请求 [cite: 12]。
        """
        # 提取数据 Schema 信息供 LLM 理解 [cite: 7]
        df_schema = f"列名: {list(df.columns)}\n数据类型:\n{df.dtypes.to_string()}"
        
        system_prompt = self._get_system_prompt(df_schema)
        
        # 组装消息列表以支持多轮迭代 
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_query})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2 # 降低随机性，保证代码稳定性
            )
            
            full_content = response.choices[0].message.content
            
            # 使用正则解析出 Python 代码块
            code_match = re.search(r"```python\n(.*?)```", full_content, re.DOTALL)
            code = code_match.group(1) if code_match else None
            
            # 解析解释性文字（代码块之外的内容）作为解读报告 
            interpretation = re.sub(r"```python.*?```", "", full_content, flags=re.DOTALL).strip()

            return {
                "code": code,
                "interpretation": interpretation,
                "raw_response": full_content
            }
            
        except Exception as e:
            st.error(f"LLM 调用异常: {str(e)}")
            return None

    def generate_interpretation(self, user_query: str, chart_code: str):
        """
        进阶功能：专门生成图表的可解释性输出 。
        """
        # 可以作为单独的步骤，在图表生成后二次调用
        pass