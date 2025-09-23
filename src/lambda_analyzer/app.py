import json
import boto3
import os

# --- Configuración ---
# Obtener nombres de recursos desde variables de entorno (mejor práctica).
CV_BUCKET = os.environ.get('CV_BUCKET_NAME', 'ai-job-agent-cvs')
JOB_LEADS_TABLE = os.environ.get('JOB_LEADS_TABLE_NAME', 'JobLeads')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-v2')

# Inicializar clientes de AWS.
s3 = boto3.client('s3')
comprehend = boto3.client('comprehend')
bedrock = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(JOB_LEADS_TABLE)

def get_cv_summary(s3_path):
    """En un sistema real, leería el PDF y lo resumiría. Aquí simulamos el resumen."""
    # Simulación del resumen del CV para el prompt de Bedrock.
    return """
    Strategic Program Manager and AWS Certified Solutions Architect with 10+ years of experience. 
    Expertise in Data Governance, CI/CD, AWS (SQS, S3, DynamoDB), GCP, FinTech, and Agile (SAFe).
    """

def analyze_with_bedrock(cv_summary, job_description, language):
    """Genera un resumen y un mensaje de contacto usando Amazon Bedrock."""
    prompt = f"""
    Human: You are a career coach AI. Based on my professional summary and the following job description, please perform two tasks in the language '{language}':
    1. Summarize the job in three bullet points from my perspective.
    2. Draft a concise, professional outreach paragraph for the recruiter.

    My Professional Summary:
    {cv_summary}

    Job Description:
    {job_description}

    Assistant:
    """
    
    body = json.dumps({"prompt": prompt, "max_tokens_to_sample": 500})
    
    try:
        response = bedrock.invoke_model(body=body, modelId=BEDROCK_MODEL_ID)
        response_body = json.loads(response.get('body').read())
        return response_body.get('completion')
    except Exception as e:
        print(f"Error al invocar Bedrock: {e}")
        return "Error al generar contenido de IA."

def lambda_handler(event, context):
    """
    Handler principal. Se activa por un evento de S3 (cuando se crea un nuevo archivo de vacante).
    """
    # 1. Obtener información del evento S3.
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    
    user_email = key.split('/')[0] # El email está en la ruta del archivo.
    
    # 2. Leer el archivo de la vacante desde S3.
    job_object = s3.get_object(Bucket=bucket, Key=key)
    job_data = json.loads(job_object['Body'].read().decode('utf-8'))
    job_description = job_data['description']
    
    # 3. Obtener el CV del usuario y analizar con IA.
    # (Obteniendo la ruta del CV desde la tabla UserSettings)
    cv_summary = get_cv_summary(f"s3://{CV_BUCKET}/{user_email}/cv.pdf")
    # (Obteniendo el idioma desde la tabla UserSettings)
    language_pref = 'es' # Simulación
    
    ai_generated_content = analyze_with_bedrock(cv_summary, job_description, language_pref)
    
    # 4. (Opcional) Usar Comprehend para extraer habilidades y puntuar.
    
    # 5. Guardar los resultados enriquecidos en DynamoDB.
    try:
        table.put_item(
            Item={
                'userEmail': user_email,
                'jobUrl': job_data['url'],
                'source': job_data['source'],
                'description': job_description,
                'aiAnalysis': ai_generated_content,
                'relevanceScore': 90 # Simulación de la puntuación
            }
        )
        print(f"Análisis de {job_data['url']} para {user_email} guardado en DynamoDB.")
    except Exception as e:
        print(f"Error al guardar en DynamoDB: {e}")
        
    return {'statusCode': 200, 'body': 'Análisis completado.'}
