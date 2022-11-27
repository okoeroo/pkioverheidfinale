import ssl
from cryptography import x509

from library.models import SimplifiedCertificate


# Connect to host, get X.509 in PEM format
def get_certificate(host, port=443, timeout=5):
    cafile = "cacert.pem"
    
    try:
        conn = ssl.create_connection((host, port), timeout=timeout)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        
        # Dangerous settings!
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
#        context.load_verify_locations(cafile=cafile)

        sock = context.wrap_socket(conn, server_hostname=host)
        cert_der = sock.getpeercert(True)
        cert_pem = ssl.DER_cert_to_PEM_cert(cert_der)

        # Note: Not matching hostname on purpose

    except Exception as e:
        print(e)
        return None

    # cert_pem = ssl.get_server_certificate((host, port))
    return cert_pem


def cert_start_probe(host, port=443, timeout=5):
    # Get certificate from endpoint
    cert_pem = get_certificate(host, port, timeout)
    if cert_pem is None:
        print(f"Connection failed, no certificate to analyse")
        return None

    # Create an x509.Certificate instance
    cert_x509 = x509.load_pem_x509_certificate(bytes(cert_pem, 'utf-8'))

    print(cert_x509.not_valid_after.isoformat())
    print(cert_x509.not_valid_before.isoformat())

    # Simplified for processing
    s_cert = SimplifiedCertificate(cert_x509.subject.rfc4514_string(),
                                    cert_x509.issuer.rfc4514_string(),
                                    cert_x509.serial_number,
                                    cert_pem,
                                    cert_x509)
    return s_cert