import streamlit as st
import pandas as pd
import joblib
import os
from google.oauth2 import service_account
from google.cloud import bigquery
import plotly.express as px

st.set_page_config(page_title="Student Success AI", layout="wide")

# Secretsから認証情報を取得
if "gcp_service_account" in st.secrets:
    credentials_info = dict(st.secrets["gcp_service_account"])
    
    # 【重要】秘密鍵の改行コードをPythonが理解できる形式に強制変換
    if "private_key" in credentials_info:
        credentials_info["private_key"] = credentials_info["private_key"].replace("\\n", "\n")
    
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    client = bigquery.Client(credentials=credentials, project=credentials_info["project_id"])
else:
    # ローカル用
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "concise-booking-473310-a0-49cbb2545f4a.json"
    client = bigquery.Client()

st.title("🎓 大学生の習慣分析・成績向上アドバイザー")

@st.cache_data
def load_data():
    query = f"SELECT * FROM `{client.project}.student_data.habits_performance`"
    return client.query(query).to_dataframe()

try:
    df = load_data()
    st.success("🎉 サーバーとの接続に成功しました！")
    
    # グラフの表示
    st.subheader("📈 データの全体傾向")
    fig = px.scatter(df, x="study_hours_per_day", y="exam_score", color="attendance_percentage")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df.head())
    
except Exception as e:
    st.error(f"接続エラー: {e}")
