import boto3
import os
from boto3.dynamodb.conditions import Key

# --- Configuración ---
JOB_LEADS_TABLE = os.environ.get('JOB_LEADS_TABLE_NAME', 'JobLeads')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'tu-correo-verificado-en-ses@example.com')

# Inicializar clientes de AWS.
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
table = dynamodb.Table(JOB_LEADS_TABLE)

def generate_html_email(user_email, top_jobs):
    """Genera el contenido HTML del correo de informe."""
    body_html = f"<html><body><h1>Hola {user_email.split('@')[0]},</h1>"
    body_html += "<p>Tu agente de IA ha analizado el mercado. Aquí están las mejores oportunidades para ti hoy:</p>"
    
    for job in top_jobs:
        body_html += f"<hr><h2>{job.get('title', 'Sin Título')} @ {job.get('company', 'Sin Compañía')}</h2>"
        body_html += f"<p><b>URL Validada:</b> <a href='{job['jobUrl']}'>{job['jobUrl']}</a></p>"
        body_html += f"<p><b>Puntuación de Relevancia:</b> {job.get('relevanceScore', 'N/A')}%</p>"
        body_html += "<h3>Análisis de IA:</h3>"
        # Formatear el análisis de IA para HTML.
        analysis_html = job.get('aiAnalysis', 'No disponible.').replace('\n', '<br>')
        body_html += f"<div style='background-color:#f0f0f0; padding:10px; border-radius:5px;'>{analysis_html}</div>"

    body_html += "<br><p>¡Mucha suerte con tus aplicaciones!</p></body></html>"
    return body_html

def lambda_handler(event, context):
    """
    Handler principal. Puede ser invocado por el orquestador al final del día.
    """
    user_email = event.get('user_email')
    if not user_email:
        return {'statusCode': 400, 'body': 'Falta el correo del usuario.'}
        
    print(f"Preparando informe para: {user_email}")

    # 1. Consultar DynamoDB para obtener las mejores vacantes para el usuario.
    try:
        response = table.query(
            KeyConditionExpression=Key('userEmail').eq(user_email),
            # Ordenar por puntuación de relevancia de mayor a menor.
            ScanIndexForward=False, 
            # Limitamos a las 5 mejores.
            Limit=5 
            # Se necesitaría un Índice Secundario Global en 'relevanceScore' para ordenar así.
            # Por simplicidad, aquí obtenemos los últimos 5 y los ordenamos en Python.
        )
        top_jobs = sorted(response.get('Items', []), key=lambda x: x.get('relevanceScore', 0), reverse=True)
    except Exception as e:
        print(f"Error al consultar DynamoDB: {e}")
        return {'statusCode': 500, 'body': 'Error de base de datos.'}

    if not top_jobs:
        print(f"No se encontraron vacantes de alta relevancia para {user_email}. No se enviará correo.")
        return {'statusCode': 200, 'body': 'No hay informe que enviar.'}

    # 2. Generar y enviar el correo.
    email_html = generate_html_email(user_email, top_jobs)
    
    try:
        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [user_email]},
            Message={
                'Subject': {'Data': 'Tu Informe Diario de Empleo con IA'},
                'Body': {'Html': {'Data': email_html}}
            }
        )
        print(f"Correo de informe enviado exitosamente a {user_email}.")
    except Exception as e:
        print(f"Error al enviar correo con SES: {e}")
        return {'statusCode': 500, 'body': 'Error al enviar correo.'}

    return {'statusCode': 200, 'body': 'Informe enviado.'}
