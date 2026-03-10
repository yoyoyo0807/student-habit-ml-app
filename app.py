import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import numpy as np
from google.cloud import bigquery
from google.oauth2 import service_account
from sklearn.metrics import mean_absolute_error, r2_score

st.set_page_config(page_title="Student Success AI", layout="wide")

@st.cache_resource
def load_model():
    return joblib.load("student_model.pkl")

@st.cache_resource
def get_bq_client():
    if "gcp_service_account" not in st.secrets:
        return None
    info = dict(st.secrets["gcp_service_account"])
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
        st.sidebar.error("❌ モデルロード失敗")
        st.stop()

    # --- セクション1: 予測シミュレーター ---
    st.header("🔍 成績予測シミュレーション")
    col1, col2 = st.columns(2)
    with col1:
        study = st.slider("1日の勉強時間 (h)", 0.0, 15.0, 7.34)
        sleep = st.slider("睡眠時間 (h)", 0.0, 12.0, 7.0)
    with col2:
        social = st.slider("SNS利用時間 (h)", 0.0, 12.0, 2.0)
        attendance = st.slider("講義の出席率 (%)", 0.0, 100.0, 80.0)

    if st.button("AIで試験成績を予測する"):
        input_df = pd.DataFrame([[study, sleep, social, attendance]], 
                                columns=["study_hours_per_day", "sleep_hours", "social_media_hours", "attendance_percentage"])
        prediction = model.predict(input_df)[0]
        st.divider()
        st.metric(label="AI予測スコア (exam_score)", value=f"{prediction:.1f} 点")

        if prediction >= 80:
            st.success("🌟 **素晴らしい結果です！**")
        elif prediction >= 60:
            st.info("✅ **合格圏内です。**")
        else:
            st.warning("⚠️ **改善が必要です。**")

    st.divider()

    # --- セクション2: ダッシュボード & モデル再評価 ---
    st.header("📊 データ分析 & AI精度検証")
    client = get_bq_client()
    if client:
        try:
            query = f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 100"
            df = client.query(query).to_dataframe()
            
            tab1, tab2, tab3 = st.tabs(["傾向分析", "AI精度検証 (答え合わせ)", "生データ"])
            
            with tab1:
                st.subheader("勉強時間と成績の相関")
                fig = px.scatter(df, x="study_hours_per_day", y="exam_score", color="attendance_percentage", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.subheader("AI予測 vs 実際の成績")
                # 分析用データで予測を実行
                X_test = df[["study_hours_per_day", "sleep_hours", "social_media_hours", "attendance_percentage"]]
                y_true = df["exam_score"]
                y_pred = model.predict(X_test)
                
                # 指標計算
                mae = mean_absolute_error(y_true, y_pred)
                r2 = r2_score(y_true, y_pred)
                
                c1, c2 = st.columns(2)
                c1.metric("平均誤差 (MAE)", f"±{mae:.2f} 点")
                c2.metric("モデル精度 (R2 Score)", f"{r2:.2f}")

                # 予測値と実測値の比較グラフ
                eval_df = pd.DataFrame({"Actual": y_true, "Predicted": y_pred})
                fig_eval = px.scatter(eval_df, x="Actual", y="Predicted", trendline="ols",
                                     title="予測と実測のプロット (線に近いほど正確)", template="plotly_white")
                st.plotly_chart(fig_eval, use_container_width=True)

            with tab3:
                st.dataframe(df, width="stretch")
            
        except Exception as e:
            st.error(f"分析エラー: {e}")

if __name__ == "__main__":
    main()
