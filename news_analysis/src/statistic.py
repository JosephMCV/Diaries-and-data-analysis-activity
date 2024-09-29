# src/statistics.py
import numpy as np

def calculate_statistics(data):
    """Calcula estadísticas como el promedio y el coeficiente de variación."""
    mean_articles = data['articles'].mean()
    std_articles = data['articles'].std()
    coefficient_of_variation = std_articles / mean_articles if mean_articles != 0 else 0
    
    return {
        "mean_articles": mean_articles,
        "std_articles": std_articles,
        "coefficient_of_variation": coefficient_of_variation
    }

def is_below_threshold(current_value, mean_value, threshold_percentage=0.8):
    """Verifica si el valor actual está por debajo del umbral."""
    threshold = mean_value * threshold_percentage
    return current_value < threshold