# src/report_generator.py
import pandas as pd

def generate_report(data, file_path='reports/daily_report.csv'):
    """Genera un reporte de la cantidad de artículos subidos durante la última semana."""
    weekly_data = data.tail(7)
    weekly_data.to_csv(file_path, index=False)
    return weekly_data