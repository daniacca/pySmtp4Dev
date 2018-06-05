import smtplib
from smtp_utils import ssl_certificate_helper
from email.mime.text import MIMEText

# Create the message
msg = MIMEText('This is the body of the message.')
me = 'Jon@MacBookPro.com'
you = 'jon.drowell@yahoo.com'

msg['Subject'] = 'The contents of the log file'
msg['From'] = me
msg['To'] = you

server = smtplib.SMTP('127.0.0.1', 2525)
#server.starttls(context=ssl_certificate_helper.create_self_signed_cert())
server.set_debuglevel(True) # show communication with the server
try:
    server.sendmail(me, [you], msg.as_string())
finally:
    server.quit()