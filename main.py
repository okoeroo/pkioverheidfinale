#!/usr/bin/env python3

import sys
import validators

from library.cli import sanity_checks, argparsing
from library.models import FqdnIpWhois
from library.fqdnipwhois import processor_probe_certificates, processor_fqdn2ip
from library.csvtools import processor_convert_list_of_fqdnipwhois2csv
from library.dnstools import DnsPythonConfig


### Main
def main():
    # Parse arguments and quit if sanity checks fail
    args = argparsing()
    if not sanity_checks(args):
        sys.exit(1)

    # Open and parse input
    with open(args.input_filename, "r") as f:
        fqdns = [FqdnIpWhois(fqdn.lower()) for fqdn in f.read().splitlines() if validators.domain(fqdn)]

    # Parse and construct config for dnspython
    dns_config = DnsPythonConfig(args.dns_servers)

    # DNS query the list, and add to the object list
    fqdns_with_dns = [processor_fqdn2ip(fqdn,
                                        dns_config,
                                        args.verbose) for fqdn in fqdns]

    # Probe for certificates and expand the object list
    fqdns_with_cert = [processor_probe_certificates(fqdn,
                                                    args.port, 
                                                    args.timeout, 
                                                    args.verbose) for fqdn in fqdns_with_dns]

    # Write output to CSV file
    processor_convert_list_of_fqdnipwhois2csv(args.output_filename, fqdns_with_cert)


if __name__ == '__main__':
    main()