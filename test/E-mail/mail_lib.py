import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class mail:
    def __init__(self, user, pas):
        self.user = user
        self.pas = pas

    def sendItem(self, receiver, subject, body, filename):
        msg = MIMEMultipart()
        msg['From'] = self.user
        msg['To'] = receiver
        msg['Subject'] = subject

        msg.attach(MIMEText(body,'plain'))
        attachment  =open(filename,'rb')

        part = MIMEBase('application','octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',"attachment; filename= "+filename)

        msg.attach(part)
        text = msg.as_string()
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(self.user, self.pas)

        server.sendmail(self.user, receiver, text)
        server.quit()

        print("The Image and message has been sent in the e-mail.")

    def sendMessage(self, receiver, subject, body):
        msg =MIMEMultipart()
        msg['From'] = self.user
        msg['To'] = receiver
        msg['Subject'] = subject

        msg.attach(MIMEText(body,'plain'))

        server = smtplib.SMTP('smtp.gmail.com: 587')

        server.starttls()
        server.login(self.user, self.pas)

        server.sendmail(self.user, receiver, msg.as_string())
        server.quit()

        print("The e-mail has been send with the message.")
