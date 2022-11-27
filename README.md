# Domain to IP, Whois and certificate checker.
The prime motivation to write this is to parse a list of hostnames (FQDNs) and create a CSV file as output to process the current state of these.

The output contains the:
- FQDN
- IP address (first A record returned)
- Prefix of the IP address in its AS
- The Autonomous System Number associated to the prefix.
- Country of AS registration
- Registrar
- Last update for the prefix
- Last update for the ASN
- Subject distinghuished name.
  - This is from the certificate found on port 443 using TLS, as with other certificate fields.
- Issuer distinghuished name.
- Common Names
  - Concattenated for the case when there are two CN fields.
- Subject Alternative Names, of the type DNS.
  - Concattenated string.
- Not valid before time of the certificate.
- Not valid after time of the certificate


# Acknowledgements:
The example "pkioverheid.txt" file was created by Hugo Leisink.