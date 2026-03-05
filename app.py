import streamlit as st
import pandas as pd
from google.cloud import bigquery

# ページ設定
st.set_page_config(page_title="大学生習慣分析", layout="wide")

# BigQueryクライアントの初期化
# ※ローカル実行時は環境変数 GOOGLE_APPLICATION_CREDENTIALS に鍵パスを通すか
#   Streamlit CloudのSecrets機能を使います
client = bigquery.Client(project="concise-booking-473310-a0")

st.title("🎓 大学生の習慣化支援・成績予測アプリ")

@st.cache_data
def load_data():
    query = "SELECT * FROM `concise-booking-473310-a0.student_data.habits_performance`"
    return client.query(query).to_dataframe()

df = load_data()

# データの表示
st.write("### BigQueryから取得した生データ", df.head())

# 簡単な可視化
st.bar_chart(df.groupby('diet_quality')['exam_score'].mean())
