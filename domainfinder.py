import os
import sys
import whois
import dns.resolver
import time
from datetime import datetime

def read_domains_from_files(filepaths):
    domains = []
    for filepath in filepaths:
        with open(filepath, 'r') as file:
            domains += [line.strip() for line in file.readlines()]
    return domains

def is_domain_available(domain):
    try:
        dns.resolver.resolve(domain, 'A')
        return False
    except dns.resolver.NXDOMAIN:
        return True
    except Exception as e:
        return False

def check_whois(domain):
    try:
        whois_data = whois.whois(domain)
        return bool(whois_data.status)
    except Exception as e:
        return False

def main(filepaths):
    domains = read_domains_from_files(filepaths)
    unclaimed_domains = []
    log_filename = datetime.now().strftime('log_%Y%m%d_%H%M%S.txt')
    whois_requests = 0
    dns_requests = 0
    rate_limit = 10
    whois_interval = 60 / rate_limit

    with open(log_filename, 'w') as log_file:
        for domain in domains:
            log_file.write(f'Checking domain: {domain}\n')
            print(f'Checking domain: {domain}')
            dns_requests += 1
            if is_domain_available(domain):
                log_file.write(f'No DNS records found for {domain}\n')
                print(f'No DNS records found for {domain}')
                if whois_requests > 0 and whois_requests % rate_limit == 0:
                    print(f'Rate limiting: Waiting for {whois_interval} seconds...')
                    time.sleep(whois_interval)
                if not check_whois(domain):
                    whois_requests += 1
                    log_file.write(f'Domain is unclaimed: {domain}\n')
                    print(f'Domain is unclaimed: {domain}')
                    unclaimed_domains.append(domain)
                else:
                    whois_requests += 1
                    log_file.write(f'Domain is claimed (WHOIS): {domain}\n')
                    print(f'Domain is claimed (WHOIS): {domain}')
            else:
                log_file.write(f'Domain is claimed (DNS): {domain}\n')
                print(f'Domain is claimed (DNS): {domain}')

    with open('unclaimed_domains.txt', 'w') as unclaimed_file:
        for domain in unclaimed_domains:
            unclaimed_file.write(f'{domain}\n')

    print(f'\nDNS Requests: {dns_requests}')
    print(f'WHOIS Requests: {whois_requests}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python check_domains.py <file1> [<file2> ...]')
        sys.exit(1)

    main(sys.argv[1:])
