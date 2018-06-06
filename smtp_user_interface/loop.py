import time
from smtp_controller import MessageHandler, PySmtpController
from smtp_user_interface import PySmtpArgumentParser


def loop(arguments=None):
    if not arguments:
        arguments = PySmtpArgumentParser().instance.parse_args()
    handler = MessageHandler(file_logging=arguments.file_log,
                             log_dir=arguments.log_dir,
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
    print("Thank you for using PySmtp4Dev!")