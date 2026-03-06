import streamlit as st
import pandas as pd
import joblib
import os
from google.cloud import bigquery
import plotly.express as px

# 認証設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "concise-booking-473310-a0-49cbb2545f4a.json"
client = bigquery.Client()

st.set_page_config(page_title="大学生習慣分析", layout="wide")
st.title("🎓 大学生の習慣分析・成績予測アプリ")

@st.cache_data
def load_data():
    query = "SELECT * FROM `concise-booking-473310-a0.student_data.habits_performance`"
    return client.query(query).to_dataframe()

df = load_data()

# サイドバー: 予測機能
st.sidebar.header("📊 成績予測シミュレーター")
study = st.sidebar.slider("1日の勉強時間 (時)", 0.0, 10.0, 4.0)
sleep = st.sidebar.slider("睡眠時間 (時)", 0.0, 12.0, 7.0)
sns = st.sidebar.slider("SNS利用時間 (時)", 0.0, 10.0, 2.0)
attendance = st.sidebar.slider("出席率 (%)", 0, 100, 90)

if os.path.exists('models/student_model.pkl'):
    model = joblib.load('models/student_model.pkl')
    # 警告回避のためDataFrame形式で入力
    input_df = pd.DataFrame([[study, sleep, sns, attendance]], 
                            columns=['study_hours_per_day', 'sleep_hours', 'social_media_hours', 'attendance_percentage'])
    prediction = model.predict(input_df)
    st.sidebar.success(f"あなたの予測試験スコア: {prediction[0]:.1f}点")
else:
    st.sidebar.warning("モデルを先に学習させてください (train_model.pyを実行)")

# メイン画面: データ分析
st.header("📈 データ分析インサイト")
col1, col2 = st.columns(2)

with col1:
    st.write("### 睡眠時間とスコアの相関")
    fig = px.scatter(df, x="sleep_hours", y="exam_score", color="diet_quality")
    st.plotly_chart(fig)

with col2:
    st.write("### 学習時間別の平均スコア")
    # エラー回避のため型変換
    df['study_bin'] = pd.cut(df['study_hours_per_day'], bins=5).astype(str)
    bin_avg = df.groupby('study_bin', observed=True)['exam_score'].mean().reset_index()
    st.bar_chart(data=bin_avg, x='study_bin', y='exam_score')

# 生データの表示
st.write("### BigQueryから取得した生データ", df.head())
