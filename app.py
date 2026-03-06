import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

st.set_page_config(page_title="Student Success AI", layout="wide")

if "gcp_service_account" in st.secrets:
    # st.secretsを直接辞書に変換して渡す
    info = dict(st.secrets["gcp_service_account"])
    # 改行コードの修復
    info["private_key"] = info["private_key"].replace("\\n", "\n")
    credentials = service_account.Credentials.from_service_account_info(info)
    client = bigquery.Client(credentials=credentials, project=info["project_id"])
    
    st.title("🎓 大学生の習慣分析・成績向上アドバイザー")
    st.success("🎉 Secretの読み込みとBigQuery接続に成功しました！")
    
    # データ取得テスト
    df = client.query(f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 5").to_dataframe()
    st.dataframe(df)
else:
    st.error("Secret 'gcp_service_account' が見つかりません。")
