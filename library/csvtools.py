import csv
from library.models import FqdnIpWhois


def generate_csv_row_dict(f: FqdnIpWhois) -> dict:
    row = {}
    row['fqdn'] = f.fqdn
    if f.ip is None:
        row['ip'] = 'FAILURE'
    else:
        row['ip'] = f.ip
        row['prefix'] = f.asn.prefix
        row['asn'] = f.asn.asn
        row['asn_description'] = f.asn.asn_description.description 
        row['country'] = f.asn.country 
        row['registrar'] = f.asn.registrar 
        row['last_update_asn'] = f.asn.last_update 
        row['last_update_asn_desc'] = f.asn.asn_description.last_update
    
    if f.cert is not None:
        row['subject_dn'] = f.cert.subject_dn
        row['issuer_dn'] = f.cert.issuer_dn

    return row

def processor_convert_list_of_fqdnipwhois2csv(outputfilename: str, fqdns_with_dns: list[FqdnIpWhois]) -> None:
    with open(outputfilename, 'w') as csvfile:
        fieldnames = ['fqdn', 'ip', 'prefix',
                        'asn', 'asn_description', 
                        'country', 'registrar',
                        'last_update_asn', 'last_update_asn_desc',
                        'subject_dn', 'issuer_dn']
    
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()

        for f in fqdns_with_dns:
            csvwriter.writerow(generate_csv_row_dict(f))
