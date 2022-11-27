import ipaddress
from library.models import ASN, ASNDescription
from library.dnstools import dns_query


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
