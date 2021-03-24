import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime


def query_movies(date, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('Movies2')
    response = table.query(
        KeyConditionExpression=Key('date').eq(date),
        ScanIndexForward=False
    )
    return response['Items']


if __name__ == '__main__':
    now = datetime.now()
    date = str(now.date())
    print(f"Movies from {date}")
    movies = query_movies(date)
    for movie in movies:
        print(movie['date'], ":", movie['unix'])
