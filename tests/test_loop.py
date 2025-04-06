# tests/test_loop.py
from unittest.mock import patch, MagicMock
from smtp_user_interface.loop import loop  # importa la funzione, non il modulo

@patch("smtp_user_interface.loop.time.sleep", return_value=None)
@patch("smtp_user_interface.loop.PySmtpController")
@patch("smtp_user_interface.loop.MessageHandler")
def test_loop_prints_email_and_handles_interrupt(mock_handler_cls, mock_controller_cls, mock_sleep):
    # Arrange
    mock_handler = MagicMock()
    mock_handler_cls.return_value = mock_handler

    mock_receiver = MagicMock()
    mock_receiver.get_email_counter.side_effect = [1, KeyboardInterrupt()]
    mock_receiver.get_received_emails.return_value.popleft.return_value = "Test Email"
    mock_controller_cls.return_value = mock_receiver

    with patch("smtp_user_interface.loop.print") as mock_print, \
         patch("smtp_user_interface.loop.PySmtpArgumentParser") as mock_parser_cls:

        mock_args = MagicMock()
        mock_args.file_log = False
        mock_args.log_dir = None
        mock_args.max_email = 1

        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_parser_cls.return_value.instance = mock_parser

        # Act
        loop()

    # Assert
    mock_handler_cls.assert_called_once()
    mock_controller_cls.assert_called_once()
    mock_receiver.start.assert_called_once()
    mock_receiver.stop.assert_called_once()
    mock_print.assert_any_call("Test Email")
    mock_print.assert_any_call("Thank you for using PySmtp4Dev!")
