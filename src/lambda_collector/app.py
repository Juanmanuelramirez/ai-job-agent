import json
import boto3
import requests # Necesitarás esta librería para validar URLs.

# --- Configuración ---
# En una aplicación de producción, estos nombres de tabla y bucket vendrían de variables de entorno.
USER_SETTINGS_TABLE = 'UserSettings'
RAW_JOBS_BUCKET = 'ai-job-agent-raw-jobs' # Un nuevo bucket para guardar las vacantes encontradas.

# Inicializar clientes de AWS fuera del handler.
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table = dynamodb.Table(USER_SETTINGS_TABLE)

def get_user_settings(email):
    """Obtiene la configuración del usuario desde DynamoDB."""
    try:
        response = table.get_item(Key={'email': email})
        return response.get('Item')
    except Exception as e:
        print(f"Error al obtener la configuración para {email}: {e}")
        return None

def search_jobs_simulation(platforms):
    """
    Simula una búsqueda en las plataformas seleccionadas y devuelve una lista de vacantes.
    En una aplicación real, aquí se conectaría a una API de empleos.
    """
    # Pool de vacantes de ejemplo para la simulación.
    job_pool = [
        {"url": "https://www.linkedin.com/jobs/view/3920112345/", "description": "Senior Data Architect at Stripe...", "source": "LinkedIn"},
        {"url": "https://www.occ.com.mx/empleo/oferta/12345678/", "description": "Arquitecto de Datos Cloud en Softtek...", "source": "OCC Mundial"},
        {"url": "https://www.linkedin.com/jobs/view/link-roto-123/", "description": "Esta vacante ya no existe...", "source": "LinkedIn"},
        {"url": "https://www.computrabajo.com.mx/ofertas-de-trabajo/oferta-de-trabajo-de-12345", "description": "Sr. Solutions Architect en Globant...", "source": "Computrabajo"}
    ]
    
    # Filtrar solo de las plataformas que el usuario seleccionó.
    return [job for job in job_pool if job['source'].lower().replace(" ", "") in platforms]

def validate_url(url):
    """
    Valida que una URL esté activa y no devuelva un error.
    Devuelve True si la URL es válida, False si no lo es.
    """
    try:
        # Usamos un timeout para no esperar demasiado por una respuesta.
        response = requests.head(url, allow_redirects=True, timeout=5)
        # Consideramos válida cualquier respuesta que no sea un error del cliente o del servidor (4xx o 5xx).
        if response.status_code < 400:
            print(f"URL VÁLIDA: {url} (Status: {response.status_code})")
            return True
        else:
            print(f"URL ROTA: {url} (Status: {response.status_code})")
            return False
    except requests.RequestException as e:
        print(f"Error de conexión al validar URL {url}: {e}")
        return False

def lambda_handler(event, context):
    """
    Handler principal para la Lambda Colectora.
    """
    user_email = event.get('user_email')
    if not user_email:
        return {'statusCode': 400, 'body': 'Falta el correo del usuario.'}
        
    print(f"Iniciando recolección para: {user_email}")
    
    # 1. Obtener la configuración del usuario.
    settings = get_user_settings(user_email)
    if not settings:
        return {'statusCode': 404, 'body': f'No se encontró la configuración para {user_email}.'}
    
    platforms_to_search = settings.get('platforms', [])
    
    # 2. Buscar vacantes.
    found_jobs = search_jobs_simulation(platforms_to_search)
    print(f"Se encontraron {len(found_jobs)} vacantes potenciales.")
    
    # 3. Validar URLs y guardar en S3 para la siguiente fase.
    valid_jobs_count = 0
    for job in found_jobs:
        if validate_url(job['url']):
            # La URL es válida, la guardamos en S3 para que la Lambda Analizadora la procese.
            s3_key = f"{user_email}/{context.aws_request_id}-{job['source']}.json"
            s3.put_object(
                Bucket=RAW_JOBS_BUCKET,
                Key=s3_key,
                Body=json.dumps(job)
            )
            valid_jobs_count += 1
            
    print(f"Proceso completado. Se guardaron {valid_jobs_count} vacantes válidas para análisis.")
    return {'statusCode': 200, 'body': f'Se encontraron y validaron {valid_jobs_count} vacantes.'}
