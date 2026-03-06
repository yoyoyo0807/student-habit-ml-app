import streamlit as st
import pandas as pd
import joblib
import os
from google.oauth2 import service_account
from google.cloud import bigquery
import plotly.express as px

# ページ設定
st.set_page_config(page_title="Student Success AI", layout="wide")

# Secretsから認証情報を取得
if "gcp_service_account" in st.secrets:
    # 辞書形式で取得し、認証オブジェクトを作成
    credentials_info = dict(st.secrets["gcp_service_account"])
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    client = bigquery.Client(credentials=credentials, project=credentials_info["project_id"])
    st.success("BigQuery認証に成功しました！")
else:
    # ローカル開発用（Secretsがない場合）
    json_path = "concise-booking-473310-a0-49cbb2545f4a.json"
    if os.path.exists(json_path):
        client = bigquery.Client.from_service_account_json(json_path)
    else:
        st.error("認証情報が見つかりません。")
        st.stop()

st.title("🎓 大学生の習慣分析・成績向上アドバイザー")

@st.cache_data
def load_data():
    query = f"SELECT * FROM `{client.project}.student_data.habits_performance`"
    return client.query(query).to_dataframe()

# データ取得
try:
    df = load_data()
except Exception as e:
    st.error(f"データの取得に失敗しました: {e}")
    st.stop()

# --- メインコンテンツ（グラフや予測） ---
st.sidebar.header("📊 パラメータ設定")
study = st.sidebar.slider("1日の勉強時間 (時)", 0.0, 10.0, 4.0)
sleep = st.sidebar.slider("睡眠時間 (時)", 0.0, 12.0, 7.0)
sns = st.sidebar.slider("SNS利用時間 (時)", 0.0, 10.0, 2.0)
attendance = st.sidebar.slider("出席率 (%)", 0, 100, 90)

if os.path.exists('models/student_model.pkl'):
    model = joblib.load('models/student_model.pkl')
    features = ['study_hours_per_day', 'sleep_hours', 'social_media_hours', 'attendance_percentage']
    input_df = pd.DataFrame([[study, sleep, sns, attendance]], columns=features)
    prediction = model.predict(input_df)[0]
    st.sidebar.metric("予測スコア", f"{prediction:.1f} 点")

st.subheader("📈 データの全体傾向")
fig = px.scatter(df, x="study_hours_per_day", y="exam_score", color="attendance_percentage")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📂 取得データサンプル")
st.dataframe(df.head())
