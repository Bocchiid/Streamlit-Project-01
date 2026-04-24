# /src/data_processor.py

import pandas as pd
import streamlit as st

class DataProcessor:
    def __init__(self):
        self.df = None

    '''加载CSV或Excel数据文件'''
    def load_data(self, file):
        try:
            if file.name.endswith('.csv'):
                self.df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                self.df = pd.read_excel(file)

            if len(self.df) > 10000:
                st.warning("数据量超过10000行, 可能会影响性能。")
            elif len(self.df.columns) > 20:
                st.warning("字段数量超过20列, 可能会影响性能。")
            return self.df
        except Exception as e:
            st.error(f"加载文件失败: {e}")
            return None

    '''获取数据维度、字段类型和缺失值统计'''
    def get_basic_info(self):
        if self.df is not None:
            info = {
                "shape": self.df.shape,
                "dtypes": self.df.dtypes,
                "missing_values": self.df.isnull().sum()
            }
            return info
        return None

    '''获取前N行数据'''
    def get_n_rows(self, n=10): # 默认预览前10行
        if self.df is not None:
            return self.df.head(min(n, len(self.df))) # 防止n超过数据行数
        return None

    '''完成基础数据清洗(处理缺失值、异常值)'''
    def basic_data_clean(self):
        if self.df is not None:
            # 数值型填补平均值，字符型填补'Unknown'
            for col in self.df.columns:
                if self.df[col].dtype in ['int64', 'float64']:
                    self.df[col] = self.df[col].fillna(self.df[col].mean())
                else:
                    self.df[col] = self.df[col].fillna('Unknown')
            return self.df