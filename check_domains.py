import sys
import os
import json
import time
from datetime import datetime
import dns.resolver
import whois
import requests
import argparse
import platform
import glob


def is_domain_available(domain):
    try:
        dns.resolver.resolve(domain, 'A')
        return False
    except dns.resolver.NXDOMAIN:
        return True
    except Exception as e:
        return False


def send_telegram_message(token, chat_id, message):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
    }
    requests.post(url, data=payload)


def rotate_logs():
    log_files = sorted(glob.glob(os.path.join('logs', 'log_*.log')))
    while len(log_files) > 30:
        os.remove(log_files.pop(0))


def main(filepaths, print_to_console=True):
    if not os.path.exists('logs'):
        os.makedirs('logs')

    rotate_logs()

    with open('credentials.json', 'r') as f:
        credentials = json.load(f)

    telegram_token = credentials['telegram_token']
    telegram_chat_id = credentials['telegram_chat_id']

    domains = []
    for filepath in filepaths:
        with open(filepath, 'r') as f:
            domains += [line.strip() for line in f.readlines()]

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = open(os.path.join('logs', f'log_{timestamp}.log'), 'w')
    unclaimed_file = open('unclaimed_domains.txt', 'w')

    start_time = time.time()
    dns_checked_domains = 0
    whois_checked_domains = 0
    unclaimed_domains = []

    previous_unclaimed_domains = []
    if os.path.exists('unclaimed_domains.txt'):
        with open('unclaimed_domains.txt', 'r') as f:
            previous_unclaimed_domains = [line.strip() for line in f.readlines()]

    for i, domain in enumerate(domains):
        if print_to_console:
            print(f'Checking domain {i + 1}/{len(domains)}: {domain}')

        if is_domain_available(domain) and domain not in previous_unclaimed_domains:
            try:
                domain_info = whois.whois(domain)
                whois_checked_domains += 1
                time.sleep(6)  # Rate limit: 10 requests per minute

                if domain_info.status is None:
                    unclaimed_domains.append(domain)
                    unclaimed_file.write(f'{domain}\n')
            except Exception as e:
                if print_to_console:
                    print(f'Error checking domain (WHOIS): {domain} - {str(e)}')
                log_file.write(f'Error checking domain (WHOIS): {domain} - {str(e)}\n')
                unclaimed_domains.append(domain)
                unclaimed_file.write(f'{domain}\n')
        else:
            dns_checked_domains += 1

        elapsed_time = time.time() - start_time
        estimated_total_time = (elapsed_time / (i + 1)) * len(domains)
        remaining_time = estimated_total_time - elapsed_time

        if print_to_console:
            print(f'Elapsed time: {elapsed_time:.2f}s - Estimated total time: {estimated_total_time:.2f}s - Remaining time: {remaining_time:.2f}s')
            print(f'Progress: {((i + 1) / len(domains)) * 100:.2f}%')

    end_time = time.time()
    execution_time = end_time - start_time
    median_domains_per_minute = len(domains) / (execution_time / 60)

    log_file.write(f'Start time: {datetime.fromtimestamp(start_time)}\n')
    log_file.write(f'End time: {datetime.fromtimestamp(end_time)}\n')
    log_file.write(f'Total tried domains: {len(domains)}\n')
    log_file.write(f'DNS checked domains: {dns_checked_domains}\n')
    log_file.write(f'WHOIS checked domains: {whois_checked_domains}\n')
    log_file.write(f'Execution time: {execution_time:.2f}s\n')
    log_file.write(f'Median domains checked per minute: {median_domains_per_minute:.2f}\n')
    log_file.write(f'Machine info: {platform.uname()}\n')
    log_file.write(f'Script version: 1.0.0\n')

    log_file.close()
    unclaimed_file.close()

    new_unclaimed_domains = list(set(unclaimed_domains) - set(previous_unclaimed_domains))
    if new_unclaimed_domains:
        message = f'New unclaimed domains:\n\n'
        message += '\n'.join(new_unclaimed_domains)
        send_telegram_message(telegram_token, telegram_chat_id, message)

    if print_to_console:
        print(f'\nFinished checking {len(domains)} domains.')
        print(f'DNS checked domains: {dns_checked_domains}')
        print(f'WHOIS checked domains: {whois_checked_domains}')
        print(f'Execution time: {execution_time:.2f}s')
        print(f'Median domains checked per minute: {median_domains_per_minute:.2f}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*', help='List of files containing domain names to check')
    parser.add_argument('--quiet', action='store_true', help='Disable console output')
    args = parser.parse_args()

    if not args.files:
        print('Usage: python check_domains.py <file1> [<file2> ...] [--quiet]')
        sys.exit(1)

    main(args.files, not args.quiet)