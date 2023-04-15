# P3DomainChecker: Test for claimed domains and get the domain name of your dreams :stars:
A script to check whether a given domain is claimed or not. Can work with multiple input files (domains with TLD seperated by line brake, see [threeletterdomains.txt](example file for three letter .de domains))

## Disclaimer
Run this script at your own risk, some ISPs really don't like the idea of providing you the A-Records of hundreds(-thousands) domains.

## What does this script do?

This script checks whether a list of domains is claimed or unclaimed by performing DNS and WHOIS lookups. It reads domain names from one or more external files, logs the process, and sends a Telegram message if a new unclaimed domain is found since the last script run. The script maintains a list of unclaimed domains in a separate text file.

Overview of the script's functionality:

    1. Read domain names from the specified external files.
    2. Load Telegram API credentials from credentials.json.
    4. Load previously unclaimed domains from unclaimed_domains.txt.
    5. For each domain:
        a. Check if the domain has any DNS A records.
        b. If no DNS records are found, perform a WHOIS lookup while respecting the rate limit of 10 requests per minute.
        c. If the domain is unclaimed and not present in the previous unclaimed domains list, send a Telegram message.
        d. Log the results of DNS and WHOIS checks in a log file.
    6. Update the unclaimed_domains.txt file with the currently unclaimed domains found during the script execution.
    7. Print the total number of DNS and WHOIS requests made during the script execution.

This script helps users monitor domain availability, automatically sending notifications about newly available domains and maintaining an up-to-date list of unclaimed domains.

## Usage