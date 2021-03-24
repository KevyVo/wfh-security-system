import boto3
from boto3.dynamodb.conditions import Key

d = boto3.resource('dynamodb')

table = d.Table('test1')

res = table.query(KeyConditionExpression=Key('user').eq(user))

print(res['Items'])