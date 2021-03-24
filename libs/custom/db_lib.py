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

            # Create the DynamoDB table by the name passed in by the parameter
            table = dynamodb.create_table(
                TableName = self.listName,
                KeySchema =
                [
                    {
                        'AttributeName': 'templateID',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions =
                [
                    {
                        'AttributeName': 'templateID',
                        'AttributeType': 'N'
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

    def appendItem(self, userID, templateID, first, last, finger, account):
        self.table.put_item(
            Item={
                'userID': userID,
                'templateID' : templateID,
                'first_name': first,
                'last_name': last,
                'finger': finger,
                'account_type': account,
            }
        )
        print("The item has been appended with username: " + userID)

    def updateItem(self, userID, last, updateExp, expAtt):
        self.table.update_item(
            Key={
                'userID': userID,
                'last_name': last
            },
            UpdateExpression= updateExp,
            ExpressionAttributeValues= {expAtt}
            )
        print("The item " + userID + " has been updated")
        

    def getItem(self, templateID):
        response = self.table.get_item(
            Key={
                'templateID': templateID
            }
        )
        item = response['Item']
        return item

    def deleteItem(self, userID, templateID):
        self.table.delete_item(
            Key={
                'userID': userID,
                'templateID': templateID
            }
        )
        print("User: " + userID + " has been deleted.")

    def deleteTable(self):
        self.table.delete()
        print("Table " + self.listName + " has been deleted.")
        
