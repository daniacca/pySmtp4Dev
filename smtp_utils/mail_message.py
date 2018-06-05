class MailMessage:
    def __init__(self, peer, mailfrom, rcpttos, data):
        self.peer = peer
        self.mail_from = mailfrom
        self.rc_prros = rcpttos
        self.data = data

    def __str__(self):
        return str.format("Receiving message from : {0}\n" +
                          "Message addressed from : {1}\n" +
                          "Message addressed to   : {2}\n" +
                          "Message length         : {3}\n",
                          self.peer, self.mail_from, self.rc_prros, len(self.data))