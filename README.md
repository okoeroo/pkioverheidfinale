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

# Commandline options
```bash
% ./main.py --help
usage: cli.py [-h] [-v] [--parallel] [-i INPUT_FILENAME] [-o OUTPUT_FILENAME]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose mode. Default is off
  --parallel            Use parallel approachauthentication key.
  -i INPUT_FILENAME, --input-filename INPUT_FILENAME
                        Input filename.
  -o OUTPUT_FILENAME, --output-filename OUTPUT_FILENAME
                        Output filename.
```

# Dependencies
```
pip3 install validators
pip3 install dnspython
pip3 install cryptography
```
Or use the requirements.txt file.


# Example run
```bash
% ./main.py --input-filename samples/pkishort.txt --output-filename samples/short.csv -v
Input filename: samples/pkishort.txt
Output filename: samples/short.csv
```

# Sample input and output
[Input file: pkishort.txt](samples/pkishort.txt)

[Output file: short.csv](samples/short.csv)

# Acknowledgements:
The example "pkioverheid.txt" file was created by Hugo Leisink.
