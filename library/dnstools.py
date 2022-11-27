import dns.resolver

def dns_query(fqdn: str, r_type: str):
    try:
        answers = dns.resolver.resolve(fqdn, r_type)
        return answers

    except Exception:
        return None
