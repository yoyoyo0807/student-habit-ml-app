import streamlit as st
import pandas as pd
import joblib
import os
from google.cloud import bigquery
from google.oauth2 import service_account
import plotly.express as px

# ページ設定
st.set_page_config(page_title="Student Success AI", layout="wide")

# 認証設定
if "gcp_service_account" in st.secrets:
    # Secretsから直接辞書として取得（加工はライブラリに任せる）
    info = dict(st.secrets["gcp_service_account"])
    credentials = service_account.Credentials.from_service_account_info(info)
    client = bigquery.Client(credentials=credentials, project=info["project_id"])
else:
    # ローカル開発環境用（JSONファイルを使用）
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "concise-booking-473310-a0-49cbb2545f4a.json"
    client = bigquery.Client()

st.title("🎓 大学生の習慣分析・成績向上アドバイザー")

@st.cache_data
def load_data():
    query = f"SELECT * FROM `{client.project}.student_data.habits_performance`"
    return client.query(query).to_dataframe()

try:
    df = load_data()
    st.success("BigQuery への接続に成功しました！")
    st.write("### 取得データサンプル", df.head())
except Exception as e:
    st.error(f"接続エラーが発生しました: {e}")
