from smtp_utils.mail_message import MailMessage

def test_mail_message_initialization():
    peer = ('127.0.0.1', 12345)
    mailfrom = "sender@example.com"
    rcpttos = ["receiver@example.com"]
    data = "This is the email body"

    message = MailMessage(peer, mailfrom, rcpttos, data)

    assert message.peer == peer
    assert message.mail_from == mailfrom
    assert message.rcpttos == rcpttos
    assert message.data == data

def test_mail_message_str():
    peer = ('127.0.0.1', 12345)
    mailfrom = "sender@example.com"
    rcpttos = ["receiver@example.com"]
    data = "This is the email body"

    message = MailMessage(peer, mailfrom, rcpttos, data)
    result = str(message)

    assert "Receiving message from" in result
    assert "sender@example.com" in result
    assert "receiver@example.com" in result
    assert str(len(data)) in result
