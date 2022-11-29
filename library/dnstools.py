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
                nameservers: list[str] = None) -> tuple[DNSERRORS, str]:
    try:
        resolver = dns.resolver.Resolver()
        if nameservers is not None:
            resolver.nameservers=nameservers.split(",")

        answers = resolver.query(fqdn, r_type)

        return DNSERRORS.NOERROR, answers


    except dns.resolver.NXDOMAIN:
        print("DNS query warning: NXDOMAIN.", 'FQDN', fqdn, 'r_type', r_type, file=sys.stderr)
        return DNSERRORS.NXDOMAIN, None

    except dns.resolver.NoAnswer:
        print("DNS query warning: SERVFAIL.", 'FQDN', fqdn, 'r_type', r_type, file=sys.stderr)
        return DNSERRORS.SERVFAIL, None

    except dns.exception.Timeout:
        print("DNS query error: Time out reached.", 'FQDN', fqdn, 'r_type', r_type, file=sys.stderr)
        return DNSERRORS.TIMEOUT, None

    except EOFError:
        print("DNS query error: EOF Error.", 'FQDN', fqdn, 'r_type', r_type, file=sys.stderr)
        return DNSERRORS.ERROR, None

    except Exception as e:
        print("DNS query error:", e, 'FQDN', fqdn, 'r_type', r_type, file=sys.stderr)
        return DNSERRORS.ERROR, None

    except Exception:
        print("DNS query error:", e, 'FQDN', fqdn, 'r_type', r_type, file=sys.stderr)
        return DNSERRORS.ERROR, None
