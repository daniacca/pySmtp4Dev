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

server = smtplib.SMTP('localhost', 2525)
server.set_debuglevel(True) # show communication with the server
#server.starttls()
try:
    server.sendmail(me, [you], msg.as_string())
finally:
    server.quit()