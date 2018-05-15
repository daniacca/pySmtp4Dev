import asyncore, argparse, os, cmd
import threading, collections, enum
from smtpd import SMTPServer
from datetime import datetime


class SmtpReceiverState(enum.Enum):
    INIT = 0
    READY = 1
    RUNNING = 2
    STOPPED = 3


class MailMessage():
    def __init__(self, peer, mailfrom, rcpttos, data):
        self.peer = peer
        self.mailfrom = mailfrom
        self.rcprros = rcpttos
        self.data = data

    def __str__(self):
        return str.format("Receiving message from : {0}\n" +
                          "Message addressed from : {1}\n" +
                          "Message addressed to   : {2}\n" +
                          "Message length         : {3}\n",
                          self.peer, self.mailfrom, self.rcprros, len(self.data))


class pySmtpServer(SMTPServer):
    def __init__(self, localaddr, remoteaddr, file_logging, log_dir, max_email):
        SMTPServer.__init__(self, localaddr, remoteaddr, decode_data=True)
        self.emails = collections.deque(maxlen = int(max_email))
        self.log_file = file_logging
        try:
            self.logging_directory = os.path.realpath(log_dir)
            if not os.path.exists(self.logging_directory):
                os.makedirs(self.logging_directory)
        except:
            self.logging_directory = os.path.realpath(".")

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        if self.log_file:
            try:
                filename = '%s-%d.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'), self.no)
                filepath = os.path.join(self.logging_directory, filename)
                f = open(filepath, 'w')
                f.write(data)
            except Exception:
                print('Error on saving email to file...')
            finally:
                if f: f.close
        self.emails.append(MailMessage(peer,mailfrom,rcpttos,data))


class pySmtpReceiver(object):
    def __init__(self):
        self.state = SmtpReceiverState.INIT
        self.arguments = None
        self.smtp_server = None
        self.thread = None

    def set_parameters(self, arguments):
        if(self.state == SmtpReceiverState.RUNNING):
            print("Can't set server parameters while server is already running. Please stop server first to change parameters.")
            return
        if(arguments):
            self.arguments = arguments
            self.state = SmtpReceiverState.READY

    def start(self, *arguments):
        if (self.state == SmtpReceiverState.RUNNING):
            print("Server already running.")
            return
        if(self.state != SmtpReceiverState.RUNNING and self.state != SmtpReceiverState.INIT):
            if(not self.arguments and not arguments):
                print("Server not configured, please set at least the local address and the local port to start listening.")
                return
        if(arguments):
            self.arguments = arguments[0]
        local_address = (self.arguments.ip_address_local, self.arguments.port_local)
        remote_addess = None if not (self.arguments.ip_address_remote and self.arguments.port_remote) else (self.arguments.ip_address_remote, self.arguments.port_remote)
        print("Starting SMTP server on (Address = %s, Port = %d)" % (local_address[0], local_address[1]))
        self.smtp_server = pySmtpServer(local_address, remote_addess, self.arguments.file_log, self.arguments.log_dir, self.arguments.max_email)
        self.smtp_server.send()
        self.thread = threading.Thread(target=asyncore.loop, kwargs = {'timeout':1} )
        self.thread.start()
        self.state = SmtpReceiverState.RUNNING
        print("Server on, waiting for emails...")

    def stop(self):
        if(self.state == SmtpReceiverState.RUNNING):
            print("Exit SMTP server...", end='')
            self.smtp_server.close()
            self.thread.join()
            print("...SMTP server stopped!")
            self.state = SmtpReceiverState.STOPPED
        else:
            print("Can't execute stop command, there is no server running!")

    def count(self):
        return 0 if not self.smtp_server else self.smtp_server.emails.count()

    def get(self):
        return self.smtp_server.emails


class PySmtpShell(cmd.Cmd):
    intro = 'Welcome to PySmtp4Dev, SMTP test server for developers.\nType help or ? to list commands.\n'
    prompt = '(PySmtp4Dev)$ '

    def __init__(self, arguments, parser):
        super(PySmtpShell, self).__init__()
        self.arguments = arguments
        self.parser = parser
        self.receiver = pySmtpReceiver()

    def preloop(self):
        if (self.arguments):
            self.receiver.set_parameters(self.arguments)
            if (self.arguments.auto_start):
                print("Selected Auto start mode => trying to start server using the given/default parameters..")
                self.receiver.start()

    def precmd(self, line):
        return line.lower()

    def do_set_params(self, arg):
        'Setting the server parameters, using the same syntax for command line arguments: SET_PARAMS [-options] [value]'
        if (self.parser):
            arguments = self.parser.parse_args(parse(arg))
            self.receiver.set_parameters(arguments)

    def do_email_counter(self, arg):
        'Get the number of received email from server: EMAIL_COUNTER'
        print(self.receiver.count())

    def do_server_state(self, arg):
        'Print the actual server state: SERVER_STATE '
        print('Server state = ' + self.receiver.state.name)

    def do_last_email(self, arg):
        'Print last email received in the buffer: LAST_EMAIL'
        last_email = self.receiver.get().popleft()
        print(str(last_email))

    def do_start(self, arg):
        'Start the server listening: START'
        self.receiver.start()

    def do_stop(self, arg):
        'Stop the server listening: STOP'
        self.receiver.stop()

    def do_exit(self, arg):
        'Stop listening and receiving email, close server and exit program:  EXIT'
        print('Thank you for using pySmtp4Dev...')
        if(self.receiver.state == SmtpReceiverState.RUNNING):
            self.receiver.stop()
        return True


def parse(arg):
    return tuple(map(str, arg.split()))


def main():
    parser = argparse.ArgumentParser(description='Smtp Debug Server Utility')
    parser.add_argument('-al', action="store", dest="ip_address_local", default='0.0.0.0',
                        help='ip address local to start server listening, use 0.0.0.0 for all the interfaces')
    parser.add_argument('-ar', action="store", dest="ip_address_remote", default=None,
                        help='ip address remote, address to redirect email messages. Optional.')
    parser.add_argument('-pl', action="store", dest="port_local", default=2525,
                        help='local port for server listening. Default to 2525.')
    parser.add_argument('-pr', action="store", dest="port_remote", default=None,
                        help='remote port to redirect email messages. Optional')
    parser.add_argument('-f', action="store_true", dest="file_log", default=False,
                        help='Activate log on file system for every email received')
    parser.add_argument('-ld', action="store", dest="log_dir", default='./email_log',
                        help='Logging directory, where the server put the email. Default ./email_log. '
                             'If directory not exists it will be created')
    parser.add_argument('-max_email', action="store", dest="max_email", default=50,
                        help='Max number of email to keep in memory. The emails are keep in memory with a circular buffer.')
    parser.add_argument('-start', action="store_true", dest="auto_start", default=False,
                        help='Auto start server SMTP server listening with the default parameters.')
    arguments = parser.parse_args()
    PySmtpShell(arguments, parser).cmdloop()


if __name__ == '__main__':
    main()