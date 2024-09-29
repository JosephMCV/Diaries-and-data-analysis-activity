# src/api.py
from fastapi import FastAPI
from src.data_loader import load_data
from src.statistic import calculate_statistics
from src.report_generator import generate_report

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de análisis de noticias"}

@app.get("/articles/")
def get_articles():
    """Endpoint para obtener todos los artículos cargados"""
    data = load_data("data/articles_data.csv")
    return {"articles": data.to_dict()}

@app.get("/articles/report/")
def get_report():
    """Endpoint para obtener el reporte de artículos subidos"""
    data = load_data("data/articles_data.csv")
    report = generate_report(data)
    return {"report": report.to_dict()}

@app.get("/statistics/")
def get_statistics():
    """Endpoint para obtener las estadísticas actuales"""
    data = load_data("data/articles_data.csv")
    stats = calculate_statistics(data)
    return {"statistics": stats}