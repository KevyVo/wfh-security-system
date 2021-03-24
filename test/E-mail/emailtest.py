import mail_lib

file = open("users.txt", "r")

recevier ="recevier@mail.com"
user = file.readline().rstrip("\n")
sender=(user.split(";")[0])
pas=(user.split(";")[1])
print(sender,pas)

m = mail_lib.mail(sender, pas)

m.sendItem(recevier, "With Image", "Body example", "bobrosspainting.jpg")

m.sendMessage(recevier, "Only Message", "Yes dun yes")