import db_lib
import boto3

testa = db_lib.db("Users")




testa.appendItem("Eden`s Thumb", 3, "Thumb", "last", "Index", "Standard")

kev = testa.getItem(0)

print(kev["userID"])

