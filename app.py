import streamlit as st
import pandas as pd
import joblib
import os
from google.oauth2 import service_account
from google.cloud import bigquery

st.set_page_config(page_title="Student Success AI", layout="wide")

# Secretsから認証情報を取得
if "gcp_service_account" in st.secrets:
    # 辞書として取得
    info = dict(st.secrets["gcp_service_account"])
    
    # \n を実際の改行に戻す（これだけで十分です）
    info["private_key"] = info["private_key"].replace("\\n", "\n")
    
    try:
        credentials = service_account.Credentials.from_service_account_info(info)
        client = bigquery.Client(credentials=credentials, project=info["project_id"])
    except Exception as e:
        st.error(f"認証オブジェクト作成エラー: {e}")
        st.stop()
else:
    # ローカル用
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "concise-booking-473310-a0-49cbb2545f4a.json"
    client = bigquery.Client()

st.title("🎓 大学生の習慣分析・成績向上アドバイザー")

@st.cache_data
def load_data():
    query = f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 10"
    return client.query(query).to_dataframe()

try:
    df = load_data()
    st.success("🎉 BigQuery への接続に成功しました！")
    st.dataframe(df)
except Exception as e:
    st.error(f"データ取得エラー: {e}")
