import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery
import os
import joblib
import plotly.express as px

st.set_page_config(page_title="Student Success AI", layout="wide")

def get_bq_client():
    # 1. Streamlit CloudのSecretsから [gcp_service_account] セクションを取得
    if "gcp_service_account" in st.secrets:
        info = dict(st.secrets["gcp_service_account"])
        
        # 秘密鍵の改行コードをPythonが扱える形式に整形
        if "private_key" in info:
            # Secretsに \n 文字として入っていても、実際の改行として入っていても対応
            info["private_key"] = info["private_key"].replace("\\n", "\n").strip()
        
        try:
            credentials = service_account.Credentials.from_service_account_info(info)
            return bigquery.Client(credentials=credentials, project=info["project_id"])
        except Exception as e:
            st.error(f"認証オブジェクトの作成に失敗しました: {e}")
            return None
    
    # 2. ローカル開発用 (JSONファイル)
    json_path = "concise-booking-473310-a0-49cbb2545f4a.json"
    if os.path.exists(json_path):
        return bigquery.Client.from_service_account_json(json_path)
    
    return None

st.title("🎓 大学生の習慣分析・成績向上アドバイザー")

try:
    client = get_bq_client()
    if client:
        # データのロード
        @st.cache_data
        def load_data():
            query = f"SELECT * FROM `{client.project}.student_data.habits_performance`"
            return client.query(query).to_dataframe()
        
        df = load_data()
        st.success("🎉 BigQuery への接続に成功しました！")
        
        # --- メインコンテンツ ---
        st.subheader("📈 データの可視化")
        fig = px.scatter(df, x="study_hours_per_day", y="exam_score", 
                         color="attendance_percentage", 
                         title="勉強時間と試験成績の相関")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📂 取得データサンプル")
        st.dataframe(df.head())
        
    else:
        st.error("認証情報が見つかりません。Secretsの設定を確認してください。")

except Exception as e:
    st.error(f"接続またはデータ取得中にエラーが発生しました: {e}")
