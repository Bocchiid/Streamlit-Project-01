# /src/app.py

import pandas as pd
import streamlit as st
from data_processor import DataProcessor

# 页面配置
st.set_page_config(page_title="AI 数据可视化助手", layout="wide")

def main():
    st.title("📊 自然语言驱动的交互式可视化智能应用")
    st.markdown("---")

    # 初始化数据处理模块
    processor = DataProcessor()

    # 数据文件上传
    st.sidebar.header("数据集管理")
    uploaded_file = st.sidebar.file_uploader("上传CSV或Excel文件", type=["csv", "xlsx"])

    if uploaded_file is not None:
        # 加载数据
        df = processor.load_data(uploaded_file)
        
        if df is not None:
            # 显示数据集预览
            st.subheader("数据集预览")

            # 获取raw数据集基本信息
            data_info = processor.get_basic_info()

            # 数据清洗
            df = processor.basic_data_clean()

            with st.spinner("正在进行基础数据清洗..."):
                if st.session_state.get("is_cleaned") is None:
                    st.session_state["is_cleaned"] = True
                    st.toast("数据清洗完成！", icon="✅")

            # 展示数据集基本信息
            col1, col2, col3 = st.columns(3)
            col1.metric("样本总量 (行)", f"{data_info['shape'][0]}")
            col2.metric("特征数量 (列)", f"{data_info['shape'][1]}")
            col3.metric("总缺失值", f"{data_info['missing_values'].sum()}")

            st.markdown("### 📋 字段详细信息")
            
            detail_df = pd.DataFrame({
                "字段名称": data_info['dtypes'].index,
                "数据类型": data_info['dtypes'].values.astype(str),
                "缺失值数量": data_info['missing_values'].values
            })
            
            st.dataframe(detail_df, use_container_width=True, hide_index=True)

            # N行预览设置
            n_preview = st.sidebar.slider("预览前N行数据", min_value=0, max_value=data_info['shape'][0], value=10, step=5)

            st.markdown("### 🔍 数据预览")
            st.dataframe(processor.get_n_rows(n_preview), use_container_width=True)


if __name__ == "__main__":
    main()