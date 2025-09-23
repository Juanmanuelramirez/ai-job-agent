import boto3

def create_dynamodb_table(dynamodb_client, table_name, key_schema, attribute_definitions):
    """Función genérica para crear una tabla de DynamoDB."""
    print(f"Creando la tabla '{table_name}'...")
    try:
        table = dynamodb_client.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        table.wait_until_exists()
        print(f"¡Tabla '{table_name}' creada exitosamente!")
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f"La tabla '{table_name}' ya existe.")
    except Exception as e:
        print(f"Error al crear la tabla '{table_name}': {e}")

if __name__ == '__main__':
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    # Tabla de Configuración de Usuarios
    create_dynamodb_table(dynamodb, 'UserSettings',
        [{'AttributeName': 'email', 'KeyType': 'HASH'}],
        [{'AttributeName': 'email', 'AttributeType': 'S'}]
    )
    
    # Tabla de Vacantes Encontradas
    create_dynamodb_table(dynamodb, 'JobLeads',
        [{'AttributeName': 'userEmail', 'KeyType': 'HASH'}, {'AttributeName': 'jobUrl', 'KeyType': 'RANGE'}],
        [{'AttributeName': 'userEmail', 'AttributeType': 'S'}, {'AttributeName': 'jobUrl', 'AttributeType': 'S'}]
    )
