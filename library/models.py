from dataclasses import dataclass
from cryptography import x509


@dataclass
class SimplifiedCertificate:
    subject_dn: str
    issuer_dn: str
    serial_nr: str
    pem: str   
    certificate: x509.Certificate 

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
    cert: SimplifiedCertificate | None = None