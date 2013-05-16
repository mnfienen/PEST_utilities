#uberPEST - PEST running and notification

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from os.path import exists
import os


def mail(to, subject, text, gmail_user, gmail_pwd, attach=None):
    msg = MIMEMultipart()

    msg['From'] = gmail_user
    msg['To'] = to
    msg['Subject'] = subject


    if attach:
        for file in attach:
            if exists(file):
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(open(file, 'rb').read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', \
                'attachment; filename="%s"' % os.path.basename(file))
                msg.attach(part)
            else:
                text += "\nATTACHMENT - " + attach + " - NOT FOUND.\nDID YOUR POST-PROCESSING FAIL?"
                
    msg.attach(MIMEText(text))
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()

