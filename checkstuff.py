import os
import sys
from multiprocessing import Pool
import validators
import dns.resolver
import ipaddress
import csv

from dataclasses import dataclass


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

def processor_convert_list_of_fqdnipwhois2csv(fqdns_with_dns: list[FqdnIpWhois]) -> None:
    filename = "/tmp/output.csv"
    with open(filename, 'w') as csvfile:
        fieldnames = ['fqdn', 'ip', 'prefix',
                        'asn', 'asn_description', 
                        'country', 'registrar',
                        'last_update_asn', 'last_update_asn_desc']
    
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()

        for f in fqdns_with_dns:
            if f.ip is None:
                csvwriter.writerow({'fqdn': f.fqdn,
                                    'ip': 'FAILURE'})
            else:
                csvwriter.writerow({'fqdn': f.fqdn,
                                    'ip': f.ip, 
                                    'prefix': f.asn.prefix, 
                                    'asn': f.asn.asn,
                                    'asn_description': f.asn.asn_description.description, 
                                    'country': f.asn.country, 
                                    'registrar': f.asn.registrar, 
                                    'last_update_asn': f.asn.last_update, 
                                    'last_update_asn_desc': f.asn.asn_description.last_update})


### Main
if __name__ == '__main__':
#    filename = "/tmp/pkishort.txt"
    filename = "/tmp/pkioverheid.txt"

    with open(filename, "r") as f:
        fqdns = [FqdnIpWhois(fqdn.lower()) for fqdn in f.read().splitlines() if validators.domain(fqdn)]


    with Pool(processes=256) as p:
        fqdns_with_dns = p.map_async(processor_fqdn2ip, fqdns).get()
#    fqdns_with_dns = [processor_fqdn2ip(fqdn) for fqdn in fqdns]

    print(fqdns_with_dns)

    processor_convert_list_of_fqdnipwhois2csv(fqdns_with_dns)

