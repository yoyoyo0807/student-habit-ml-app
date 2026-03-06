import streamlit as st
import pandas as pd
import joblib
import os
import json
from google.cloud import bigquery

# ページ設定
st.set_page_config(page_title="Student Success AI", layout="wide")

# 認証設定（Secretsを一時ファイルとして書き出す方式）
def get_bq_client():
    if "gcp_service_account" in st.secrets:
        # Secretsから辞書を取得
        info = dict(st.secrets["gcp_service_account"])
        # 鍵のフォーマットを修正
        info["private_key"] = info["private_key"].replace("\\n", "\n").strip().strip('"')
        
        # 一時的なJSONファイルを作成
        with open("temp_key.json", "w") as f:
            json.dump(info, f)
        
        return bigquery.Client.from_service_account_json("temp_key.json")
    else:
        # ローカル環境用
        return bigquery.Client.from_service_account_json("concise-booking-473310-a0-49cbb2545f4a.json")

try:
    client = get_bq_client()
    st.success("BigQuery 認証成功！")
    
    # データ取得
    query = f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 5"
    df = client.query(query).to_dataframe()
    st.dataframe(df)
    
except Exception as e:
    st.error(f"認証またはデータ取得に失敗しました: {e}")
    # 秘密鍵の形式をデバッグ表示（重要：本番では消すこと）
    if "gcp_service_account" in st.secrets:
        st.write("Key starts with:", st.secrets["gcp_service_account"]["private_key"][:30])
        st.write("Key ends with:", st.secrets["gcp_service_account"]["private_key"][-30:])
