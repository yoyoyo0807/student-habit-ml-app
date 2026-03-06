import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
from google.cloud import bigquery

def train_and_save_model():
    # 認証設定（app.pyと共通）
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "concise-booking-473310-a0-49cbb2545f4a.json"
    client = bigquery.Client()

    # データ取得
    query = "SELECT * FROM `concise-booking-473310-a0.student_data.habits_performance`"
    df = client.query(query).to_dataframe()

    # 前処理: カテゴリ変数を数値に変換
    df['gender'] = df['gender'].map({'Male': 0, 'Female': 1})
    
    # 特徴量とターゲットの選択
    features = ['study_hours_per_day', 'sleep_hours', 'social_media_hours', 'attendance_percentage']
    X = df[features]
    y = df['exam_score']

    # モデル学習
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # 保存
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/student_model.pkl')
    print("Model trained and saved to models/student_model.pkl")

if __name__ == "__main__":
    train_and_save_model()
