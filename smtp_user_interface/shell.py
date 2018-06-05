import cmd
from smtp_utils.receiver_state import SmtpReceiverState
from smtp_controller.message_handler import MessageHandler
from smtp_controller.smtp_controller import PySmtpController


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

