from unittest.mock import MagicMock, patch
from smtp_user_interface.shell import PySmtpShell
from smtp_utils import SmtpReceiverState

def test_shell_exit_calls_stop_if_running():
    arguments = MagicMock()
    receiver_mock = MagicMock()
    receiver_mock.state = SmtpReceiverState.RUNNING

    with patch("smtp_user_interface.shell.MessageHandler"), \
         patch("smtp_user_interface.shell.PySmtpController", return_value=receiver_mock), \
         patch("smtp_user_interface.shell.print") as mock_print:

        shell = PySmtpShell(arguments)
        shell.receiver = receiver_mock

        result = shell.do_exit("")

        assert result is True
        receiver_mock.stop.assert_called_once()
        mock_print.assert_any_call("Thank you for using pySmtp4Dev...")

def test_shell_exit_does_not_call_stop_if_not_running():
    arguments = MagicMock()
    receiver_mock = MagicMock()
    receiver_mock.state = SmtpReceiverState.STOPPED

    with patch("smtp_user_interface.shell.MessageHandler"), \
         patch("smtp_user_interface.shell.PySmtpController", return_value=receiver_mock), \
         patch("smtp_user_interface.shell.print") as mock_print:

        shell = PySmtpShell(arguments)
        shell.receiver = receiver_mock

        result = shell.do_exit("")

        assert result is True
        receiver_mock.stop.assert_not_called()
        mock_print.assert_any_call("Thank you for using pySmtp4Dev...")

def test_shell_email_counter_prints_value():
    arguments = MagicMock()
    receiver_mock = MagicMock()
    receiver_mock.get_email_counter.return_value = 3

    with patch("smtp_user_interface.shell.MessageHandler"), \
         patch("smtp_user_interface.shell.PySmtpController", return_value=receiver_mock), \
         patch("smtp_user_interface.shell.print") as mock_print:

        shell = PySmtpShell(arguments)
        shell.receiver = receiver_mock

        shell.do_email_counter("")

        mock_print.assert_called_once_with(3)

        receiver_mock.get_email_counter.assert_called_once()

def test_shell_print_all_email_prints_all():
    arguments = MagicMock()
    receiver_mock = MagicMock()
    receiver_mock.get_received_emails.return_value = ["Email1", "Email2"]

    with patch("smtp_user_interface.shell.MessageHandler"), \
         patch("smtp_user_interface.shell.PySmtpController", return_value=receiver_mock), \
         patch("smtp_user_interface.shell.print") as mock_print:

        shell = PySmtpShell(arguments)
        shell.receiver = receiver_mock

        shell.do_print_all_email("")

        mock_print.assert_any_call("Email1")
        mock_print.assert_any_call("Email2")

def test_shell_set_params_uses_parser_and_sets_parameters():
    arguments = MagicMock()
    parsed_arguments = MagicMock()
    parser_mock = MagicMock()
    parser_mock.parse_args.return_value = parsed_arguments

    receiver_mock = MagicMock()

    with patch("smtp_user_interface.shell.MessageHandler"), \
         patch("smtp_user_interface.shell.PySmtpController", return_value=receiver_mock):

        shell = PySmtpShell(arguments, parser=parser_mock)
        shell.receiver = receiver_mock

        shell.do_set_params("-f True -m 3")

        parser_mock.parse_args.assert_called_once()
        receiver_mock.set_parameters.assert_called_with(parsed_arguments)

def test_shell_start_and_stop_call_receiver_methods():
    arguments = MagicMock()
    receiver_mock = MagicMock()

    with patch("smtp_user_interface.shell.MessageHandler"), \
         patch("smtp_user_interface.shell.PySmtpController", return_value=receiver_mock):

        shell = PySmtpShell(arguments)
        shell.receiver = receiver_mock

        shell.do_start("")
        receiver_mock.start.assert_called_once()

        shell.do_stop("")
        receiver_mock.stop.assert_called_once()

def test_shell_last_email_with_email():
    arguments = MagicMock()
    receiver_mock = MagicMock()
    receiver_mock.get_email_counter.return_value = 1
    receiver_mock.get_received_emails.return_value.popleft.return_value = "LastEmail"

    with patch("smtp_user_interface.shell.MessageHandler"), \
         patch("smtp_user_interface.shell.PySmtpController", return_value=receiver_mock), \
         patch("smtp_user_interface.shell.print") as mock_print:

        shell = PySmtpShell(arguments)
        shell.receiver = receiver_mock

        shell.do_last_email("")

        mock_print.assert_called_with("LastEmail")

def test_shell_last_email_without_email():
    arguments = MagicMock()
    receiver_mock = MagicMock()
    receiver_mock.get_email_counter.return_value = 0

    with patch("smtp_user_interface.shell.MessageHandler"), \
         patch("smtp_user_interface.shell.PySmtpController", return_value=receiver_mock), \
         patch("smtp_user_interface.shell.print") as mock_print:

        shell = PySmtpShell(arguments)
        shell.receiver = receiver_mock

        shell.do_last_email("")

        mock_print.assert_called_with("No email in the receiver buffer!")
