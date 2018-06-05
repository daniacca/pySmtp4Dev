import os
import collections
from smtp_utils.mail_message import MailMessage
from datetime import datetime


class MessageHandler:
    def __init__(self, file_logging, log_dir, max_email, *args, **kwargs):
        self.emails = collections.deque(maxlen=int(max_email))
        self.email_counter = 0
        self.log_file = file_logging
        try:
            self.logging_directory = os.path.realpath(log_dir)
            if not os.path.exists(self.logging_directory):
                os.makedirs(self.logging_directory)
        except Exception as ex:
            self.logging_directory = os.path.realpath(".")

    async def handle_DATA(self, server, session, envelope):
        if self.log_file:
            f = None
            try:
                filename = '%s-%d.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'), self.email_counter)
                filepath = os.path.join(self.logging_directory, filename)
                f = open(filepath, 'w')
                f.write(envelope.content.decode('utf8', errors='replace'))
            except Exception:
                print('Error on saving email to file...')
            finally:
                if f:
                    f.close
        self.emails.append(MailMessage(session.peer, envelope.mail_from, envelope.rcpt_tos, envelope.content))
        self.email_counter += 1
        return '250 Message accepted for delivery'