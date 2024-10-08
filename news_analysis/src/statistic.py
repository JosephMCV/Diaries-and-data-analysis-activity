import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_alert_email(current_articles, mean_articles, threshold, diary):
    """Envía un correo electrónico de alerta cuando el número de artículos está por debajo del umbral."""
    
    sender_email = "contreras.joseph.7630@eam.edu.co"  # Cambia a tu correo electrónico
    receiver_email = "contreras.joseph.7630@eam.edu.co"
    password = ""  # Cambia a tu contraseña de correo

    # Crear el mensaje
    subject = f"Alerta: Artículos bajos para el diario {diary}"
    body = (f"Alerta: El diario {diary} ha subido {current_articles} artículos, "
            f"por debajo del umbral del 80% del promedio ({threshold:.2f}).")
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Enviar el correo
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Cambia a tu servidor SMTP
            server.starttls()  # Inicia la conexión segura
            server.login(sender_email, password)
            server.send_message(msg)
            print("Correo de alerta enviado.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

def calculate_statistics(data, diary, current_articles):
    """Calcula estadísticas y verifica si los artículos actuales están por debajo del umbral de 80%, aplicando el modelo estadístico."""

    # Día de la semana actual (ejemplo: jueves)
    current_weekday = datetime.now().weekday()
    current_weekday_str = datetime.now().strftime('%A')

    # Filtrar datos de los últimos 6 meses, el día de la semana actual y el diario especificado
    six_months_ago = datetime.now() - timedelta(days=180)
    filtered_data = data[
        (pd.to_datetime(data['date']) >= six_months_ago) &
        (pd.to_datetime(data['date']).dt.weekday == current_weekday) &
        (data['diary'] == diary)
    ]

    if filtered_data.empty:
        return {
            "message": f"No hay datos disponibles para los últimos 6 meses en los días {current_weekday_str} para el diario {diary}.",
            "mean_articles": 0,
            "std_articles": 0,
            "coefficient_of_variation": 0,
            "alert": False
        }

    # Calcular las estadísticas
    mean_articles = filtered_data['articles'].mean()
    std_articles = filtered_data['articles'].std()
    coefficient_of_variation = std_articles / mean_articles if mean_articles != 0 else 0

    # Calcular el umbral del 80% del promedio
    threshold = mean_articles * 0.8
    below_threshold = current_articles < threshold

    # Fase 1: Si está por debajo del 80% del promedio
    if below_threshold:
        message = f"El diario {diary} ha subido {current_articles} artículos, por debajo del 80% del promedio ({threshold:.2f}) de los últimos 6 meses en los días {current_weekday_str}."

        # Enviar correo de alerta
        send_alert_email(current_articles, mean_articles, threshold, diary)

        # Fase 2: Coeficiente de variación
        if coefficient_of_variation > 0.2:  # Alta variabilidad (umbral arbitrario)
            # Calcular cuartiles
            q1 = filtered_data['articles'].quantile(0.25)
            q3 = filtered_data['articles'].quantile(0.75)
            iqr = q3 - q1  # Rango intercuartílico
            if current_articles < q1 or current_articles > q3 + 1.5 * iqr:
                return {
                    "message": message + " Además, la cantidad de artículos está fuera del rango intercuartílico.",
                    "count_message": f"Se utilizaron {len(filtered_data)} días para el cálculo.",
                    "mean_articles": mean_articles,
                    "std_articles": std_articles,
                    "coefficient_of_variation": coefficient_of_variation,
                    "alert": True,  # Genera alerta
                    "detailed_info": filtered_data[['date', 'articles']].to_dict('records')
                }
            else:
                message += " Sin embargo, la cantidad de artículos está dentro del rango intercuartílico."
        else:
            # Fase 3: Baja variabilidad - Verificar distribución de frecuencias
            freq_table = filtered_data['articles'].value_counts()
            most_frequent_value = freq_table.idxmax()
            if current_articles != most_frequent_value:
                return {
                    "message": message + f" Además, la cantidad de artículos no coincide con el valor más frecuente ({most_frequent_value}).",
                    "count_message": f"Se utilizaron {len(filtered_data)} días para el cálculo.",
                    "mean_articles": mean_articles,
                    "std_articles": std_articles,
                    "coefficient_of_variation": coefficient_of_variation,
                    "alert": True,  # Genera alerta
                    "detailed_info": filtered_data[['date', 'articles']].to_dict('records')
                }
            else:
                message += f" Sin embargo, la cantidad de artículos coincide con el valor más frecuente ({most_frequent_value})."
    else:
        message = f"El diario {diary} ha subido {current_articles} artículos, lo cual está por encima del umbral del 80% ({threshold:.2f}). No se requiere alerta."

    return {
        "message": message,
        "count_message": f"Se utilizaron {len(filtered_data)} días para el cálculo.",
        "mean_articles": mean_articles,
        "std_articles": std_articles,
        "coefficient_of_variation": coefficient_of_variation,
        "alert": False,  # No genera alerta
        "detailed_info": filtered_data[['date', 'articles']].to_dict('records')
    }
