import boto3

# Get the service resource.
dynamodb = boto3.resource('dynamodb')

# Create the DynamoDB table.
table = dynamodb.create_table(
    TableName='Users',
    KeySchema=[
        {
            'AttributeName': 'username',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'last_name',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'username',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'last_name',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

table = dynamodb.Table('Users')
# Wait until the table exists.
table.meta.client.get_waiter('table_exists').wait(TableName='Users')

# Print out some data about the table.
print(table.item_count)

print(table.creation_date_time)

username = "Edenwon"
first = "Eden"
last = ""
age = 21
account = "standard"

table.put_item(
   Item={
        'username': username,
        'first_name': first,
        'last_name': last,
        'age': age,
        'account_type': account,
    }
)

response = table.get_item(
    Key={
        'username': username,
        'last_name': last
    }
)
item = response['Item']
print(item)
