# P3DC - 16th of April, 2023 - Paul Goldschmidt | Version 1.3
import argparse
import dns.resolver
import glob
import json
import os
import platform
import requests
import sys
import time
from datetime import datetime
from whois import whois
from whois.parser import PywhoisError


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
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    return response.status_code == 200

def send_initial_telegram_message(token, chat_id, filepaths, total_domains, machine_info):
    message = f'<b>📝 Domain Check Started!</b>\n\n'
    message += f'<b>📂 Files to check ({len(filepaths)}):</b> \n'
    countdomainstemp = 0
    for filepath in filepaths:
        message += f'- {os.path.basename(filepath)}\n'
        with open(filepath, 'r') as f:
            countdomainstemp = [line.strip() for line in f.readlines()]
            total_domains = total_domains + len(countdomainstemp)
    message += f'\n<b>☝️ Total domains to check:</b> {total_domains}\n'
    message += f'\n<b>🤖 Machine info:</b>\n{machine_info}'

    send_telegram_message(token, chat_id, message)

def main(filepaths, print_to_console=True):
    with open('credentials.json', 'r') as f:
        credentials = json.load(f)
        telegram_token = credentials['telegram_token']
        telegram_chat_id = credentials['telegram_chat_id']
        machine_info = f'{platform.system()} {platform.release()} ({platform.version()})'


    if not os.path.exists('logs'):
        os.makedirs('logs')
    if not os.path.exists('results'):
        os.makedirs('results')

    log_filename = f'logs/{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    log_file = open(log_filename, 'w')

    dns_checked_domains = 0
    whois_checked_domains = 0
    start_time = time.time()
    total_domains = 0
    send_initial_telegram_message(telegram_token, telegram_chat_id, filepaths, total_domains, machine_info)
    
    for filepath in filepaths:
        previous_unclaimed_domains = []
        result_filename = f'unclaimed_{os.path.splitext(os.path.basename(filepath))[0]}.txt'

        previous_result_filename = f'unclaimed_{os.path.splitext(os.path.basename(filepath))[0]}.txt'
        previous_result_files = sorted(glob.glob(os.path.join('results', previous_result_filename)))

        if previous_result_files:
            with open(previous_result_files[-1], 'r') as f:
                previous_unclaimed_domains = [line.strip() for line in f.readlines()]

        unclaimed_domains = []
        with open(filepath, 'r') as f:
            domains = [line.strip() for line in f.readlines()]

        unclaimed_file = open(os.path.join('results', result_filename), 'w')

        for i, domain in enumerate(domains):
            if print_to_console:
                print(f'Checking domain: {domain}')
            dns_checked_domains += 1
            if is_domain_available(domain):
                if domain not in previous_unclaimed_domains:
                    try:
                        whois_checked_domains += 1
                        domain_info = whois(domain)
                        time.sleep(6)

                        if domain_info.status is None:
                            unclaimed_domains.append(domain)
                            unclaimed_file.write(f'{domain}\n')

                            if print_to_console:
                                print(f'Domain is unclaimed: {domain}')
                        else:
                            log_file.write(f'Domain is claimed (WHOIS): {domain}\n')

                    except PywhoisError as e:
                        log_file.write(f'Error (WHOIS): {domain}, {e}\n')
                        unclaimed_domains.append(domain)
                        unclaimed_file.write(f'{domain}\n')

                    except Exception as e:
                        log_file.write(f'Error (WHOIS): {domain}, {e}\n')
                        unclaimed_domains.append(domain)
                        unclaimed_file.write(f'{domain}\n')

                else:
                    unclaimed_domains.append(domain)
                    unclaimed_file.write(f'{domain}\n')

            elapsed_time = time.time() - start_time
            estimated_total_time = (elapsed_time / (i + 1)) * len(domains)
            remaining_time = estimated_total_time - elapsed_time
            if print_to_console:
                print(f'Progress: {((i + 1) / len(domains)) * 100:.2f}%, Elapsed time: {elapsed_time:.2f}s, Remaining time: {remaining_time:.2f}s')

        unclaimed_file.close()

        new_unclaimed_domains = list(set(unclaimed_domains) - set(previous_unclaimed_domains))
        if new_unclaimed_domains:
            message = f'✨ New unclaimed domains:\n\n'
            message += '\n'.join(new_unclaimed_domains)
            send_telegram_message(telegram_token, telegram_chat_id, message)

        if print_to_console:
            print(f'\nFinished checking {len(domains)} domains for file {filepath}.')
            print(f'DNS checked domains: {dns_checked_domains}')
            print(f'WHOIS checked domains: {whois_checked_domains}')

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
    log_file.write(f'Script version: 1.3.0\n')

    log_file.close()

    if print_to_console:
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
