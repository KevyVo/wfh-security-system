import db_lib
import boto3

testa = db_lib.db("Users")




testa.appendItem("Kevin`s Index", 0, "Kevin", "vo", "Index", "Admin")
testa.appendItem("Kevin`s Thumb", 1, "Kevin", "Vo", "Thumb", "Admin")
testa.appendItem("Eden`s Index", 2, "Eden", "last", "Index", "Standard")

kev = testa.getItem(0)

print(kev["userID"])

