import os
import sys
from multiprocessing import Pool
import validators
import dns.resolver
import ipaddress
import csv

import ssl
from cryptography import utils, x509

from dataclasses import dataclass


@dataclass
class SimplifiedCertificate:
    subject_dn: str
    issuer_dn: str
    serial_nr: str
    pem: str   
    certificate: x509.Certificate 

@dataclass
class ASNDescription:
    asn: int
    country: str
    registrar: str
    last_update: str
    description: str

@dataclass
class ASN:
    asn: int
    prefix: str
    country: str
    registrar: str
    last_update: str
    asn_description: ASNDescription

@dataclass
class FqdnIpWhois:
    fqdn: str
    ip: str | None = None
    asn: ASN | None = None
    cert: SimplifiedCertificate | None = None



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

    # Simplified for processing
    s_cert = SimplifiedCertificate(cert_x509.subject.rfc4514_string(),
                                    cert_x509.issuer.rfc4514_string(),
                                    cert_x509.serial_number,
                                    cert_pem,
                                    cert_x509)
    return s_cert


def dns_query(fqdn: str, r_type: str):
    try:
        answers = dns.resolver.resolve(fqdn, r_type)
        return answers

    except Exception:
        return None


def fetch_asndescription(asn: int) -> ASNDescription:
    fqdn = "AS" + str(asn) + ".asn.cymru.com"

    answers = dns_query(fqdn, "TXT")
    rr_data = str(answers[0]).replace('"','')

    asn = int(rr_data.split(" | ")[0])
    country = rr_data.split(" | ")[1]
    registrar = rr_data.split(" | ")[2]
    last_update = rr_data.split(" | ")[3]
    description = rr_data.split(" | ")[4]

    # Create ASN object
    asn_desc = ASNDescription(asn, country, registrar, last_update, description)

    return asn_desc


def fetch_ip2asn(ip: str) -> ASN:
    ip_obj = ipaddress.ip_address(ip)

    fqdn = ip_obj.reverse_pointer.split(".in-addr.arpa")[0] + ".origin.asn.cymru.com"

    answers = dns_query(fqdn, "TXT")
    rr_data = str(answers[0]).replace('"','')

    asn = int(rr_data.split(" | ")[0])
    prefix = rr_data.split(" | ")[1]
    country = rr_data.split(" | ")[2]
    registrar = rr_data.split(" | ")[3]
    last_update = rr_data.split(" | ")[4]

    # Create ASN Description object
    asn_desc = fetch_asndescription(asn)

    # Create ASN object
    asn_info = ASN(asn, prefix, country, registrar, last_update, asn_desc)

    return asn_info


def processor_fqdn2ip(fqdnipwhois: FqdnIpWhois) -> FqdnIpWhois:
    answers = dns_query(str(fqdnipwhois.fqdn), 'A')
    if not answers:
        return fqdnipwhois

    fqdnipwhois.ip = str(answers[0])

    asn_info = fetch_ip2asn(fqdnipwhois.ip)
    fqdnipwhois.asn = asn_info

    return fqdnipwhois


def generate_csv_row_dict(f: FqdnIpWhois) -> dict:
    row = {}
    row['fqdn'] = f.fqdn
    if f.ip is None:
        row['ip'] = 'FAILURE'
    else:
        row['ip'] = f.ip
        row['prefix'] = f.asn.prefix
        row['asn'] = f.asn.asn
        row['asn_description'] = f.asn.asn_description.description 
        row['country'] = f.asn.country 
        row['registrar'] = f.asn.registrar 
        row['last_update_asn'] = f.asn.last_update 
        row['last_update_asn_desc'] = f.asn.asn_description.last_update
    
    if f.cert is not None:
        row['subject_dn'] = f.cert.subject_dn
        row['issuer_dn'] = f.cert.issuer_dn

    return row

def processor_convert_list_of_fqdnipwhois2csv(fqdns_with_dns: list[FqdnIpWhois]) -> None:
    filename = "expanded-output.csv"
    with open(filename, 'w') as csvfile:
        fieldnames = ['fqdn', 'ip', 'prefix',
                        'asn', 'asn_description', 
                        'country', 'registrar',
                        'last_update_asn', 'last_update_asn_desc',
                        'subject_dn', 'issuer_dn']
    
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()

        for f in fqdns_with_dns:
            csvwriter.writerow(generate_csv_row_dict(f))


def processor_probe_certificates(fqdnipwhois: FqdnIpWhois) -> FqdnIpWhois:
    fqdnipwhois.cert = cert_start_probe(fqdnipwhois.fqdn)
    return fqdnipwhois
    

### Main
if __name__ == '__main__':
    filename = "pkioverheid.txt"
    filename = "pkishort.txt"

    with open(filename, "r") as f:
        fqdns = [FqdnIpWhois(fqdn.lower()) for fqdn in f.read().splitlines() if validators.domain(fqdn)]


    with Pool(processes=256) as p:
        fqdns_with_dns = p.map_async(processor_fqdn2ip, fqdns).get()
#    fqdns_with_dns = [processor_fqdn2ip(fqdn) for fqdn in fqdns]

    fqdns_with_cert = [processor_probe_certificates(fqdn) for fqdn in fqdns_with_dns]
    print("==================================================")

    processor_convert_list_of_fqdnipwhois2csv(fqdns_with_cert)

