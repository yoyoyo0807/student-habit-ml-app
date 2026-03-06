import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery
import os

st.set_page_config(page_title="Student Success AI", layout="wide")

def get_bq_client():
    # 1. Streamlit CloudのSecretsを確認
    if "gcp_service_account" in st.secrets:
        info = dict(st.secrets["gcp_service_account"])
        # 改行コードの整形
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        credentials = service_account.Credentials.from_service_account_info(info)
        return bigquery.Client(credentials=credentials, project=info["project_id"])
    
    # 2. ローカル用 (JSONファイル)
    json_path = "concise-booking-473310-a0-49cbb2545f4a.json"
    if os.path.exists(json_path):
        return bigquery.Client.from_service_account_json(json_path)
    
    return None

st.title("🎓 大学生の習慣分析・成績向上アドバイザー")

try:
    client = get_bq_client()
    if client:
        # 実際にデータを取得して確認
        query = f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 5"
        df = client.query(query).to_dataframe()
        st.success("🎉 BigQuery への接続に成功しました！")
        st.dataframe(df)
    else:
        st.error("認証情報が見つかりません。")
except Exception as e:
    st.error(f"接続エラーが発生しました: {e}")

