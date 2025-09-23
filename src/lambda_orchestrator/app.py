import boto3
import json

# Inicializar clientes fuera del handler para reutilizar conexiones
dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
user_settings_table = dynamodb.Table('UserSettings')

def lambda_handler(event, context):
    """
    Esta función se ejecuta diariamente.
    Escanea la tabla de usuarios y dispara el proceso de búsqueda para los usuarios activos.
    """
    print("Iniciando el proceso de orquestación diario...")
    
    try:
        # Escanear la tabla para encontrar a todos los usuarios activos
        # En producción, se usaría un enfoque más eficiente para grandes volúmenes.
        response = user_settings_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('isActive').eq(True)
        )
        
        active_users = response.get('Items', [])
        print(f"Se encontraron {len(active_users)} usuarios activos para procesar.")
        
        for user in active_users:
            email = user.get('email')
            if email:
                print(f"Invocando el colector de vacantes para el usuario: {email}")
                # Invocar la siguiente Lambda en la cadena (el Colector) de forma asíncrona
                lambda_client.invoke(
                    FunctionName='CollectorFunction', # Nombre de la siguiente Lambda
                    InvocationType='Event', # Asíncrono
                    Payload=json.dumps({'user_email': email})
                )
                
        return {
            'statusCode': 200,
            'body': json.dumps(f'Proceso iniciado para {len(active_users)} usuarios.')
        }

    except Exception as e:
        print(f"Error en el orquestador: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error durante la orquestación.')
        }
