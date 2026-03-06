import streamlit as st
import pandas as pd
import os
import json
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(page_title="Student Success AI", layout="wide")

def get_bq_client():
    # 1. 環境変数 (GitHub/Streamlitの環境変数) から取得を試みる
    env_key = os.getenv("GCP_JSON_KEY")
    
    if env_key:
        info = json.loads(env_key)
        credentials = service_account.Credentials.from_service_account_info(info)
        return bigquery.Client(credentials=credentials, project=info["project_id"])
    
    # 2. ローカル環境用 (JSONファイル)
    json_path = "concise-booking-473310-a0-49cbb2545f4a.json"
    if os.path.exists(json_path):
        return bigquery.Client.from_service_account_json(json_path)
    
    return None

st.title("🎓 大学生の習慣分析・成績向上アドバイザー")

try:
    client = get_bq_client()
    if client:
        query = f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 5"
        df = client.query(query).to_dataframe()
        st.success("認証に成功しました！")
        st.dataframe(df)
    else:
        st.error("認証情報が見つかりません。")
except Exception as e:
    st.error(f"エラー: {e}")
