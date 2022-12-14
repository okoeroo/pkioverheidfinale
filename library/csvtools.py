import re
import csv
import operator
from library.models import FqdnIpWhois


def generate_csv_row_dict(f: FqdnIpWhois) -> dict:
    row = {}

    # Initializer, for reasons of the sorted() feat later.
    row['organisation'] = ''
    row['not_valid_after'] = ''
    row['san_dns_names'] = ''

    
    row['fqdn'] = f.fqdn

    if f.ip is None:
        row['ip'] = 'FAILURE'
    else:
        row['ip'] = f.ip
        
    if f.asn is not None:
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
        row['is_expired'] = 'Yes' if f.cert.is_expired else 'No'
        row['not_valid_before'] = f.cert.not_valid_before
        row['not_valid_after'] = f.cert.not_valid_after
        row['common_names'] = f.cert.common_names
        row['san_dns_names'] = f.cert.san_dns_names
#        row['san_dns_names'] = f.cert.san_dns_names.replace(",", ",\r\n")

        result = re.search('O=([\w\-_ \.\(\)&,\\\\]+),[a-zA-Z]+=', f.cert.subject_dn)
        if result is not None:
            row['organisation'] = result.group(1)

    return row

def processor_convert_list_of_fqdnipwhois2csv(outputfilename: str, fqdns_with_dns: list[FqdnIpWhois]) -> None:
    with open(outputfilename, 'w') as csvfile:
        fieldnames = ['organisation', 'fqdn',
                        'is_expired',
                        'not_valid_before', 'not_valid_after',
                        # 'prefix',
                        'san_dns_names', 
                        'subject_dn', 'issuer_dn',
                        'common_names',
                        'ip', 'prefix',
                        'asn', 'asn_description',
                        'last_update_asn', 'last_update_asn_desc',
                        'country', 'registrar']
    
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()

        rows_to_write = [generate_csv_row_dict(f) for f in fqdns_with_dns]

        rows_to_write.sort(key=operator.itemgetter('san_dns_names'))
        rows_to_write.sort(key=operator.itemgetter('not_valid_after'))
        rows_to_write.sort(key=operator.itemgetter('organisation'))

        for r in rows_to_write:
            csvwriter.writerow(r)
