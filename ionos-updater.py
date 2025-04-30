#!/usr/bin/env python3

# Author: Alejandro Carballo

# HOW TO - GUIDE
# The program must be run alongside the "config.py" file in the same folder, it contains variables necessary for the execution
# The API public prefix and secret can be specified in the "config.py", if they are not present they must be specified using arguments
# For a fully automated process, specify the zone to update in the config file or via arguments. If not present, it will be consulted via an API call and asked in the execution.

from config import *
from argparse import ArgumentParser

import re
import os.path
import requests
import json
import sys
import logging

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(message)s", datefmt="%b %d %H:%M:%S -", level=logging.INFO)

def main():
    ipv4_addr = get_ipv4_addr()
    logging.info("Current public IPv4 address: " + ipv4_addr)
    
    if args.ip_cache and get_match_cached_ipv4(ipv4_addr):
        logging.info("Cached IP matches the current IP, no API calls were made: " + ipv4_addr)
        exit()

    selected_zone_id = zone_id or args.zone_id
    if selected_zone_id is None:
        zones = get_zones()
        if zone_name or args.zone_name:
            selected_zone_id = obtain_zone_id_from_name(zone_name or args.zone_name, zones)
        else:
            selected_zone_id = obtain_zone_to_update(zones)

    print(selected_zone_id, zones, zone_name, args.zone_name)
    records = get_records_from_zone(selected_zone_id)

    if records:
        update_arr = []
        for record in records:
            if record["content"] != ipv4_addr:
                logging.info(f"{record['name']} - A record is outdated: {record['content']}")
                update_arr.append({"name": record["name"], "type": "A", "content": ipv4_addr})
        if (len(update_arr) > 0):
            update_records_from_zone(selected_zone_id, update_arr)
            logging.info(f"All selected A records have been updated")
        else:
            logging.info(f"No A records are outdated, records left intact")
    else:
        logging.error(f"No A records found for this zone, try again")

def arg_parser():
    argparser = ArgumentParser()
    argparser.add_argument(
        "--ip-cache",
        required=False,
        action="store_true",
        help="Caches the IP address to a file and compares it every time the program is run. Saves up API requests to check if the A records have changed."
    )
    argparser.add_argument(
        "--zone-name",
        required=False,
        action="store",
        metavar="",
        help="Specifies the zone name to update"
    )
    argparser.add_argument(
        "--zone-id",
        required=False,
        action="store",
        metavar="",
        help="Specifies the zone id to update (saves one API request)"
    )
    argparser.add_argument(
        "--api-prefix",
        required=False,
        action="store",
        metavar="",
        help="Specifies the API key publicprefix"
    )
    argparser.add_argument(
        "--api-secret",
        required=False,
        action="store",
        metavar="",
        help="Specifies the API key secret"
    )

    args = argparser.parse_args()

    return args

# Returns wether the stored IPv4 address from the last execution is the same as the current system IPv4 address
def get_match_cached_ipv4(ipv4_addr_current):
    try:
        if not os.path.exists(public_ip_cache):
            write_to_file(public_ip_cache, ipv4_addr_current)
            return False
        else:
            fp = open(public_ip_cache, 'r')
            ipv4_addr_old = fp.readlines()[0]
            fp.close()
            write_to_file(public_ip_cache, ipv4_addr_current)
    except Exception as err:
        logging.error(f"R/W error while accesing the IP cache file, ip-cache option is disabled: {err}")
        return False
    
    return ipv4_addr_current == ipv4_addr_old

def write_to_file(path, content):
    fp = open(path, 'w')
    fp.seek(0)
    fp.write(content)
    fp.close()

# Obtains zone to update from the config file
def obtain_zone_to_update(zones):
    selected_zone_id = ""
    if len(zones) > 0 and zones[0] and zones[0]["id"]:
        zones_str = "\n"
        for i in range(len(zones)):
            zones_str = zones_str + str(i+1) + ") "+ zones[i]["name"] + "\n"
        sel_zone_num = input("Which zone would you like to update (number): "+zones_str)
        regex = r"[0-9]*"
        if re.search(regex, sel_zone_num) is not None and int(sel_zone_num) <= len(zones) and int(sel_zone_num) > 0:
            selected_zone_id = zones[int(sel_zone_num)-1]["id"]
        else:
            logging.error(f"Invalid option, closing...")
            exit()
        selected_zone_id = zones[0]["id"]
    else:
        logging.error(f"No zones found, check the specified API keys")
        exit()
    return selected_zone_id

def obtain_zone_id_from_name(zone_name, zones):
    zone = list(filter(lambda zone: zone["name"] == zone_name, zones))
    if len(zone) == 1 and zone[0]:
        return zone[0]["id"]
    else:
        logging.error(f"No zones found for the specicified name")
        exit()

def get_ipv4_addr():
    return requests.head(public_ip_url).headers["x-client-ip"]

def get_zones():
    return json.loads(requests.request("GET", api_url, headers=api_headers).text)

def get_records_from_zone(zone_id):
    url = f"{api_url}/{zone_id}"
    records = json.loads(requests.request("GET", url, headers=api_headers).text)["records"]
    return list(filter(lambda record: record["type"] == "A", records))

def update_records_from_zone(zone_id, records):
    url = f"{api_url}/{zone_id}"
    return requests.request("PATCH", url, headers=api_headers, json=records)


# Previous verifications and execution
args = arg_parser()
if not public_ip_url or not api_url or not api_headers or not public_ip_cache:
    logging.error(f"Invalid config file, try again")
    exit()
if not api_key_pubprefix or not api_key_secret:
    if args.api_prefix and args.api_secret:
        api_key_pubprefix = args.api_prefix
        api_key_secret = args.api_secret
    else:
        logging.error(f"No API keys found, use the config file or specify them as arguments")
        exit()

try:
    main()
except Exception as err:
    logging.error(f"Raised exception: {err}")
    write_to_file(public_ip_cache, "NaN")
except KeyboardInterrupt:
    logging.info(f"User aborted")
    write_to_file(public_ip_cache, "NaN")