from aiosmtpd.smtp import SMTP as SMTPServer
from aiosmtpd.controller import Controller
from smtp_utils.receiver_state import SmtpReceiverState

class PySmtpController(Controller):
    def __init__(self, handler, arguments=None, *args, **kwargs):
        self.state = SmtpReceiverState.INIT
        self.arguments = arguments
        super().__init__(handler,
                         hostname=arguments.ip_address_local if arguments else None,
                         port=arguments.port_local if arguments else 8025,
                         ssl_context=arguments.context if arguments else None,
                         *args, **kwargs)

    def get_email_counter(self):
        return 0 if not self.handler else self.handler.email_counter

    def get_received_emails(self):
        return self.handler.emails

    def set_parameters(self, arguments):
        if self.state == SmtpReceiverState.RUNNING:
            print("Can't set server parameters while server is already running."
                  "Please stop server first to change parameters.")
            return
        if arguments:
            self.arguments = arguments
            self.state = SmtpReceiverState.READY

    def factory(self):
        if not self.arguments:
            return super().factory()
        else:
            context = self.arguments.context
            return SMTPServer(hostname=self.hostname,
                              handler=self.handler,
                              enable_SMTPUTF8=self.enable_SMTPUTF8,
                              require_starttls = True if context else False,
                              tls_context = context)

    def start(self, *arguments):
        if self.state == SmtpReceiverState.RUNNING:
            print("Server already running.")
            return
        if self.state != SmtpReceiverState.RUNNING and self.state != SmtpReceiverState.INIT:
            if not self.arguments and not arguments:
                print("Server not configured, please set at least local"
                      " address and the local port to start listening.")
                return
        print("Starting SMTP server on (Address = %s, Port = %s)" % (self.hostname, str(self.port)))
        super().start()
        self.state = SmtpReceiverState.RUNNING
        print("Server on, waiting for emails...")

    def stop(self):
        if self.state != SmtpReceiverState.RUNNING:
            print("Can't execute stop command, there is no server running!")
            return
        print("Exit SMTP server...", end='')
        super().stop()
        print("...SMTP server stopped!")
        self.state = SmtpReceiverState.STOPPED

