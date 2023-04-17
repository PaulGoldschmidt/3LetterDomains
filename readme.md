![Domain Availability Checker](https://media1.giphy.com/media/B7o99rIuystY4/giphy.gif)
# P3DomainChecker (P3DC): Test for claimed domains and get the domain name of your dreams :stars:
This Python script checks if a list of domains read from one or more external files are claimed or unclaimed. It uses DNS lookups and the whois library to perform the checks and creates a detailed log file with the current date of execution. All unclaimed domains are written to a separate file as plain text. Both files only contain the contents of the last execution. The script also integrates with Telegram to send notifications for newly available domains.

## Disclaimer
Run this script at your own risk, some ISPs really don't like the idea of providing you the A-Records of hundreds(-thousands) domains.

## How the script works

1. Reads domain names from one or multiple input files.
2. Checks if the domain is claimed or unclaimed using a two-step process:
   - First, it performs a DNS lookup for each domain. If DNS records are found, it assumes the domain is claimed.
   - If no DNS records are found, it uses the whois library to check if the domain is registered.
3. Logs the results of the checks in a log file named log_YYYYMMDD_HHMMSS.log, where YYYYMMDD_HHMMSS is the current date and time.
4. Writes all unclaimed domains to a separate file called unclaimed_domains.txt as plain text.
5. Sends a Telegram notification if a new domain becomes available since the last run of the script.

The script is designed to have a rate limit of no more than 10 requests per minute to the whois library, while DNS lookups are executed without any rate limitation. It also provides console output with information on the current status of the script, including the number of domains tried on a DNS level and the list tried against the whois library.

During execution, the script estimates the remaining time and provides elapsed time and percentage of domains tried in the console output. The print-to-console feature can be disabled by providing the --quiet flag when running the script.


## Installation

1. Python 3.6 or higher
2. Install required Python packages by running:

```bash
pip install -r requirements.txt
```

## How to use (self-installed, recommended)

1. Create a credentials.json file in the same directory as the script with your Telegram bot token and chat ID, formatted as follows:

```json
{
  "telegram_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "telegram_chat_id": "YOUR_TELEGRAM_CHAT_ID"
}
```

2. Create one or more text files with a list of domains to check. One domain per line.

3. Run the script by providing the input file(s) as arguments. Optionally, add the --quiet flag to disable console output:

```bash
python check_domains.py input_file1.txt [input_file2.txt ...] [--quiet]
```

4. The script will create a log file in the format log_YYYYMMDD_HHMMSS.log and an unclaimed_domains.txt file with the unclaimed domains.

5. Check the log file and unclaimed_domains.txt file for results.

### Example

Assuming you have a file domains.txt with the following content:

example1.com
example2.com
example3.com

Run the script as follows:

```bash
python check_domains.py domains.txt
```

The script will check the availability of each domain and print the progress to the console. At the end, you will find a log file and an unclaimed_domains.txt file with the results.

## How to install the script as a cronjob

To run the script regularly using a cronjob, follow these steps:

1. Ensure that the script is executable. In the terminal, navigate to the directory containing the script and run:

   ```bash
   chmod +x check_domains.py
   ```

2. Open the crontab configuration file for the current user by running:

   ```bash
   crontab -e
   ```

3. Add a new line to the end of the file with the following format:

   ```bash
   * * * * * /path/to/python3 /path/to/check_domains.py /path/to/input_file1.txt [ /path/to/input_file2.txt ...] [--quiet]
   ```

   Replace `/path/to/python3` with the path to your Python 3 executable (use `which python3` command to find the path), `/path/to/check_domains.py` with the path to the script, and `/path/to/input_file1.txt` with the path to your input file(s). Add additional input files separated by spaces if needed.

   The `* * * * *` part represents the cron schedule. Adjust these values to set the desired frequency of script execution. For example, to run the script every day at midnight, use:

   ```bash
   0 0 * * * /path/to/python3 /path/to/check_domains.py /path/to/input_file1.txt [ /path/to/input_file2.txt ...] [--quiet]
   ```

   To run the script every hour, use:

   ```bash
   0 * * * * /path/to/python3 /path/to/check_domains.py /path/to/input_file1.txt [ /path/to/input_file2.txt ...] [--quiet]
   ```

4. Save and exit the crontab configuration file.

The script will now execute according to the schedule you defined in the cronjob. Note that if you want to disable console output, include the `--quiet` flag at the end of the command.

### Example Script

There is also a [bash example script](p3dc-crontab.sh.example) given that you can run via the crontab instead of the script directly, if you have trouble with the environment variable (crontab has a different environment variable than your local user) not pointing to the correct directory.

## Prebuild executable

You can find an prebuild executable in the GitHub-Actions-Tab of this Repository. There will be an executable to download at the "artifacts"-section of the corresponding Workflow. Use this is at your own risk, I would strongly recommend to use the program directly in python, the installation for that should be straight-foreward.