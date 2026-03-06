import streamlit as st
import pandas as pd
import joblib
import os
from google.cloud import bigquery
from google.oauth2 import service_account

# ページ設定
st.set_page_config(page_title="Student Success AI", layout="wide")

# 認証設定
if "gcp_service_account" in st.secrets:
    info = dict(st.secrets["gcp_service_account"])
    # \n を実際の改行コードに変換する処理を追加
    info["private_key"] = info["private_key"].replace("\\n", "\n")
    credentials = service_account.Credentials.from_service_account_info(info)
    client = bigquery.Client(credentials=credentials, project=info["project_id"])
else:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "concise-booking-473310-a0-49cbb2545f4a.json"
    client = bigquery.Client()

st.title("🎓 大学生の習慣分析・成績向上アドバイザー")

# --- データ取得 ---
@st.cache_data
def load_data():
    query = f"SELECT * FROM `{client.project}.student_data.habits_performance`"
    return client.query(query).to_dataframe()

try:
    df = load_data()
    st.success("BigQueryに接続しました！")
    st.dataframe(df.head())
except Exception as e:
    st.error(f"接続エラー: {e}")
