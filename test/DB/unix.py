import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

#Complete the query table, in acsending order

def query_dates(date, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('SmartLogs')
    response = table.query(
        KeyConditionExpression=Key('date').eq(date),
        ScanIndexForward=False
    )
    return response['Items']


if __name__ == '__main__':
    now = datetime.now()
    date = str(now.date())
    print(f"Dates from {date}")
    logs = query_dates(date)
    for event in logs:
        print(event['date'], ":", event['unix'])
