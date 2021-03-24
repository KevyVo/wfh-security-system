import boto3

class db(object):
    #Construter will take in listName that is already exsiting table or create a new table 
    def __init__(self, listName):
        self.dynamodb = boto3.resource('dynamodb')
        self.listName = listName
        if (self.checkTable()==False):
            self.table = self.dynamodb.Table(self.listName) 
            print("The table " + self.listName + " just got created at: " + str(self.table.creation_date_time) + " and has " + str(self.table.item_count) + " items.")
        else:
            self.table = self.dynamodb.Table(self.listName) 
            print("The table " + self.listName + " already exist and has " + str(self.table.item_count) + " items.")
            
    # Query client and list_tables to see if table exists or not
    def checkTable(self):
        # Instantiate your dynamo client object
        client = boto3.client('dynamodb')

        # Get an array of table names associated with the current account and endpoint.
        response = client.list_tables()

        if self.listName in response['TableNames']:
            table_found = True
        else:
            table_found = False
            # Get the service resource.
            dynamodb = boto3.resource('dynamodb')

            # Create the DynamoDB table called followers
            table = dynamodb.create_table(
                TableName = self.listName,
                KeySchema =
                [
                    {
                        'AttributeName': 'username',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'last_name',
                        'KeyType': 'RANGE'
                    }
                ],
                AttributeDefinitions =
                [
                    {
                        'AttributeName': 'username',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'last_name',
                        'AttributeType': 'S'
                    },
                ],
                ProvisionedThroughput =
                {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )

            # Wait until the table exists.
            table.meta.client.get_waiter('table_exists').wait(TableName=self.listName)

        return table_found

    def appendItem(self, username, first, last, age, account):
        self.table.put_item(
            Item={
                'username': username,
                'first_name': first,
                'last_name': last,
                'age': age,
                'account_type': account,
            }
        )
        print("The item has been appended with username: " + username)

    def updateItem(self, username, last, updateExp, expAtt):
        self.table.update_item(
            Key={
                'username': username,
                'last_name': last
            },
            UpdateExpression= updateExp,
            ExpressionAttributeValues= {expAtt}
            )
        print("The item " + username + " has been updated")
        

    def getItem(self, username, last):
        response = self.table.get_item(
            Key={
                'username': username,
                'last_name': last
            }
        )
        item = response['Item']
        print("The item username: ", item)

    def deleteItem(self, username, last):
        self.table.delete_item(
            Key={
                'username': username,
                'last_name': last
            }
        )
        print("User: " + username + " has been deleted.")

    def deleteTable(self):
        self.table.delete()
        print("Table " + self.listName + " has been deleted.")
        
