import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config

def generate_report(data, file_path='reports/daily_report.csv'):
    """Genera un reporte de la cantidad total de artículos subidos durante la última semana, especificando la fuente de cada uno."""

    if len(data.columns) < 3:
        raise ValueError("El archivo CSV no tiene suficientes columnas para calcular el conteo de artículos.")

    # Renombrar columnas si es necesario
    data.columns = ['date', 'source', 'articles_count']

    # Agrupar los datos por fecha y fuente
    daily_data = data.groupby(['date', 'source'])['articles_count'].sum().reset_index()

    # Tomar los últimos 7 días
    weekly_data = daily_data[daily_data['date'].isin(daily_data['date'].unique()[-7:])]
    weekly_data.to_csv(file_path, index=False)

    # Calcular el promedio total de artículos por día
    total_articles_per_day = daily_data.groupby('date')['articles_count'].sum().reset_index()
    average = total_articles_per_day['articles_count'].mean()
    threshold = average * 0.8  # Umbral del 80% del promedio

    # Verificar el conteo del último día (total de todas las fuentes)
    last_day_data = total_articles_per_day.iloc[-1]
    last_day_count = last_day_data['articles_count']

    # Si el conteo del último día es menor al umbral, enviar alerta
    if last_day_count < threshold:
        send_email_alert(last_day_count, threshold)

    return weekly_data

def send_email_alert(last_day_count, threshold):
    """Envía un correo de alerta si la cantidad de artículos está por debajo del umbral."""
    email_host = config('EMAIL_HOST')
    email_port = config('EMAIL_PORT')
    sender_email = config('EMAIL_SENDER')
    sender_password = config('EMAIL_PASSWORD')
    recipient_email = config('EMAIL_RECIPIENT')

    subject = "Alerta: Conteo de artículos bajo"
    body = f"Alerta: La cantidad de artículos subidos ({last_day_count}) está por debajo del umbral esperado ({threshold})."

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(email_host, email_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        print("Correo de alerta enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
