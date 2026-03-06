import streamlit as st
import pandas as pd
import os
import json
import base64
from google.cloud import bigquery
from google.oauth2 import service_account
import plotly.express as px

st.set_page_config(page_title="Student Success AI", layout="wide")

def get_bq_client():
    # SecretsからBase64形式の鍵を取得
    if "GCP_SERVICE_ACCOUNT_BASE64" in st.secrets:
        encoded_key = st.secrets["GCP_SERVICE_ACCOUNT_BASE64"]
        try:
            # デコードしてJSON辞書に復元
            decoded_key = base64.b64decode(encoded_key).decode("utf-8")
            info = json.loads(decoded_key)
            
            # private_key内の改行文字を正規化
            if "private_key" in info:
                info["private_key"] = info["private_key"].replace("\\n", "\n")
            
            credentials = service_account.Credentials.from_service_account_info(info)
            return bigquery.Client(credentials=credentials, project=info["project_id"])
        except Exception as e:
            st.error(f"認証デコードエラー: {e}")
            return None
    else:
        # ローカル環境用
        json_path = "concise-booking-473310-a0-49cbb2545f4a.json"
        if os.path.exists(json_path):
            return bigquery.Client.from_service_account_json(json_path)
        return None

st.title("🎓 大学生の習慣分析・成績向上アドバイザー")

try:
    client = get_bq_client()
    if client:
        # データ取得
        query = f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 100"
        df = client.query(query).to_dataframe()
        st.success("🎉 BigQuery への接続に成功しました！")
        
        # グラフ表示
        st.subheader("📈 データの可視化")
        fig = px.scatter(df, x="study_hours_per_day", y="exam_score", 
                         color="attendance_percentage", title="勉強時間と試験成績の相関")
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("### 取得データサンプル")
        st.dataframe(df.head())
    else:
        st.warning("認証情報が設定されていません。")

except Exception as e:
    st.error(f"接続エラー: {e}")
