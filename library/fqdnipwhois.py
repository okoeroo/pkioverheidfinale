from library.models import FqdnIpWhois
from library.dnstools import dns_query
from library.asntools import fetch_ip2asn
from library.ssltools import cert_start_probe


def processor_fqdn2ip(fqdnipwhois: FqdnIpWhois) -> FqdnIpWhois:
    answers = dns_query(str(fqdnipwhois.fqdn), 'A')
    if not answers:
        return fqdnipwhois

    fqdnipwhois.ip = str(answers[0])

    asn_info = fetch_ip2asn(fqdnipwhois.ip)
    fqdnipwhois.asn = asn_info

    return fqdnipwhois


def processor_probe_certificates(fqdnipwhois: FqdnIpWhois) -> FqdnIpWhois:
    fqdnipwhois.cert = cert_start_probe(fqdnipwhois.fqdn)
    return fqdnipwhois
    