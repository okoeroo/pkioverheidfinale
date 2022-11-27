#!/usr/bin/env python3

import sys
from multiprocessing import Pool
import validators

from library.cli import sanity_checks, argparsing
from library.models import FqdnIpWhois
from library.fqdnipwhois import processor_probe_certificates, processor_fqdn2ip
from library.csvtools import processor_convert_list_of_fqdnipwhois2csv


### Main
if __name__ == '__main__':
    filename = "pkioverheid.txt"
    filename = "pkishort.txt"
    outputfilename = "expanded-output.csv"

    # Parse arguments
    args = argparsing()
    if not sanity_checks(args):
        sys.exit(1)

    # Open and parse input
    with open(args.input_filename, "r") as f:
        fqdns = [FqdnIpWhois(fqdn.lower()) for fqdn in f.read().splitlines() if validators.domain(fqdn)]


#    with Pool(processes=256) as p:
#        fqdns_with_dns = p.map_async(processor_fqdn2ip, fqdns).get()
    fqdns_with_dns = [processor_fqdn2ip(fqdn) for fqdn in fqdns]


    fqdns_with_cert = [processor_probe_certificates(fqdn) for fqdn in fqdns_with_dns]

    processor_convert_list_of_fqdnipwhois2csv(args.output_filename, fqdns_with_cert)

