import smtplib
from email.mime.text import MIMEText

# Create the message
msg = MIMEText('This is the body of the message.')
me = 'Jon@MacBookPro.com'
you = 'jon.drowell@yahoo'

msg['Subject'] = 'The contents of the log file'
msg['From'] = me
msg['To'] = you

server = smtplib.SMTP('localhost', 2525)
server.set_debuglevel(True) # show communication with the server
server.starttls()

try:
    server.sendmail(me, [you], msg.as_string())
finally:
    server.quit()