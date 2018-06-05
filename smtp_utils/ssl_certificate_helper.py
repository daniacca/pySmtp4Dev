import ssl
from OpenSSL import crypto
from socket import gethostname
from os.path import exists, join


CERT_FILE = "PySmtp4Dev.crt"
KEY_FILE = "PySmtp4Dev.key"


def create_self_signed_cert(cert_dir="."):
    """
    If datacard.crt and datacard.key don't exist in cert_dir, create a new
    self-signed cert and keypair and write them into that directory.
    """
    if not exists(join(cert_dir, CERT_FILE)) or not exists(join(cert_dir, KEY_FILE)):
        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 1024)

        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "IT"
        cert.get_subject().ST = "Italy"
        cert.get_subject().L = "Italian"
        cert.get_subject().O = "PySmtpServer4Dev"
        cert.get_subject().OU = "Smtp 4 developer testing"
        cert.get_subject().CN = gethostname()
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha1')

        open(join(cert_dir, CERT_FILE), "wb").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        open(join(cert_dir, KEY_FILE), "wb").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(join(cert_dir, CERT_FILE),join(cert_dir, KEY_FILE))
    return context