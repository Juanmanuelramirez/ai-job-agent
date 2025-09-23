import boto3

def create_table_if_not_exists(dynamodb_client, table_name, key_schema, attribute_definitions, global_secondary_indexes=None):
    """
    Creates a DynamoDB table if it doesn't already exist.
    Includes support for Global Secondary Indexes (GSI).
    """
    print(f"Checking for table '{table_name}'...")
    try:
        table_params = {
            'TableName': table_name,
            'KeySchema': key_schema,
            'AttributeDefinitions': attribute_definitions,
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        }
        if global_secondary_indexes:
            table_params['GlobalSecondaryIndexes'] = global_secondary_indexes

        table = dynamodb_client.create_table(**table_params)
        table.wait_until_exists()
        print(f"Success! Table '{table_name}' created.")
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f"Table '{table_name}' already exists. No action taken.")
    except Exception as e:
        print(f"Error creating table '{table_name}': {e}")

if __name__ == '__main__':
    # It's a good practice to specify the region.
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1') 

    # 1. UserSettings Table
    create_table_if_not_exists(dynamodb, 'UserSettings',
        key_schema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
        attribute_definitions=[{'AttributeName': 'email', 'AttributeType': 'S'}]
    )

    # 2. JobLeads Table with the crucial Global Secondary Index (GSI)
    create_table_if_not_exists(dynamodb, 'JobLeads',
        key_schema=[
            {'AttributeName': 'userEmail', 'KeyType': 'HASH'},
            {'AttributeName': 'jobUrl', 'KeyType': 'RANGE'}
        ],
        attribute_definitions=[
            {'AttributeName': 'userEmail', 'AttributeType': 'S'},
            {'AttributeName': 'jobUrl', 'AttributeType': 'S'},
            {'AttributeName': 'relevanceScore', 'AttributeType': 'N'} # 'N' for Number
        ],
        global_secondary_indexes=[
            {
                'IndexName': 'RelevanceScoreIndex',
                'KeySchema': [
                    {'AttributeName': 'userEmail', 'KeyType': 'HASH'},
                    {'AttributeName': 'relevanceScore', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            }
        ]
    )

