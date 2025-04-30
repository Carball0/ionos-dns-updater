# ionos-dns-updater

Simple Python script that enables a machine to act as a **dynamic DNS updater** for [IONOS](https://www.ionos.com), which updates the A records (IPv4 addresses) of a domain when this address is renewed. 

This solution is ideal for dynamic IP setups such as home servers, VPNs, or self-hosted services via a cron service.


## Features

- Detects your public IPv4 address automatically.
- Updates outdated A records in IONOS DNS zones.
- Optional IP caching to reduce API usage (only when the machine IP changes).
- Can be fully automated via a cron job or controlled with CLI arguments.
- Interactive zone selection if no zone is configured.


## Installation

Two scripts can be found: **ionos-updater.py** (the main script) and **config.py** (needed data for the script to run).

The script uses Python 3, make sure to meet all the dependencies needed (Python3 and pip must be already present):

```bash
pip install requests
```

Also, an API key is necessary for this script to run, check ["Arguments > --api-prefix-and---api-secret"](#arguments) to learn more.

Installation can be done in several ways:

### 1) Set up as a cron job

First of all, the **config.py** script must be correctly set up to run the main script.

1) Edit the **config.py** script and specify your domain name (**zone_name** or **zone_id**), and the API key (**api_key_pubprefix** and **api_key_secret**).
2) Store both scripts somewhere safe and in the same folder. Make sure to set the permissions correctly to protect your private API keys.
3) Open the crontab editor: ```crontab -e```
4) Add a rule at the end of the file, depending on your preferences:

```bash
# Runs every 3 mins, IP address is cached, logs execution -> ! An additional job should be set up to clean regularly
*/3 * * * * /usr/bin/python3 /route/to/ionos-scripts/ionos-updater.py --ip-cache >> /route/to/logs/ionos-log.txt 2>&1

# Runs every 3 mins, IP address is cached, no logs
*/3 * * * * /usr/bin/python3 /route/to/ionos-scripts/ionos-updater.py --ip-cache

# Runs every 45 mins, IP address is NOT cached -> ! Take into account the limits of your API quota
*/30 * * * * /usr/bin/python3 /route/to/ionos-scripts/ionos-updater.py >> /route/to/logs/ionos-log.txt 2>&1

```

Note that ["--ip-cache"](#arguments) is optional, but recommended. See ["Arguments"](#arguments) to learn more about it.


### 2) Running manually

If you want to run the script manually, there are two options: use the provided **config.py** file (recommended) to store your API keys and zone to update, or specify them via command line arguments. Either way, **config.py must be present in the same folder**, if it is not the script will fail to run.

If you want to run it manually **using** the **config.py** file:
1) Edit the **config.py** script and specify your domain name (**zone_name** or **zone_id**), and the API key (**api_key_pubprefix** and **api_key_secret**).
2) Store both scripts somewhere safe and in the same folder. Make sure to set the permissions correctly to protect your private API keys.
3) Run the script: 
```bash
#------Updates specified zone automatically, data retrieved from config.py------
python .\ionos-updater.py --ip-cache
```

If you want to run it manually **without using** the **config.py** file (**via arguments**):
1) Store both scripts somewhere safe and in the same folder. You can leave the **config.py** file as is (**zone_name**, **zone_id**, **api_key_pubprefix** and **api_key_secret** set to None).
2) Run the script specifying the needed arguments (more on arguments [here](#arguments)):

```bash
#------Option 1: Specify only API key - CLI will query your available zones and will prompt you to select one------
python .\ionos-updater.py --ip-cache --api-prefix xxxxxxx --api-secret yyyyyy

#------Option 2: Specify API key and zone to update------
python .\ionos-updater.py --ip-cache --zone-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" --api-prefix xxxxxxx --api-secret yyyyyy
```

You can also specify only the zone ID or zone name without using these arguments if they are specified in the **config.py** file. In this case, the resulting command would be:

```bash
#------Option 3: Specify only zone name------
python .\ionos-updater.py --ip-cache --zone-name example.com

#------Option 4: Specify only zone ID------
python .\ionos-updater.py --ip-cache --zone-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

#------Option 5: CLI will query your available zones and will prompt you to select one------
python .\ionos-updater.py --ip-cache
```

## Arguments
Running ```python .\ionos-updater.py -h``` will give you an overview of the available arguments:

```bash
usage: ionos-updater.py [-h] [--ip-cache] [--zone-name ] [--zone-id ] [--api-prefix ] [--api-secret ]

options:
  -h, --help     show this help message and exit
  --ip-cache     Caches the IP address to a file and compares it every time the program is run. Saves up API requests to check if the A records have changed.
  --zone-name    Specifies the zone name to update
  --zone-id      Specifies the zone id to update (saves one API request)
  --api-prefix   Specifies the API key publicprefix
  --api-secret   Specifies the API key secret
```

### --ip-cache
Caches the system IP to a file in the same folder. Every time the script is run, the system IP will be compared to the one found in this file.

If the current IP and cached IP matches the script aborts its execution, avoiding making API calls and potentially exhausting the API quota.

It is recommended to use this option: ```python .\ionos-updater.py --ip-cache```

### --zone-name and zone_id
To identify which zone will be updated, a zone ID or zone name must be specified.

You can specify either the ID or the zone name in **config.py** > **zone_name** or **zone_id** (recommended), using one of these two arguments: --zone-name and --zone-id.

If you don't have the ID, the zone name is the easiest way to set up the script, for example: ```python .\ionos-updater.py --ip-cache --zone-name example.com```.

The logs will output the zone ID that corresponds to that name, which can be used later instead of the name.

### --api-prefix and --api-secret
IONOS has [its own guide about setting up API keys](https://developer.hosting.ionos.com/docs/getstarted). This is necessary for the script to run, if you don't have a key already you can create one via "IONOS' API Portal"

If you already have your keys, either specify them in **config.py** > **api_key_pubprefix** and **api_key_secret** (recommended) or using these two arguments: --api-prefix and --api-secret.

## Securing your API keys
Make sure your API keys are safely stored in your machine.

The use of the **config.py** file is recommended, as it provides a safe way for storing your API keys without specifying them every time the script is run.

Make sure this file is safely stored in a route that is not accesible to other users (such as www-data or others) and set the permissions correctly:

```bash
sudo chown user12:user12 /route/to/ionos-scripts/*.py
sudo chmod 600 /route/to/ionos-scripts/*.py
```

For additional security, renew your API keys regularly and ensure your API quota usage is coherent with the expected use.