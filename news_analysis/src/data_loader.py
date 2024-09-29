# src/data_loader.py
import pandas as pd

def load_data(file_path):
    """Carga los datos desde un archivo CSV."""
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return None