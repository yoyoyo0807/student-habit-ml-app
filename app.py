import streamlit as st
import pandas as pd
import joblib
import os
import json
import base64
from google.cloud import bigquery

st.set_page_config(page_title="Student Success AI", layout="wide")

def get_bq_client():
    # SecretsからBase64形式の鍵を取得
    if "GCP_SERVICE_ACCOUNT_BASE64" in st.secrets:
        encoded_key = st.secrets["GCP_SERVICE_ACCOUNT_BASE64"]
        # デコードして辞書形式に戻す
        decoded_key = base64.b64decode(encoded_key).decode("utf-8")
        info = json.loads(decoded_key)
        
        # 一時的なJSONファイルとして書き出してBigQueryクライアントを作成
        with open("temp_key.json", "w") as f:
            json.dump(info, f)
        return bigquery.Client.from_service_account_json("temp_key.json")
    else:
        # ローカル環境用
        return bigquery.Client.from_service_account_json("concise-booking-473310-a0-49cbb2545f4a.json")

try:
    client = get_bq_client()
    
    st.title("🎓 大学生の習慣分析・成績向上アドバイザー")
    
    # データ取得
    query = f"SELECT * FROM `{client.project}.student_data.habits_performance`"
    df = client.query(query).to_dataframe()
    st.success("BigQuery との連携に成功しました！")

    # サイドバー: パラメータ設定
    st.sidebar.header("📊 パラメータ設定")
    study = st.sidebar.slider("1日の勉強時間 (時)", 0.0, 10.0, 4.0)
    sleep = st.sidebar.slider("睡眠時間 (時)", 0.0, 12.0, 7.0)
    sns = st.sidebar.slider("SNS利用時間 (時)", 0.0, 10.0, 2.0)
    attendance = st.sidebar.slider("出席率 (%)", 0, 100, 90)

    # モデル読み込みと予測
    if os.path.exists('models/student_model.pkl'):
        model = joblib.load('models/student_model.pkl')
        features = ['study_hours_per_day', 'sleep_hours', 'social_media_hours', 'attendance_percentage']
        input_df = pd.DataFrame([[study, sleep, sns, attendance]], columns=features)
        prediction = model.predict(input_df)[0]
        st.sidebar.metric("予測試験スコア", f"{prediction:.1f} 点")
    
    st.write("### 取得データサンプル", df.head())

except Exception as e:
    st.error(f"エラーが発生しました: {e}")
