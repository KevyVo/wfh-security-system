import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


receiver = "recevier@mail.com"
subject = "Test1"

file = open("users.txt","r")


user=ID = file.readline().rstrip("\n")
sender=(user.split(";")[0])
pas=(user.split(";")[1])
print(sender,pas)

msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = receiver
msg['Subject'] = subject

body = 'Hi there, sending this email from Python!'
msg.attach(MIMEText(body,'plain'))

filename="bobrosspainting.jpg"
attachment  =open(filename,'rb')

part = MIMEBase('application','octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition',"attachment; filename= "+filename)

msg.attach(part)
text = msg.as_string()
server = smtplib.SMTP('smtp.gmail.com: 587')
server.starttls()
server.login(sender,pas)


server.sendmail(sender,receiver,text)
server.quit()
