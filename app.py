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
    
    if "private_key" in credentials_info:
        # 【決定版】秘密鍵の前後にある余計な文字や引用符を徹底的に排除する
        key = credentials_info["private_key"].strip().strip('"').strip("'")
        # \n という文字列を本物の改行に変換し、末尾の余計な空白を消す
        credentials_info["private_key"] = key.replace("\\n", "\n").rstrip()
    
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
    st.success("🎉 ついに BigQuery への接続に成功しました！")
    
    # メインコンテンツの表示
    st.subheader("📈 データの全体傾向")
    fig = px.scatter(df, x="study_hours_per_day", y="exam_score", color="attendance_percentage")
    st.plotly_chart(fig, use_container_width=True)
    st.write("### 取得データサンプル", df.head())
    
except Exception as e:
    st.error(f"接続に失敗しました。Secretsの private_key の末尾を確認してください: {e}")
