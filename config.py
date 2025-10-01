# External variables for the updater, such as URLs and API keys
# Keep this file somewhere secure and remove all r/w permissions to all users except the owner of ionos-updater.py

# Zone name or ID, specify at least one to automate the process. If None found, it will be asked via CLI
zone_name = None
zone_id = None

# Communication with the IONOS API URL, specify the pubprefix and secret here or provide them via arguments
api_key_pubprefix = None
api_key_secret = None

# --------------------- DO NOT modify ---------------------
public_ip_url = "https://wikipedia.org/"    # URL to obtain public IPv4 address from "x-client-ip" header
                                            # User-Agent header for requests that need it
user_agent = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"}
public_ip_cache = "ip_cache.txt"            # System current IP is written to the file - this avoids making API calls if the system IP does not vary
api_url = "https://api.hosting.ionos.com/dns/v1/zones"
api_headers = {
    "accept": "application/json",
    "X-API-Key": f"{api_key_pubprefix}.{api_key_secret}"
}
# --------------------- DO NOT modify ---------------------