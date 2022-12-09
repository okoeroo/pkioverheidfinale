import sys
import dns.resolver
from enum import Enum

class DNSERRORS(Enum):
    NOERROR = 1,
    NXDOMAIN = 2,
    SERVFAIL = 3,
    TIMEOUT = 4,
    ERROR = 5


def dns_query(fqdn: str, r_type: str,
                nameservers: str = None,
                verbose: bool = False) -> tuple[DNSERRORS, str]:

    if verbose:
        print(f"DNS query (verbose): FQDN={fqdn} RRtype={r_type}", file=sys.stderr)

    try:
        resolver = dns.resolver.Resolver()

        if nameservers: 
            ns_list = [nsp for nsp in nameservers.split(",")]

            nameservers_filtered_list = [ns.split(":")[0] for ns in ns_list]
            nameservers_filtered_list_dict = [{ns.split(":")[0]: ns.split(":")[1]} for ns in ns_list if ":" in ns]

            # Set additional nameservers
            if len(nameservers_filtered_list) == 1:
                resolver.nameservers = nameservers_filtered_list[0]
            else:
                resolver.nameservers = nameservers_filtered_list

            # If exists, add nameserver port mapping
            # Limitation: due to an interface limitation, only one nameserver
            # can have a different port
            if nameservers_filtered_list_dict:
                resolver.nameserver_ports = nameservers_filtered_list_dict[0]

        # Query
        answers = resolver.query(fqdn, r_type)

        if verbose:
            rrset = ",".join([str(rr) for rr in answers])
            print(f"DNS query (verbose): FQDN={fqdn} RRtype={r_type} RRset={rrset}", file=sys.stderr)

        return DNSERRORS.NOERROR, answers


    except dns.resolver.NXDOMAIN:
        print(f"DNS query: warning=NXDOMAIN FQDN={fqdn} RRtype={r_type}", file=sys.stderr)
        return DNSERRORS.NXDOMAIN, None

    except dns.resolver.NoAnswer:
        print(f"DNS query: warning=SERVFAIL FQDN={fqdn} RRtype={r_type}", file=sys.stderr)
        return DNSERRORS.SERVFAIL, None

    except dns.exception.Timeout:
        print(f"DNS query: error=TIMEOUT FQDN={fqdn} RRtype={r_type}", file=sys.stderr)
        return DNSERRORS.TIMEOUT, None

    except EOFError:
        print(f"DNS query: error=EOF FQDN={fqdn} RRtype={r_type}", file=sys.stderr)
        return DNSERRORS.ERROR, None

    except Exception as e:
        print(f"DNS query: error='{e}' FQDN={fqdn} RRtype={r_type}", file=sys.stderr)
        return DNSERRORS.ERROR, None
