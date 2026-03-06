import streamlit as st
import pandas as pd
import os
import json
import re
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(page_title="Student Success AI", layout="wide")

def get_bq_client():
    # Secretsから取得
    raw_key = st.secrets.get("GCP_JSON_KEY")
    
    if raw_key:
        try:
            # 文字列の前後にある余計なシングル/ダブルクォートや空白を徹底的に掃除
            clean_key = raw_key.strip().strip("'").strip('"')
            
            # JSONとして読み込み
            info = json.loads(clean_key)
            
            # private_key内の改行コードを正常化
            if "private_key" in info:
                info["private_key"] = info["private_key"].replace("\\n", "\n")
            
            credentials = service_account.Credentials.from_service_account_info(info)
            return bigquery.Client(credentials=credentials, project=info["project_id"])
        except Exception as e:
            st.error(f"JSONパースエラー: {e}")
            # デバッグ用に中身の断片を表示（本番では削除推奨）
            st.code(raw_key[:50] + "..." + raw_key[-50:])
    
    return None

st.title("🎓 大学生の習慣分析・成績向上アドバイザー")

try:
    client = get_bq_client()
    if client:
        query = f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 5"
        df = client.query(query).to_dataframe()
        st.success("🎉 BigQuery への接続に成功しました！")
        st.dataframe(df)
    else:
        st.warning("認証情報 (GCP_JSON_KEY) が設定されていません。")
except Exception as e:
    st.error(f"接続エラー: {e}")
