import smtplib
from config import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template


def getTemplate(fileName):
    with open(fileName) as f:
        content = f.read()
    return Template(content)

def sendPin(fromAcad,dest, pin):
    template = getTemplate("pinMailTemplate.txt")
    message = template.substitute(INIT_ACADEMY=fromAcad,LAB_PIN=pin)
    s = smtplib.SMTP(host=config['SMTP_SRV'], port=config['SMTP_PORT'])
    s.starttls()
    s.login(user=config['SMTP_USER'], password=config['SMTP_PASS'])
    msg = MIMEMultipart()
    msg['from'] = config['SMTP_FROM']
    msg['to'] = dest
    msg['subject'] = "You are invited to a new lab!"

    msg.attach(MIMEText(message, 'plain'))
    s.send_message(msg)
    del msg

if __name__ == "__main__":
    sendPin("yannick","furest@furest.be", 123456789)
