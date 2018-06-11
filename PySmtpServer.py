from smtp_utils import create_self_signed_cert
from smtp_user_interface import PySmtpShell, PySmtpArgumentParser, loop


def main():
    arguments = PySmtpArgumentParser().instance.parse_args()

    arguments.context = None
    if arguments.enable_ssl:
        arguments.context = create_self_signed_cert()

    if arguments.shell_mode:
        PySmtpShell(arguments).cmdloop()
    else:
        loop(arguments)


if __name__ == '__main__':
    main()