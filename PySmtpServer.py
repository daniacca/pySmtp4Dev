import time
from smtp_utils import ssl_certificate_helper
from smtp_controller.message_handler import MessageHandler
from smtp_controller.smtp_controller import PySmtpController
from smtp_user_interface.shell import PySmtpShell
from smtp_user_interface.arguments_parser import MyArgumentParser


def main():
    parser = MyArgumentParser().instance
    arguments = parser.parse_args()

    if arguments.enable_ssl:
        arguments.context = ssl_certificate_helper.create_self_signed_cert()
    else:
        arguments.context = None

    if arguments.shell_mode:
        PySmtpShell(arguments, parser).cmdloop()
    else:
        handler = MessageHandler(file_logging=arguments.file_log, log_dir=arguments.log_dir,
                                 max_email=arguments.max_email)
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