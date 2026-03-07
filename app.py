import streamlit as st
import pandas as pd
import joblib
import os
import re
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(page_title="Student Success AI", layout="wide")

@st.cache_resource
def load_model():
    return joblib.load("student_model.pkl")

@st.cache_resource
def get_bq_client():
    if "gcp_service_account" not in st.secrets:
        return None
    
    info = dict(st.secrets["gcp_service_account"])
    pk = info.get("private_key", "")

    # --- 強制整形ロジック ---
    # 1. ヘッダーとフッターを一旦取り除く
    body = pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
    # 2. 全ての改行、空白、バックスラッシュ、\n という文字列を除去
    body = re.sub(r'[\s\\n]', '', body)
    # 3. 正しいヘッダーとフッターで包み直す
    clean_pk = f"-----BEGIN PRIVATE KEY-----\n{body}\n-----END PRIVATE KEY-----"
    info["private_key"] = clean_pk
    # -----------------------

    try:
        credentials = service_account.Credentials.from_service_account_info(info)
        return bigquery.Client(credentials=credentials, project=info["project_id"])
    except Exception as e:
        st.error(f"BigQuery接続エラー: {e}")
        return None

def main():
    st.title("🎓 大学生の習慣分析・成績向上アドバイザー")
    try:
        model = load_model()
        st.sidebar.success("✅ モデルをロードしました")
    except Exception:
        st.sidebar.error("❌ ロード失敗")
        st.stop()

    st.header("🔍 成績予測シミュレーション")
    col1, col2 = st.columns(2)
    with col1:
        study = st.slider("1日の勉強時間", 0.0, 15.0, 7.34)
        sleep = st.slider("睡眠時間", 0.0, 12.0, 3.19)
    with col2:
        social = st.slider("SNS利用時間", 0.0, 12.0, 2.0)
        attendance = st.slider("講義の出席率", 0.0, 100.0, 14.09)

    if st.button("AIで試験成績を予測する"):
        input_df = pd.DataFrame([[study, sleep, social, attendance]], 
                                columns=["study_hours_per_day", "sleep_hours", "social_media_hours", "attendance_percentage"])
        prediction = model.predict(input_df)[0]
        st.metric(label="AI予測スコア (exam_score)", value=f"{prediction:.1f} 点")

    st.divider()
    st.subheader("📊 実際の学習データ (BigQuery)")
    client = get_bq_client()
    if client:
        query = f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 5"
        df = client.query(query).to_dataframe()
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
