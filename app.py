import streamlit as st
import pandas as pd
import joblib
import os
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(page_title="Student Success AI", layout="wide")

@st.cache_resource
def load_model():
    """学習済みモデルをキャッシュしてロード"""
    return joblib.load("student_model.pkl")

@st.cache_resource
def get_bq_client():
    """Streamlit Secretsから認証情報を読み込み、改行コードを補正してクライアントを作成"""
    try:
        if "gcp_service_account" not in st.secrets:
            return None

        info = dict(st.secrets["gcp_service_account"])

        if "private_key" in info and isinstance(info["private_key"], str):
            # 秘密鍵内の文字列としての \n を実際の改行文字に置換し、余計な空白を削除
            info["private_key"] = info["private_key"].strip().replace("\\n", "\n")

        credentials = service_account.Credentials.from_service_account_info(info)
        return bigquery.Client(
            credentials=credentials,
            project=info["project_id"],
        )
    except Exception as e:
        st.error(f"BigQueryクライアントの初期化に失敗しました: {e}")
        return None

def main():
    st.title("🎓 大学生の習慣分析・成績向上アドバイザー")

    # --- 1. モデルのロード ---
    try:
        model = load_model()
        st.sidebar.success("✅ 学習済みモデルをロードしました")
    except Exception as e:
        st.sidebar.error(f"❌ モデルのロードに失敗: {e}")
        st.stop()

    # --- 2. 予測シミュレーション ---
    st.header("🔍 成績予測シミュレーション")
    col1, col2 = st.columns(2)

    with col1:
        # モデルが期待する正確な特徴量名と順序に基づいた入力項目
        study_hours_per_day = st.slider("1日の勉強時間 (時間)", 0.0, 15.0, 7.3)
        sleep_hours = st.slider("睡眠時間 (時間)", 0.0, 12.0, 3.2)

    with col2:
        social_media_hours = st.slider("SNS利用時間 (時間)", 0.0, 12.0, 2.0)
        attendance_percentage = st.slider("講義の出席率 (%)", 0.0, 100.0, 14.1)

    if st.button("AIで試験成績を予測する"):
        # モデル学習時と全く同じ列名および順番でDataFrameを作成
        input_data = pd.DataFrame(
            [[study_hours_per_day, sleep_hours, social_media_hours, attendance_percentage]],
            columns=["study_hours_per_day", "sleep_hours", "social_media_hours", "attendance_percentage"],
        )

        try:
            # 予測スコアの算出
            prediction = model.predict(input_data)[0]
            st.metric(label="予測スコア (exam_score)", value=f"{prediction:.1f} 点")

            if prediction < 60:
                st.warning("⚠️ 生活習慣を見直すことで、スコアがさらに伸びる可能性があります！")
            else:
                st.balloons()
                st.info("✨ 素晴らしい習慣です！この調子で継続しましょう。")
        except Exception as e:
            st.error(f"予測中にエラーが発生しました。モデルの期待する形式を確認してください: {e}")

    # --- 3. BigQueryデータの表示 ---
    st.divider()
    st.subheader("📊 実際の学習データ (BigQuery)")

    client = get_bq_client()
    if client is None:
        st.warning("BigQueryのSecretsが未設定、または接続に失敗しました。公開後はStreamlit設定が必要です。")
        return

    # 実績データ取得クエリ
    query = f"""
        SELECT student_id, study_hours_per_day, sleep_hours, social_media_hours, attendance_percentage, exam_score
        FROM `{client.project}.student_data.habits_performance`
        LIMIT 5
    """

    try:
        df = client.query(query).to_dataframe()
        st.success("✅ BigQueryから最新データを取得しました")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"BigQueryのクエリ実行に失敗しました: {e}")

if __name__ == "__main__":
    main()
