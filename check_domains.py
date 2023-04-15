import os
import sys
import whois
import dns.resolver
import time
import json
import requests
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

def load_credentials():
    with open('credentials.json', 'r') as file:
        return json.load(file)

def send_telegram_message(token, chat_id, message):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message}
    response = requests.post(url, json=payload)
    return response.status_code == 200

def load_previous_unclaimed_domains():
    if os.path.exists('unclaimed_domains.txt'):
        with open('unclaimed_domains.txt', 'r') as file:
            return [line.strip() for line in file.readlines()]
    return []

def main(filepaths, print_to_console=True):
    domains = read_domains_from_files(filepaths)
    credentials = load_credentials()
    token = credentials['telegram_token']
    chat_id = credentials['telegram_chat_id']

    unclaimed_domains = []
    previous_unclaimed_domains = load_previous_unclaimed_domains()
    log_filename = datetime.now().strftime('log_%Y%m%d_%H%M%S.log')
    whois_requests = 0
    dns_requests = 0
    rate_limit = 10
    whois_interval = 60 / rate_limit

    start_time = time.time()

    with open(log_filename, 'w') as log_file:
        for i, domain in enumerate(domains):
            if print_to_console:
                print(f'Checking domain: {domain}')
            dns_requests += 1
            if is_domain_available(domain):
                if print_to_console:
                    print(f'No DNS records found for {domain}')
                if whois_requests > 0 and whois_requests % rate_limit == 0:
                    if print_to_console:
                        print(f'Rate limiting: Waiting for {whois_interval} seconds...')
                    time.sleep(whois_interval)
                if not check_whois(domain):
                    whois_requests += 1
                    if print_to_console:
                        print(f'Domain is unclaimed: {domain}')
                    unclaimed_domains.append(domain)
                    if domain not in previous_unclaimed_domains:
                        send_telegram_message(token, chat_id, f'New unclaimed domain: {domain}')
                else:
                    whois_requests += 1
                    log_file.write(f'Domain is claimed (WHOIS): {domain}\n')
                    if print_to_console:
                        print(f'Domain is claimed (WHOIS): {domain}')
            else:
                log_file.write(f'Domain is claimed (DNS): {domain}\n')
                if print_to_console:
                    print(f'Domain is claimed (DNS): {domain}')

            elapsed_time = time.time() - start_time
            estimated_total_time = (elapsed_time / (i + 1)) * len(domains)
            elapsed_time = time.time() - start_time
            estimated_total_time = (elapsed_time / (i + 1)) * len(domains)
            remaining_time = estimated_total_time - elapsed_time
            percentage_done = ((i + 1) / len(domains)) * 100

            if print_to_console:
                print(f'Elapsed time: {elapsed_time:.2f} seconds')
                print(f'Estimated remaining time: {remaining_time:.2f} seconds')
                print(f'Percentage of domains tried: {percentage_done:.2f}%')

    with open('unclaimed_domains.txt', 'w') as unclaimed_file:
        for domain in unclaimed_domains:
            unclaimed_file.write(f'{domain}\n')

    end_time = time.time()
    execution_length = end_time - start_time
    median_requests_per_minute = (dns_requests + whois_requests) / (execution_length / 60)

    with open(log_filename, 'a') as log_file:
        log_file.write(f'\nDNS Requests: {dns_requests}\n')
        log_file.write(f'WHOIS Requests: {whois_requests}\n')
        log_file.write(f'Execution length: {execution_length:.2f} seconds\n')
        log_file.write(f'Median requests per minute: {median_requests_per_minute:.2f}\n')

    if print_to_console:
        print(f'\nDNS Requests: {dns_requests}')
        print(f'WHOIS Requests: {whois_requests}')
        print(f'Execution length: {execution_length:.2f} seconds')
        print(f'Median requests per minute: {median_requests_per_minute:.2f}')

if __name__ == '__main__':
    filepaths = [arg for arg in sys.argv[1:] if arg != '--quiet']

    if not filepaths:
        print('Usage: python check_domains.py <file1> [<file2> ...] [--quiet]')
        sys.exit(1)

    print_to_console = '--quiet' not in sys.argv
    main(filepaths, print_to_console)