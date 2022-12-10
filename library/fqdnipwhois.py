import asyncio
from library.models import FqdnIpWhois
from library.dnstools import dns_query, a_dns_query, DNSERRORS
from library.asntools import fetch_ip2asn
from library.ssltools import cert_start_probe
from library.dnstools import DnsPythonConfig

def processor_fqdn2ip(fqdnipwhois: FqdnIpWhois,
                        dns_config: DnsPythonConfig,
                        verbose: bool = False) -> FqdnIpWhois:
    status, answers = dns_query(fqdnipwhois.fqdn,
                                'A', 
                                dns_config,
                                verbose)
    if status != DNSERRORS.NOERROR:
        return fqdnipwhois

    # Get list of IP addresses, let the output be sorted
    ip_list = sorted([str(rr) for rr in answers])

    # Short cut, only scan and work with the first hit
    fqdnipwhois.ip = ip_list[0]

    # Record the IP list for later use.
    fqdnipwhois.ip_list = ip_list

    asn_info = fetch_ip2asn(fqdnipwhois.ip,
                            dns_config,
                            verbose)
    fqdnipwhois.asn = asn_info

    return fqdnipwhois


async def a_processor_fqdn2ip(fqdnipwhois: FqdnIpWhois,
                                dns_config: DnsPythonConfig,
                                verbose: bool = False) -> FqdnIpWhois:
    status, answers = await a_dns_query(fqdnipwhois.fqdn,
                                        'A', 
                                        dns_config,
                                        verbose)
    if status != DNSERRORS.NOERROR:
        return fqdnipwhois

    # Get list of IP addresses, let the output be sorted
    ip_list = sorted([str(rr) for rr in answers])

    # Short cut, only scan and work with the first hit
    fqdnipwhois.ip = ip_list[0]

    # Record the IP list for later use.
    fqdnipwhois.ip_list = ip_list

    asn_info = fetch_ip2asn(fqdnipwhois.ip,
                            dns_config,
                            verbose)
    fqdnipwhois.asn = asn_info

    return fqdnipwhois



def processor_probe_certificates(fqdnipwhois: FqdnIpWhois,
                                 port: int = 443,
                                 timeout: int = 5,
                                 verbose: bool = False) -> FqdnIpWhois:
    fqdnipwhois.cert = cert_start_probe(fqdnipwhois.fqdn, port, timeout, verbose)
    return fqdnipwhois
    