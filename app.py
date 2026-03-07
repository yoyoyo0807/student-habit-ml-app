import streamlit as st
import pandas as pd
import joblib
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
    
    # 【重要】文字としての "\n" を 本物の改行コードに変換
    if "private_key" in info:
        info["private_key"] = info["private_key"].replace("\\n", "\n")
    
    try:
        credentials = service_account.Credentials.from_service_account_info(info)
        return bigquery.Client(credentials=credentials, project=info["project_id"])
    except Exception as e:
        st.error(f"BigQuery接続エラー: {e}")
        # 文字数確認（改行変換後）
        st.write(f"DEBUG: 変換後の鍵文字数: {len(info.get('private_key', ''))}")
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
        try:
            query = f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 5"
            df = client.query(query).to_dataframe()
            st.success("✅ BigQuery接続成功")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"クエリ実行エラー: {e}")

if __name__ == "__main__":
    main()
