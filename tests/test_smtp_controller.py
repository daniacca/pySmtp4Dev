from unittest.mock import MagicMock, patch

from smtp_utils.receiver_state import SmtpReceiverState
from smtp_controller import PySmtpController


class DummyHandler:
    def __init__(self):
        self.email_counter = 5
        self.emails = ["email1", "email2"]

class DummyArgs:
    def __init__(self, ip_address_local="127.0.0.1", port_local=8025, context=None):
        self.ip_address_local = ip_address_local
        self.port_local = port_local
        self.context = context


def test_initial_state():
    controller = PySmtpController(handler=DummyHandler(), arguments=None)
    assert controller.state == SmtpReceiverState.INIT
    assert controller.arguments is None


def test_get_email_counter_and_emails():
    handler = DummyHandler()
    controller = PySmtpController(handler=handler)
    assert controller.get_email_counter() == 5
    assert controller.get_received_emails() == ["email1", "email2"]


def test_set_parameters_when_not_running():
    controller = PySmtpController(handler=DummyHandler())
    args = DummyArgs()
    controller.set_parameters(args)
    assert controller.arguments == args
    assert controller.state == SmtpReceiverState.READY


def test_set_parameters_when_running(capfd):
    controller = PySmtpController(handler=DummyHandler())
    controller.state = SmtpReceiverState.RUNNING
    controller.set_parameters(DummyArgs())
    out, _ = capfd.readouterr()
    assert "Can't set server parameters while server is already running" in out


@patch("smtp_controller.smtp_controller.SMTPServer")
def test_factory_with_context(mock_smtp_class):
    handler = DummyHandler()
    context = MagicMock()
    args = DummyArgs(context=context)
    controller = PySmtpController(handler=handler, arguments=args)

    smtp_instance = controller.factory()
    mock_smtp_class.assert_called_once()
    assert smtp_instance == mock_smtp_class.return_value


@patch("smtp_controller.smtp_controller.Controller.start")
def test_start_changes_state_and_prints(mock_start, capfd):
    controller = PySmtpController(handler=DummyHandler(), arguments=DummyArgs())
    controller.state = SmtpReceiverState.READY

    controller.start()
    out, _ = capfd.readouterr()
    assert "Starting SMTP server on" in out
    assert "Server on, waiting for emails" in out
    assert controller.state == SmtpReceiverState.RUNNING
    mock_start.assert_called_once()


@patch("smtp_controller.smtp_controller.Controller.stop")
def test_stop_changes_state_and_prints(mock_stop, capfd):
    controller = PySmtpController(handler=DummyHandler(), arguments=DummyArgs())
    controller.state = SmtpReceiverState.RUNNING

    controller.stop()
    out, _ = capfd.readouterr()
    assert "Stopping SMTP server..." in out
    assert "...SMTP server stopped!" in out
    assert controller.state == SmtpReceiverState.STOPPED
    mock_stop.assert_called_once()


def test_stop_when_not_running(capfd):
    controller = PySmtpController(handler=DummyHandler(), arguments=DummyArgs())
    controller.state = SmtpReceiverState.READY

    controller.stop()
    out, _ = capfd.readouterr()
    assert "Can't execute stop command, there is no server running!" in out
    assert controller.state == SmtpReceiverState.READY