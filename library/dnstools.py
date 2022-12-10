import sys
from enum import Enum
from dataclasses import dataclass, field
import dns.resolver


class DNSERRORS(Enum):
    NOERROR = 1,
    NXDOMAIN = 2,
    SERVFAIL = 3,
    TIMEOUT = 4,
    ERROR = 5


# Very weird config interface, but this is what dnspython does:
# only one port to be set, as the dict only allows for one dict.
@dataclass
class DnsPythonConfig:
    raw: str
    nameservers: list[str] = field(init=False)
    nameservers_port: dict = field(init=False)

    def split_raw_str_to_nameservers_list(self, raw_ns_str) -> list[str]:
        # Split nameservers by comma, and only take the left side of a colon, if
        # it exists
        return [ns.split(":")[0] for ns in raw_ns_str.split(",")]

    def split_raw_str_to_nameserver_port_dict(self, raw_ns_str) -> dict:
        # Split the nameserver by comma, and only for the elements with colon, add
        # the nameserver and port key/value to the dict
        ns_elems_dict = {}
        for ns in raw_ns_str.split(","):
            if ":" in ns:
                ns_elems_dict[ns.split(":")[0]] = int(ns.split(":")[1])

        return ns_elems_dict

    def __post_init__(self):
        raw_ns_str = self.raw

        if raw_ns_str is None:
            raise ValueError("No nameservers provided")

        self.nameservers = self.split_raw_str_to_nameservers_list(self.raw) 
        self.nameservers_port = self.split_raw_str_to_nameserver_port_dict(self.raw)
        

def dns_query(fqdn: str, r_type: str,
                dns_config: DnsPythonConfig,
                verbose: bool = False) -> tuple[DNSERRORS, str]:

    if verbose:
        print(f"DNS query (verbose): FQDN={fqdn} RRtype={r_type}", file=sys.stderr)

    try:
        resolver = dns.resolver.Resolver()

        resolver.nameservers = dns_config.nameservers
        resolver.nameserver_ports = dns_config.nameservers_port

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
