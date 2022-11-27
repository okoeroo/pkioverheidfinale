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

    # Technically, multiple Common Names could appear. Concattenating when applicable.
    common_names = ",".join([c.value for c in cert_x509.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)])

    sans = cert_x509.extensions.get_extension_for_class(x509.SubjectAlternativeName)
    san_dns_names = ",".join([san for san in sans.value.get_values_for_type(x509.DNSName)])
    print(san_dns_names)


    # Simplified for processing
    s_cert = SimplifiedCertificate(cert_x509.subject.rfc4514_string(),
                                    cert_x509.issuer.rfc4514_string(),
                                    cert_x509.serial_number,
                                    cert_x509.not_valid_before.isoformat(),
                                    cert_x509.not_valid_after.isoformat(),
                                    common_names,
                                    san_dns_names,
                                    cert_pem,
                                    cert_x509)
    return s_cert