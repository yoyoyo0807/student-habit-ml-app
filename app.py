import streamlit as st
import pandas as pd
import joblib
import os
from google.cloud import bigquery
import plotly.express as px

# ページ設定
st.set_page_config(page_title="Student Success AI", layout="wide")

# 認証設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "concise-booking-473310-a0-49cbb2545f4a.json"
client = bigquery.Client()

st.title("🎓 大学生の習慣分析・成績向上アドバイザー")
st.markdown("---")

@st.cache_data
def load_data():
    query = "SELECT * FROM `concise-booking-473310-a0.student_data.habits_performance`"
    return client.query(query).to_dataframe()

with st.spinner('BigQueryからデータを取得中...'):
    df = load_data()

# サイドバー: 予測シミュレーター
st.sidebar.header("📊 パラメータ設定")
study = st.sidebar.slider("1日の勉強時間 (時)", 0.0, 10.0, 4.0)
sleep = st.sidebar.slider("睡眠時間 (時)", 0.0, 12.0, 7.0)
sns = st.sidebar.slider("SNS利用時間 (時)", 0.0, 10.0, 2.0)
attendance = st.sidebar.slider("出席率 (%)", 0, 100, 90)

if os.path.exists('models/student_model.pkl'):
    model = joblib.load('models/student_model.pkl')
    features = ['study_hours_per_day', 'sleep_hours', 'social_media_hours', 'attendance_percentage']
    
    # 現在の予測
    input_df = pd.DataFrame([[study, sleep, sns, attendance]], columns=features)
    current_pred = model.predict(input_df)[0]
    
    # 爆速改善シミュレーション（勉強を1時間増やした場合）
    boost_df = pd.DataFrame([[study + 1.0, sleep, sns, attendance]], columns=features)
    boost_pred = model.predict(boost_df)[0]
    
    # 予測結果の表示
    st.sidebar.metric("予測スコア", f"{current_pred:.1f} 点", f"+{boost_pred - current_pred:.1f} (勉強+1h時)")
    
    if boost_pred > current_pred:
        st.sidebar.info(f"💡 アドバイス: 勉強時間をあと1時間増やすだけで、スコアが約 {boost_pred - current_pred:.1f} 点アップする見込みです！")

    # メインエリア: インサイト
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 データの全体傾向")
        fig = px.scatter(df, x="study_hours_per_day", y="exam_score", color="attendance_percentage", 
                         size="sleep_hours", hover_data=['diet_quality'], title="勉強時間・出席率・睡眠の相関図")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🎯 AIが重視する項目")
        importance = pd.DataFrame({'feature': features, 'importance': model.feature_importances_})
        fig_imp = px.bar(importance.sort_values('importance'), x='importance', y='feature', orientation='h')
        st.plotly_chart(fig_imp, use_container_width=True)

else:
    st.error("AIモデルが見つかりません。models/train_model.py を実行してください。")

st.markdown("---")
st.subheader("📂 取得データサンプル (Top 5)")
st.dataframe(df.head())
