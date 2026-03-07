import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
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

    # --- セクション1: 予測シミュレーター ---
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
        
        st.divider()
        st.metric(label="AI予測スコア (exam_score)", value=f"{prediction:.1f} 点")

        if prediction >= 80:
            st.success("🌟 **素晴らしい予測結果です！** 現在の習慣を維持すれば、トップクラスの成績が期待できます。")
        elif prediction >= 60:
            st.info("✅ **合格圏内です。** 安定した成績ですが、勉強時間をあと少し増やすとさらにスコアが伸びる可能性があります。")
        else:
            st.warning("⚠️ **もっと勉強や生活習慣の改善が必要です。** 特に勉強時間や出席率を見直すことで、スコアを大きく改善できるでしょう。")

    st.divider()

    # --- セクション2: BigQuery ダッシュボード ---
    st.header("📊 データダッシュボード (傾向分析)")
    client = get_bq_client()
    if client:
        try:
            # 分析用に100件程度のデータを取得
            query = f"SELECT * FROM `{client.project}.student_data.habits_performance` LIMIT 100"
            df = client.query(query).to_dataframe()
            
            # タブ分けして表示
            tab1, tab2, tab3 = st.tabs(["相関分析 (散布図)", "出席率と成績 (比較)", "生データ"])
            
            with tab1:
                st.subheader("勉強時間と予測スコアの相関")
                fig_scatter = px.scatter(
                    df, x="study_hours_per_day", y="exam_score", 
                    color="attendance_percentage",
                    labels={"study_hours_per_day": "勉強時間 (h)", "exam_score": "スコア", "attendance_percentage": "出席率(%)"},
                    title="勉強時間が増えるほどスコアは上がるか？",
                    template="plotly_white"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
                st.write("💡 散布図を見ると、勉強時間（横軸）とスコア（縦軸）の間に正の相関があるかがわかります。")

            with tab2:
                st.subheader("出席率によるスコア平均の差")
                # 出席率80%以上を「高」、それ未満を「低」としてグループ化
                df['attendance_group'] = df['attendance_percentage'].apply(lambda x: 'High (>=80%)' if x >= 80 else 'Low (<80%)')
                avg_scores = df.groupby('attendance_group')['exam_score'].mean().reset_index()
                
                fig_bar = px.bar(
                    avg_scores, x="attendance_group", y="exam_score",
                    color="attendance_group",
                    labels={"attendance_group": "出席率グループ", "exam_score": "平均スコア"},
                    title="出席率が成績に与える影響",
                    text_auto='.1f'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                st.write("💡 一般的に、出席率が高いグループの方が平均スコアが高い傾向にあります。")

            with tab3:
                st.success("✅ 最新の100件を表示中")
                st.dataframe(df, width="stretch")
            
        except Exception as e:
            st.error(f"データ取得・可視化エラー: {e}")
    else:
        st.info("GCP設定が完了すると、ここにダッシュボードが表示されます。")

if __name__ == "__main__":
    main()
