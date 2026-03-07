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
    
    # 文字としての "\n" を 本物の改行コードに変換
    if "private_key" in info:
        info["private_key"] = info["private_key"].replace("\\n", "\n")
    
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
        st.sidebar.error("❌ モデルのロードに失敗しました")
        st.stop()

    st.header("🔍 成績予測シミュレーション")
    col1, col2 = st.columns(2)
    with col1:
        study = st.slider("1日の勉強時間 (時間)", 0.0, 15.0, 7.34)
        sleep = st.slider("睡眠時間 (時間)", 0.0, 12.0, 7.0)
    with col2:
        social = st.slider("SNS利用時間 (時間)", 0.0, 12.0, 2.0)
        attendance = st.slider("講義の出席率 (%)", 0.0, 100.0, 80.0)

    if st.button("AIで試験成績を予測する"):
        input_df = pd.DataFrame([[study, sleep, social, attendance]], 
                                columns=["study_hours_per_day", "sleep_hours", "social_media_hours", "attendance_percentage"])
        prediction = model.predict(input_df)[0]
        
        # スコアの表示
        st.divider()
        st.metric(label="AI予測スコア (exam_score)", value=f"{prediction:.1f} 点")

        # --- 追加機能: 動的アドバイスロジック ---
        if prediction >= 80:
            st.success("🌟 **素晴らしい予測結果です！** 現在の習慣を維持すれば、トップクラスの成績が期待できます。")
        elif prediction >= 60:
            st.info("✅ **合格圏内です。** 安定した成績ですが、勉強時間をあと少し増やすとさらにスコアが伸びる可能性があります。")
        else:
            st.warning("⚠️ **もっと勉強や生活習慣の改善が必要です。** 特に勉強時間や出席率を見直すことで、スコアを大きく改善できるでしょう。")

    st.divider()
    st.subheader("📊 実際の学習データ (BigQuery)")
    client = get_bq_client()
    if client:
        try:
            query = f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 5"
            df = client.query(query).to_dataframe()
            st.success("✅ BigQueryから最新データを取得しました")
            
            # --- 警告修正: use_container_width=True を width="stretch" に変更 ---
            st.dataframe(df, width="stretch")
            
        except Exception as e:
            st.error(f"クエリ実行エラー: {e}")

if __name__ == "__main__":
    main()
