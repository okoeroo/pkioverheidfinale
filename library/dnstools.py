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
                nameservers: list[str] = None,
                verbose: bool = False) -> tuple[DNSERRORS, str]:

    if verbose:
        print(f"DNS query (verbose): FQDN={fqdn} RRtype={r_type}", file=sys.stderr)

    try:
        resolver = dns.resolver.Resolver()
        if nameservers is not None:
            resolver.nameservers=nameservers.split(",")

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
