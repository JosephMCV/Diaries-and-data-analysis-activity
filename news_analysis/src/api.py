from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.data_loader import load_data, save_data
from src.statistic import calculate_statistics
from src.report_generator import generate_report
from datetime import datetime
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

# Lista de diarios permitidos
VALID_DIARIES = ["The Daily News", "Global Times", "Morning Star"]

def send_alert_email(recipient, subject, message):
    sender_email = "tu_correo@gmail.com"  # Cambia esto a tu correo
    sender_password = "tu_contraseña"  # Cambia esto a tu contraseña

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject

    # Agregar el cuerpo del mensaje
    msg.attach(MIMEText(message, 'plain'))

    try:
        # Conectar al servidor SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Iniciar TLS
            server.login(sender_email, sender_password)  # Iniciar sesión
            server.send_message(msg)  # Enviar el mensaje
        print("Correo electrónico enviado.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


# Modelo para la entrada del usuario
class ArticleInput(BaseModel):
    diary: str
    articles: int

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de análisis de noticias"}

@app.get("/articles/")
def get_articles():
    """Endpoint para obtener todos los artículos cargados"""
    data = load_data("data/articles_data.csv")
    return {"articles": data.to_dict()}

@app.post("/articles/report/")
def get_report():
    """Endpoint para obtener el reporte de artículos subidos"""
    data = load_data("data/articles_data.csv")
    report = generate_report(data)
    return {"report": report.to_dict()}

@app.post("/statistics/")
def get_statistics(input_data: ArticleInput):
    """Endpoint para obtener estadísticas basado en el diario y la cantidad de artículos ingresados"""
    
    # Validar si el diario es válido
    if input_data.diary not in VALID_DIARIES:
        raise HTTPException(status_code=400, detail="Diario no válido. Elija uno de los siguientes: 'The Daily News', 'Global Times', 'Morning Star'.")

    # Cargar los datos actuales
    data = load_data("data/articles_data.csv")

    # Registrar los artículos para el día actual
    current_date = datetime.now().strftime('%Y-%m-%d')
    new_entry = pd.DataFrame([{"date": current_date, "diary": input_data.diary, "articles": input_data.articles}])
    
    # Agregar la nueva entrada a los datos
    data = pd.concat([data, new_entry], ignore_index=True)
    
    # Guardar los datos actualizados en el CSV
    save_data("data/articles_data.csv", data)

    # Filtrar los datos para el diario actual y el día de la semana actual (por ejemplo, todos los jueves)
    statistics = calculate_statistics(data, input_data.diary, input_data.articles)

    return statistics
