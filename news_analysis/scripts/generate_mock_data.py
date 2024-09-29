# scripts/generate_mock_data.py
import pandas as pd
import random
from datetime import datetime, timedelta

def generate_mock_data(file_path, days=180):
    """Genera datos simulados de artículos subidos por varios diarios durante un periodo."""
    start_date = datetime.now() - timedelta(days=days)
    dates = [start_date + timedelta(days=i) for i in range(days)]

    data = []
    diaries = ["The Daily News", "Global Times", "Morning Star"]
    
    for date in dates:
        for diary in diaries:
            articles = random.randint(70, 120)
            data.append([date.strftime("%Y-%m-%d"), diary, articles])
    
    df = pd.DataFrame(data, columns=["date", "diary", "articles"])
    df.to_csv(file_path, index=False)

# Ejecutar la generación de datos
if __name__ == "__main__":
    generate_mock_data("data/articles_data.csv")
