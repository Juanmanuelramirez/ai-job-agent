import boto3
import os
import json
from boto3.dynamodb.conditions import Key

# Clientes de AWS
ses_client = boto3.client('ses')
dynamodb = boto3.resource('dynamodb')

# Nombres de la tabla y del índice desde las variables de entorno
JOB_LEADS_TABLE_NAME = os.environ.get('JOB_LEADS_TABLE')
USER_SETTINGS_TABLE_NAME = os.environ.get('USER_SETTINGS_TABLE')
# La identidad de correo VERIFICADA desde donde se enviarán los correos
SENDER_EMAIL = os.environ.get('SES_IDENTITY') 

def lambda_handler(event, context):
    """
    Esta función se activa para un usuario específico, obtiene sus 5 mejores vacantes
    y le envía un informe por correo electrónico.
    """
    # El correo del usuario (destinatario) se pasa desde el orquestador
    user_email = event.get('user_email')
    
    if not user_email:
        print("Error: No se proporcionó el correo del usuario.")
        return {'statusCode': 400, 'body': 'user_email es requerido'}
    
    print(f"Preparando informe para el destinatario: {user_email}")
    
    # --- 1. Obtener la configuración del usuario (para el idioma y el nombre) ---
    user_settings_table = dynamodb.Table(USER_SETTINGS_TABLE_NAME)
    try:
        user_settings = user_settings_table.get_item(Key={'email': user_email}).get('Item', {})
        user_name = user_settings.get('fullName', 'Usuario')
        language = user_settings.get('language', 'es') # 'es' por defecto
    except Exception as e:
        print(f"Error al obtener la configuración del usuario: {e}")
        user_name = "Usuario"
        language = "es"

    # --- 2. Obtener las 5 mejores vacantes para ese usuario ---
    job_leads_table = dynamodb.Table(JOB_LEADS_TABLE_NAME)
    try:
        response = job_leads_table.query(
            IndexName='RelevanceScoreIndex',
            KeyConditionExpression=Key('userEmail').eq(user_email),
            ScanIndexForward=False, # Orden descendente (de mayor a menor puntuación)
            Limit=5
        )
        top_jobs = response.get('Items', [])
        
        if not top_jobs:
            print(f"No se encontraron nuevas vacantes para {user_email}. No se enviará correo.")
            return {'statusCode': 200, 'body': 'No hay vacantes para notificar.'}
            
    except Exception as e:
        print(f"Error al consultar las vacantes en DynamoDB: {e}")
        return {'statusCode': 500, 'body': 'Error interno al consultar la base de datos.'}

    # --- 3. Construir el cuerpo del correo ---
    subject, body_html, body_text = build_email_content(top_jobs, user_name, language)

    # --- 4. Enviar el correo usando SES ---
    try:
        RECIPIENT_EMAIL = user_email # El destinatario es el correo del usuario
        
        ses_client.send_email(
            Source=SENDER_EMAIL, # Remitente: el correo verificado del sistema
            Destination={'ToAddresses': [RECIPIENT_EMAIL]}, # Destinatario: el correo del usuario
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Html': {'Data': body_html},
                    'Text': {'Data': body_text}
                }
            }
        )
        print(f"Correo enviado exitosamente a {RECIPIENT_EMAIL} desde {SENDER_EMAIL}")
        return {'statusCode': 200, 'body': 'Correo enviado exitosamente.'}
        
    except Exception as e:
        print(f"Error al enviar el correo con SES: {e}")
        return {'statusCode': 500, 'body': 'Error al enviar el correo.'}

def build_email_content(jobs, user_name, language):
    """
    Construye el contenido del correo en el idioma especificado.
    """
    if language == 'en':
        subject = "Your AI Job Agent Report is Here!"
        greeting = f"Hello {user_name},"
        intro = "Your AI agent has analyzed new job opportunities. Here are the top 5 matches for your profile:"
        footer = "Good luck with your applications!\n- The AI Job Agent Team"
    else: # Español por defecto
        subject = "¡Tu Informe del Agente de IA de Empleo está Listo!"
        greeting = f"Hola {user_name},"
        intro = "Tu agente de IA ha analizado nuevas oportunidades de empleo. Aquí están las 5 mejores que coinciden con tu perfil:"
        footer = "¡Mucha suerte con tus postulaciones!\n- El equipo del Agente de IA"

    # Construir el cuerpo del correo en HTML y texto plano
    body_html = f"<html><body><h2>{greeting}</h2><p>{intro}</p><ul>"
    body_text = f"{greeting}\n\n{intro}\n\n"
    
    for job in jobs:
        title = job.get('title', 'N/A')
        company = job.get('company', 'N/A')
        url = job.get('jobUrl', '#')
        score = job.get('relevanceScore', 0)
        
        body_html += f"<li><b>{title}</b> at {company} (Score: {score}%)<br/><a href='{url}'>View Job</a></li>"
        body_text += f"- {title} at {company} (Puntuación: {score}%)\n  Enlace: {url}\n\n"
        
    body_html += f"</ul><p>{footer.replace(chr(10), '<br/>')}</p></body></html>"
    body_text += footer
    
    return subject, body_html, body_text

