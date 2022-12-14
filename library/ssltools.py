import sys
import ssl
from cryptography import x509

from library.models import SimplifiedCertificate


# Connect to host, get X.509 in PEM format
def get_certificate(fqdn: str, 
                    port: int = 443,
                    timeout: int = 5,
                    verbose: bool = False):
    cafile = "cacert.pem"
    
    if verbose:
        print(f"Debug (get_certificate): {fqdn}:{port} (with timeout {timeout}s) - probing...", file=sys.stderr)

    try:
        conn = ssl.create_connection((fqdn, port), timeout=timeout)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        
        # Dangerous settings!
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        # context.load_verify_locations(cafile=cafile)

        sock = context.wrap_socket(conn, server_hostname=fqdn)
        cert_der = sock.getpeercert(True)
        cert_pem = ssl.DER_cert_to_PEM_cert(cert_der)

        # Note: Not matching hostname on purpose

    except Exception as e:
        print(f"TLS error for {fqdn}:{port} (with timeout {timeout}): {e}", file=sys.stderr)
        return None

    print(f"Debug (get_certificate): {fqdn}:{port} (with timeout {timeout}s) - success", file=sys.stderr)
    return cert_pem


def cert_start_probe(fqdn: str,
                     port: int = 443,
                     timeout: int = 5,
                     verbose: bool = False):
    # Get certificate from endpoint
    cert_pem = get_certificate(fqdn, port, timeout, verbose)
    if cert_pem is None:
        print(f"Connection failed, no certificate to analyse")
        return None

    # Create an x509.Certificate instance
    cert_x509 = x509.load_pem_x509_certificate(bytes(cert_pem, 'utf-8'))

    try:
        # Technically, multiple Common Names could appear. Concattenating when applicable.
        common_names = ",".join([c.value for c in cert_x509.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)])
    except Exception as e:
        print(f"Warning {fqdn}:{port}: no Common Name found. Exception: {e}")
        common_names = ''

    try:
        # Extract Subject Alt Names from the certificate, concattenate the output
        sans = cert_x509.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        san_dns_names = ",".join([san for san in sans.value.get_values_for_type(x509.DNSName)])
    except Exception as e:
        print(f"Warning {fqdn}:{port}: no Subject Alt Names extension. Exception: {e}")
        san_dns_names = ''

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