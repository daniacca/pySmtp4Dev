import argparse


class PySmtpArgumentParser():
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
            self.add_argument('-ssl', '--start_ssl', action="store_true", dest="enable_ssl", default=False,
                              help='Enable SSL context for connection on server SMTP')

        def __str__(self):
            return repr(self)

    def __init__(self, *arg):
        if not PySmtpArgumentParser.instance:
            PySmtpArgumentParser.instance = PySmtpArgumentParser.__MyArgumentParser(*arg)

    def __getattr__(self, name):
        return getattr(self.instance, name)

