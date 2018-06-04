import argparse, os, cmd
import collections, enum
from aiosmtpd.smtp import SMTP as SMTPServer
from aiosmtpd.controller import Controller
from datetime import datetime
import time


class SmtpReceiverState(enum.Enum):
    INIT = 0
    READY = 1
    RUNNING = 2
    STOPPED = 3


class MailMessage():
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


class PySmtpController(Controller):
    def __init__(self, handler, arguments=None, *args, **kwargs):
        self.state = SmtpReceiverState.INIT
        self.arguments = arguments
        super().__init__(handler,
                         hostname=arguments.ip_address_local if arguments else None,
                         port=arguments.port_local if arguments else 8025,
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
            return SMTPServer(hostname=self.hostname,
                              handler=self.handler,
                              enable_SMTPUTF8=self.enable_SMTPUTF8)

    def start(self, *arguments):
        if self.state == SmtpReceiverState.RUNNING:
            print("Server already running.")
            return
        if self.state != SmtpReceiverState.RUNNING and self.state != SmtpReceiverState.INIT:
            if not self.arguments and not arguments:
                print("Server not configured, please set at least local address and the local port to start listening.")
                return
        print("Starting SMTP server on (Address = %s, Port = %s)" % (self.hostname, str(self.port)))
        super().start()
        self.state = SmtpReceiverState.RUNNING
        print("Server on, waiting for emails...")

    def stop(self):
        if self.state == SmtpReceiverState.RUNNING:
            print("Exit SMTP server...", end='')
            super().stop()
            print("...SMTP server stopped!")
            self.state = SmtpReceiverState.STOPPED
        else:
            print("Can't execute stop command, there is no server running!")


class PySmtpShell(cmd.Cmd):
    intro = 'Welcome to PySmtp4Dev, SMTP test server for developers.\nType help or ? to list commands.\n'
    prompt = '(PySmtp4Dev)$ '

    def __init__(self, arguments, parser):
        self.arguments = arguments
        self.parser = parser
        handler = MessageHandler(file_logging=arguments.file_log, log_dir=arguments.log_dir,
                                 max_email=arguments.max_email)
        self.receiver = PySmtpController(handler, arguments)
        super(PySmtpShell, self).__init__()

    def __parse(self, arg):
        return tuple(map(str, arg.split()))

    def preloop(self):
        if self.arguments:
            self.receiver.set_parameters(self.arguments)
            if self.arguments.auto_start:
                print("Selected Auto start mode => trying to start server using the given/default parameters..")
                self.receiver.start()

    def precmd(self, line):
        return line.lower()

    def do_set_params(self, arg):
        'Setting the server parameters, using the same syntax for command line arguments: SET_PARAMS [-options] [value]'
        if self.parser:
            arguments = self.parser.parse_args(self.__parse(arg))
            self.receiver.set_parameters(arguments)

    def do_email_counter(self, arg):
        'Get the number of received email from server: EMAIL_COUNTER'
        print(self.receiver.get_email_counter())

    def do_server_state(self, arg):
        'Print the actual server state: SERVER_STATE '
        print('Server state = ' + self.receiver.state.name)

    def do_last_email(self, arg):
        'Print last email received in the buffer: LAST_EMAIL'
        if self.receiver.get_email_counter() > 0:
            last_email = self.receiver.get_received_emails().popleft()
            print(str(last_email))
        else:
            print("No email in the receiver buffer!")

    def do_print_all_email(self, arg):
        'Print all email received in the buffer: PRINT_ALL_EMAIL'
        emails = self.receiver.get_received_emails()
        for email in emails:
            print(str(email))

    def do_start(self, arg):
        'Start the server listening: START'
        self.receiver.start()

    def do_stop(self, arg):
        'Stop the server listening: STOP'
        self.receiver.stop()

    def do_exit(self, arg):
        'Stop listening and receiving email, close server and exit program:  EXIT'
        print('Thank you for using pySmtp4Dev...')
        if self.receiver.state == SmtpReceiverState.RUNNING:
            self.receiver.stop()
        return True


class MyArgumentParser():
    instance = None

    class __MyArgumentParser(argparse.ArgumentParser):
        def __init__(self, *arg):
            super().__init__(*arg)
            self.description = 'Smtp Debug Server Utility'
            self.add_argument('-al', action="store", dest="ip_address_local", default='0.0.0.0',
                                help='ip address local to start server listening, use 0.0.0.0 for all the interfaces')
            self.add_argument('-ar', action="store", dest="ip_address_remote", default=None,
                                help='ip address remote, address to redirect email messages. Optional.')
            self.add_argument('-pl', action="store", dest="port_local", default=2525,
                                help='local port for server listening. Default to 2525.')
            self.add_argument('-pr', action="store", dest="port_remote", default=None,
                                help='remote port to redirect email messages. Optional')
            self.add_argument('-f', action="store_true", dest="file_log", default=False,
                                help='Activate log on file system for every email received')
            self.add_argument('-ld', action="store", dest="log_dir", default='./email_log',
                                help='Logging directory, where the server put the email. Default ./email_log. '
                                     'If directory not exists it will be created')
            self.add_argument('-max_email', action="store", dest="max_email", default=50,
                                help='Max number of email to keep in memory. The emails are keep in memory '
                                     'with circular buffer.')
            self.add_argument('-as', '--auto_start', action="store_true", dest="auto_start", default=False,
                                help='Auto start server SMTP server listening with the default parameters.')
            self.add_argument('-sh', '--shell', action="store_true", dest="shell_mode", default=False,
                                help='Start server SMTP listening with the default parameters in shell interactive mode.')
            self.add_argument('-ssl', '--start_ssl', action="store_true", dest="shell_mode", default=False,
                              help='Enable SSL context for connection on server SMTP')

        def __str__(self):
            return repr(self)

    def __init__(self, *arg):
        if not MyArgumentParser.instance:
            MyArgumentParser.instance = MyArgumentParser.__MyArgumentParser(*arg)

    def __getattr__(self, name):
        return getattr(self.instance, name)


def main():
    parser = MyArgumentParser().instance
    arguments = parser.parse_args()
    if arguments.shell_mode:
        PySmtpShell(arguments, parser).cmdloop()
    else:
        handler = MessageHandler(file_logging=arguments.file_log, log_dir=arguments.log_dir
                                   ,max_email=arguments.max_email)
        receiver = PySmtpController(handler, arguments)
        receiver.start()
        try:
            while True:
                if receiver.get_email_counter() > 0:
                    try:
                        print(str(receiver.get_received_emails().popleft()))
                    except IndexError:
                        pass
                    except KeyboardInterrupt as interrupt:
                        raise interrupt
                time.sleep(0.1)
        except KeyboardInterrupt:
            receiver.stop()


if __name__ == '__main__':
    main()