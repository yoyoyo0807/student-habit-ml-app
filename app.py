import streamlit as st
import pandas as pd
import joblib
import os
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(page_title="Student Success AI", layout="wide")

@st.cache_resource
def load_model():
    return joblib.load("student_model.pkl")

@st.cache_resource
def get_bq_client():
    """デバッグ情報を表示しながらBigQueryクライアントを初期化"""
    if "gcp_service_account" not in st.secrets:
        st.error("Secretsに 'gcp_service_account' セクションが見つかりません。")
        return None
    
    info = dict(st.secrets["gcp_service_account"])
    pk = info.get("private_key", "")
    
    # --- デバッグ表示セクション ---
    st.write(f"DEBUG: 検出された秘密鍵の長さ = {len(pk)} 文字")
    if pk.startswith("-----BEGIN"):
        st.write("DEBUG: 鍵の開始ヘッダーを確認 ✅")
        # 改行コードの補正
        info["private_key"] = pk.strip().replace("\\n", "\n")
    else:
        st.error("DEBUG: 鍵の開始ヘッダーが不正です ❌")
        st.write(f"DEBUG: 鍵の先頭15文字 = '{pk[:15]}...'")
    # ----------------------------

    try:
        credentials = service_account.Credentials.from_service_account_info(info)
        return bigquery.Client(credentials=credentials, project=info["project_id"])
    except Exception as e:
        st.error(f"BigQueryクライアントの初期化に失敗しました: {e}")
        return None

def main():
    st.title("🎓 大学生の習慣分析・成績向上アドバイザー")

    try:
        model = load_model()
        st.sidebar.success("✅ 学習済みモデルをロードしました")
    except Exception as e:
        st.sidebar.error(f"❌ モデルのロードに失敗: {e}")
        st.stop()

    st.header("🔍 成績予測シミュレーション")
    col1, col2 = st.columns(2)
    with col1:
        study_hours_per_day = st.slider("1日の勉強時間 (時間)", 0.0, 15.0, 7.34)
        sleep_hours = st.slider("睡眠時間 (時間)", 0.0, 12.0, 3.19)
    with col2:
        social_media_hours = st.slider("SNS利用時間 (時間)", 0.0, 12.0, 2.0)
        attendance_percentage = st.slider("講義の出席率 (%)", 0.0, 100.0, 14.09)

    if st.button("AIで試験成績を予測する"):
        # 成功した順序（study -> sleep -> social -> attendance）を維持
        input_data = pd.DataFrame(
            [[study_hours_per_day, sleep_hours, social_media_hours, attendance_percentage]],
            columns=["study_hours_per_day", "sleep_hours", "social_media_hours", "attendance_percentage"],
        )
        try:
            prediction = model.predict(input_data)[0]
            st.metric(label="AI予測スコア (exam_score)", value=f"{prediction:.1f} 点")
        except Exception as e:
            st.error(f"予測エラー: {e}")

    st.divider()
    st.subheader("📊 実際の学習データ (BigQuery)")
    client = get_bq_client()
    if client:
        try:
            query = f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 5"
            df = client.query(query).to_dataframe()
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"クエリ実行エラー: {e}")

if __name__ == "__main__":
    main()
