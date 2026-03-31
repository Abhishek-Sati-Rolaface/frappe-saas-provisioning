# # saas_manager/api/signup.py
# import frappe
# import subprocess

# CADDYFILE_PATH = "/etc/caddy/Caddyfile"
# BENCH_SITES_PATH = "/srv/apps/erp/backend/master-bench/sites"

# def add_caddy_domain(site_name: str):
#     """
#     Appends a new site block to Caddyfile and reloads Caddy.
#     Called after bench new-site succeeds.
#     """
#     # 1. Read current Caddyfile
#     with open(CADDYFILE_PATH, "r") as f:
#         content = f.read()

#     # 2. Check if domain already exists (avoid duplicates)
#     if site_name in content:
#         frappe.logger().info(f"Caddy: {site_name} already exists, skipping.")
#         return

#     # 3. Build the new Caddy block
#     new_block = (
#         f"\n{site_name} {{\n"
#         f"\n"
#         f"    @assets path /assets/*\n"
#         f"    root * {BENCH_SITES_PATH}\n"
#         f"    file_server @assets\n"
#         f"\n"
#         f"    @files path /files/*\n"
#         f"    root * {BENCH_SITES_PATH}/{site_name}\n"
#         f"    file_server @files\n"
#         f"\n"
#         f"    reverse_proxy 127.0.0.1:8004\n"
#         f"}}\n"
#     )

#     # 4. Append to Caddyfile using sudo tee -a (no overwrite)
#     write_proc = subprocess.run(
#         ["sudo", "tee", "-a", CADDYFILE_PATH],
#         input=new_block,
#         capture_output=True,
#         text=True
#     )

#     if write_proc.returncode != 0:
#         frappe.log_error(f"Caddyfile write failed: {write_proc.stderr}", "Caddy Error")
#         frappe.throw("Failed to write Caddy config. Contact support.")

#     # 5. Reload Caddy
#     reload_proc = subprocess.run(
#         ["sudo", "/usr/bin/caddy", "reload", "--config", CADDYFILE_PATH],
#         capture_output=True,
#         text=True
#     )

#     if reload_proc.returncode != 0:
#         frappe.log_error(f"Caddy reload failed: {reload_proc.stderr}", "Caddy Error")
#         frappe.throw("Failed to reload Caddy. Contact support.")

#     frappe.logger().info(f"Caddy: {site_name} added and reloaded successfully.")


# import frappe
# import subprocess
# import requests

# CADDYFILE_PATH = "/etc/caddy/Caddyfile"
# BENCH_SITES_PATH = "/srv/apps/erp/backend/master-bench/sites"

# def get_config():
#     return {
#         "token": frappe.conf.get("hostinger_api_token", "YGoCmpvmNkVKu59EkX2MlbqejhiCTzDbkmj6PJvN80b0903f"),
#         "domain": frappe.conf.get("saas_domain", "rolaface.com"),
#         "server_ip": frappe.conf.get("server_ip", "72.60.102.130"),
#     }

# def add_dns_record(subdomain: str):
#     conf = get_config()
#     url = f"https://developers.hostinger.com/api/dns/v1/zones/{conf['domain']}"
#     headers = {
#         "Authorization": f"Bearer {conf['token']}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "overwrite": False,
#         "zone": [
#             {
#                 "name": subdomain,
#                 "type": "A",
#                 "records": [{"content": conf["server_ip"], "ttl": 300}]
#             }
#         ]
#     }
#     response = requests.put(url, json=payload, headers=headers)
#     if response.status_code not in (200, 201, 202):
#         frappe.log_error(f"DNS API error: {response.text}", "DNS Error")
#         frappe.throw(f"Failed to add DNS record: {response.text}")
#     frappe.logger().info(f"DNS: A record added for {subdomain}.{conf['domain']}")

# def add_caddy_domain(site_name: str):
#     conf = get_config()

#     # 1. Add DNS record
#     subdomain = site_name.replace(f".{conf['domain']}", "")
#     add_dns_record(subdomain)

#     # 2. Read current Caddyfile
#     with open(CADDYFILE_PATH, "r") as f:
#         content = f.read()

#     # 3. Check if domain already exists
#     if site_name in content:
#         frappe.logger().info(f"Caddy: {site_name} already exists, skipping.")
#         return

#     # 4. Build the new Caddy block
#     new_block = (
#         f"\n{site_name} {{\n"
#         f"\n"
#         f"    handle /assets/* {{\n"
#         f"        root * {BENCH_SITES_PATH}\n"
#         f"        file_server\n"
#         f"    }}\n"
#         f"\n"
#         f"    handle /files/* {{\n"
#         f"        root * {BENCH_SITES_PATH}/{site_name}\n"
#         f"        file_server\n"
#         f"    }}\n"
#         f"\n"
#         f"    handle {{\n"
#         f"        reverse_proxy 127.0.0.1:8004\n"
#         f"    }}\n"
#         f"}}\n"
# )

#     # 5. Append to Caddyfile using sudo tee -a
#     write_proc = subprocess.run(
#         ["sudo", "tee", "-a", CADDYFILE_PATH],
#         input=new_block,
#         capture_output=True,
#         text=True
#     )
#     if write_proc.returncode != 0:
#         frappe.log_error(f"Caddyfile write failed: {write_proc.stderr}", "Caddy Error")
#         frappe.throw("Failed to write Caddy config. Contact support.")

#     # 6. Reload Caddy
#     reload_proc = subprocess.run(
#         ["sudo", "/usr/bin/caddy", "reload", "--config", CADDYFILE_PATH],
#         capture_output=True,
#         text=True
#     )
#     if reload_proc.returncode != 0:
#         frappe.log_error(f"Caddy reload failed: {reload_proc.stderr}", "Caddy Error")
#         frappe.throw("Failed to reload Caddy. Contact support.")

#     frappe.logger().info(f"Caddy: {site_name} added and reloaded successfully.")



# import frappe
# import subprocess
# import requests

# CADDYFILE_PATH = "/etc/caddy/Caddyfile"
# BENCH_SITES_PATH = "/srv/apps/erp/backend/master-bench/sites"
# FRONTEND_PORT = 3005  # React app port

# def get_config():
#     return {
#         "token": frappe.conf.get("hostinger_api_token", "YGoCmpvmNkVKu59EkX2MlbqejhiCTzDbkmj6PJvN80b0"),
#         "domain": frappe.conf.get("saas_domain", "rolaface.com"),
#         "server_ip": frappe.conf.get("server_ip", "72.60.102.130"),
#     }


# def add_dns_record(subdomain: str):
#     """Add A record in Hostinger DNS."""
#     conf = get_config()
#     url = f"https://developers.hostinger.com/api/dns/v1/zones/{conf['domain']}"
#     headers = {
#         "Authorization": f"Bearer {conf['token']}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "overwrite": False,
#         "zone": [
#             {
#                 "name": subdomain,
#                 "type": "A",
#                 "records": [{"content": conf["server_ip"], "ttl": 300}]
#             }
#         ]
#     }
#     response = requests.put(url, json=payload, headers=headers)
#     if response.status_code not in (200, 201, 202):
#         frappe.log_error(f"DNS API error: {response.text}", "DNS Error")
#         frappe.throw(f"Failed to add DNS record: {response.text}")
#     frappe.logger().info(f"DNS: A record added for {subdomain}.{conf['domain']}")


# def add_caddy_domain(site_name: str):
#     """
#     site_name = api.erp.rolaerpnew32.rolaface.com
#     company   = rolaerpnew32
#     backend   = api.erp.rolaerpnew32.rolaface.com
#     frontend  = rolaerpnew32.erp.rolaface.com
#     """
#     conf = get_config()
#     domain = conf["domain"]

#     # Extract company name from site_name
#     # api.erp.rolaerpnew32.rolaface.com → rolaerpnew32
#     company = site_name.replace(f".{domain}", "").replace("api.erp.", "")

#     backend_domain = f"api.erp.{company}.{domain}"   # api.erp.rolaerpnew32.rolaface.com
#     frontend_domain = f"{company}.erp.{domain}"       # rolaerpnew32.erp.rolaface.com

#     # 1. Add DNS records
#     add_dns_record(f"api.erp.{company}")  # api.erp.rolaerpnew32
#     add_dns_record(f"{company}.erp")      # rolaerpnew32.erp

#     # 2. Check for duplicates
#     with open(CADDYFILE_PATH, "r") as f:
#         content = f.read()

#     if backend_domain in content:
#         frappe.logger().info(f"Caddy: {backend_domain} already exists, skipping.")
#         return

#     # 3. Backend block — api.erp.rolaerpnew32.rolaface.com
#     backend_block = (
#         f"\n{backend_domain} {{\n"
#         f"\n"
#         f"    handle /assets/* {{\n"
#         f"        root * {BENCH_SITES_PATH}\n"
#         f"        file_server\n"
#         f"    }}\n"
#         f"\n"
#         f"    handle /files/* {{\n"
#         f"        root * {BENCH_SITES_PATH}/{backend_domain}\n"
#         f"        file_server\n"
#         f"    }}\n"
#         f"\n"
#         f"    handle /socket.io/* {{\n"
#         f"        reverse_proxy 127.0.0.1:9004\n"
#         f"    }}\n"
#         f"\n"
#         f"    handle {{\n"
#         f"        reverse_proxy 127.0.0.1:8004 {{\n"
#         f"            header_up Host {backend_domain}\n"
#         f"        }}\n"
#         f"    }}\n"
#         f"}}\n"
#     )

#     # 4. Frontend block — rolaerpnew32.erp.rolaface.com
#     frontend_block = (
#         f"\n{frontend_domain} {{\n"
#         f"    encode zstd gzip\n"
#         f"    reverse_proxy localhost:{FRONTEND_PORT}\n"
#         f"}}\n"
#     )

#     # 5. Append both blocks to Caddyfile
#     all_blocks = backend_block + frontend_block
#     write_proc = subprocess.run(
#         ["sudo", "tee", "-a", CADDYFILE_PATH],
#         input=all_blocks,
#         capture_output=True,
#         text=True
#     )

#     if write_proc.returncode != 0:
#         frappe.log_error(f"Caddyfile write failed: {write_proc.stderr}", "Caddy Error")
#         frappe.throw("Failed to write Caddy config. Contact support.")

#     # 6. Reload Caddy
#     reload_proc = subprocess.run(
#         ["sudo", "/usr/bin/caddy", "reload", "--config", CADDYFILE_PATH],
#         capture_output=True,
#         text=True
#     )

#     if reload_proc.returncode != 0:
#         frappe.log_error(f"Caddy reload failed: {reload_proc.stderr}", "Caddy Error")
#         frappe.throw("Failed to reload Caddy. Contact support.")

#     frappe.logger().info(f"Caddy: {backend_domain} and {frontend_domain} added successfully.")




import frappe
import subprocess
import requests

CADDYFILE_PATH = "/etc/caddy/Caddyfile"
BENCH_SITES_PATH = "/srv/apps/erp/backend/master-bench/sites"
FRONTEND_PORT = 3005  # React app port


def get_config():
    return {
        "token": frappe.conf.get("hostinger_api_token", "YGoCmpvmNkVKu59EkX2MlbqejhiCTzDbkmj6PJvN80b0"),
        "domain": frappe.conf.get("saas_domain", "rolaface.com"),
        "server_ip": frappe.conf.get("server_ip", "72.60.102.130"),
    }


def add_dns_record(subdomain: str):
    """
    subdomain = api.erp.rolaerpnew32  (without the root domain)
    Creates an A record pointing to server_ip
    """
    conf = get_config()
    domain = conf["domain"]
    token = conf["token"]
    server_ip = conf["server_ip"]

    # url = f"https://api.hostinger.com/v1/dns/zones/{domain}/records"
    url = f"https://developers.hostinger.com/api/dns/v1/zones/{conf['domain']}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "type": "A",
        "name": subdomain,
        "content": server_ip,
        "ttl": 3600
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code in (200, 201):
            frappe.logger().info(f"DNS: A record added for {subdomain}.{domain} → {server_ip}")
        elif response.status_code == 422:
            # Record already exists — not an error
            frappe.logger().info(f"DNS: A record for {subdomain}.{domain} already exists, skipping.")
        else:
            frappe.log_error(
                f"DNS add failed for {subdomain}.{domain}: {response.status_code} {response.text}",
                "DNS Error"
            )
            frappe.throw(f"Failed to add DNS record for {subdomain}.{domain}")

    except requests.exceptions.RequestException as e:
        frappe.log_error(f"DNS request error for {subdomain}.{domain}: {str(e)}", "DNS Error")
        frappe.throw(f"DNS request failed for {subdomain}.{domain}")


def add_caddy_domain(site_name: str):
    """
    site_name = api.erp.rolaerpnew32.rolaface.com
    company   = rolaerpnew32
    backend   = api.erp.rolaerpnew32.rolaface.com
    frontend  = rolaerpnew32.erp.rolaface.com
    """
    conf = get_config()
    domain = conf["domain"]

    # Extract company name from site_name
    # api.erp.rolaerpnew32.rolaface.com → rolaerpnew32
    company = site_name.replace(f".{domain}", "").replace("api.erp.", "")

    backend_domain = f"api.erp.{company}.{domain}"   # api.erp.rolaerpnew32.rolaface.com
    frontend_domain = f"{company}.erp.{domain}"       # rolaerpnew32.erp.rolaface.com

    # 1. Add DNS records
    add_dns_record(f"api.erp.{company}")  # api.erp.rolaerpnew32
    add_dns_record(f"{company}.erp")      # rolaerpnew32.erp

    # 2. Check for duplicates
    with open(CADDYFILE_PATH, "r") as f:
        content = f.read()

    if backend_domain in content:
        frappe.logger().info(f"Caddy: {backend_domain} already exists, skipping.")
        return

    # 3. Backend block — api.erp.rolaerpnew32.rolaface.com
    # backend_block = (
    #     f"\n{backend_domain} {{\n"
    #     f"\n"
    #     f"    encode zstd gzip\n"
    #     f"\n"
    #     f"    header {{\n"
    #     f"        Access-Control-Allow-Origin \"https://{frontend_domain}\"\n"
    #     f"        Access-Control-Allow-Methods \"GET, POST, PUT, PATCH, DELETE, OPTIONS\"\n"
    #     f"        Access-Control-Allow-Headers \"Origin, Accept, Content-Type, Authorization, X-Frappe-Site-Name\"\n"
    #     f"        Access-Control-Allow-Credentials true\n"
    #     f"        defer\n"
    #     f"    }}\n"
    #     f"\n"
    #     f"    @options method OPTIONS\n"
    #     f"    respond @options 204\n"
    #     f"\n"
    #     f"    @private path /private/*\n"
    #     f"    respond @private 403\n"
    #     f"\n"
    #     f"    @assets path /assets/*\n"
    #     f"    handle @assets {{\n"
    #     f"        root * {BENCH_SITES_PATH}\n"
    #     f"        file_server\n"
    #     f"    }}\n"
    #     f"\n"
    #     f"    @files path /files/*\n"
    #     f"    handle @files {{\n"
    #     f"        root * {BENCH_SITES_PATH}/{backend_domain}\n"
    #     f"        file_server\n"
    #     f"    }}\n"
    #     f"\n"
    #     f"    @socketio path /socket.io/*\n"
    #     f"    reverse_proxy @socketio 127.0.0.1:9004 {{\n"
    #     f"        header_up Host {{host}}\n"
    #     f"        header_up X-Frappe-Site-Name {backend_domain}\n"
    #     f"        header_up X-Real-IP {{remote}}\n"
    #     f"        header_down -Access-Control-Allow-Origin\n"
    #     f"        header_down -Access-Control-Allow-Methods\n"
    #     f"        header_down -Access-Control-Allow-Headers\n"
    #     f"        header_down -Access-Control-Allow-Credentials\n"
    #     f"        header_down -Access-Control-Max-Age\n"
    #     f"        header_down -Vary\n"
    #     f"    }}\n"
    #     f"\n"
    #     f"    reverse_proxy 127.0.0.1:8004 {{\n"
    #     f"        header_up Host {{host}}\n"
    #     f"        header_up X-Frappe-Site-Name {backend_domain}\n"
    #     f"        header_up X-Real-IP {{remote}}\n"
    #     f"        header_down -Access-Control-Allow-Origin\n"
    #     f"        header_down -Access-Control-Allow-Methods\n"
    #     f"        header_down -Access-Control-Allow-Headers\n"
    #     f"        header_down -Access-Control-Allow-Credentials\n"
    #     f"        header_down -Access-Control-Max-Age\n"
    #     f"        header_down -Vary\n"
    #     f"    }}\n"
    #     f"}}\n"
    # )


    # 3. Backend block — api.erp.rolaerpnew32.rolaface.com
    backend_block = (
        f"\n{backend_domain} {{\n"
        f"\n"
        f"    encode zstd gzip\n"
        f"\n"
        f"    header {{\n"
        f"        Access-Control-Allow-Origin \"https://{frontend_domain}\"\n"
        f"        Access-Control-Allow-Methods \"GET, POST, PUT, PATCH, DELETE, OPTIONS\"\n"
        f"        Access-Control-Allow-Headers \"Origin, Accept, Content-Type, Authorization, X-Frappe-Site-Name\"\n"
        f"        Access-Control-Allow-Credentials true\n"
        f"        defer\n"
        f"    }}\n"
        f"\n"
        f"    @options method OPTIONS\n"
        f"    respond @options 204\n"
        f"\n"
        f"    @socketio path /socket.io/*\n"
        f"    reverse_proxy @socketio 127.0.0.1:9000 {{\n"
        f"        header_up Host {{host}}\n"
        f"        header_up X-Frappe-Site-Name {backend_domain}\n"
        f"        header_up X-Real-IP {{remote}}\n"
        f"        header_down -Access-Control-Allow-Origin\n"
        f"        header_down -Access-Control-Allow-Methods\n"
        f"        header_down -Access-Control-Allow-Headers\n"
        f"        header_down -Access-Control-Allow-Credentials\n"
        f"        header_down -Access-Control-Max-Age\n"
        f"        header_down -Vary\n"
        f"    }}\n"
        f"\n"
        f"    @private path /private/*\n"
        f"    respond @private 403\n"
        f"\n"
        f"    handle /assets/* {{\n"
        f"        root * {BENCH_SITES_PATH}\n"
        f"        file_server\n"
        f"    }}\n"
        f"\n"
        f"    handle /files/* {{\n"
        f"        root * {BENCH_SITES_PATH}/{backend_domain}/public\n"
        f"        file_server\n"
        f"    }}\n"
        f"\n"
        f"    handle {{\n"
        f"        reverse_proxy 127.0.0.1:8004 {{\n"
        f"            header_up Host {{host}}\n"
        f"            header_up X-Frappe-Site-Name {backend_domain}\n"
        f"            header_up X-Real-IP {{remote}}\n"
        f"            header_down -Access-Control-Allow-Origin\n"
        f"            header_down -Access-Control-Allow-Methods\n"
        f"            header_down -Access-Control-Allow-Headers\n"
        f"            header_down -Access-Control-Allow-Credentials\n"
        f"            header_down -Access-Control-Max-Age\n"
        f"            header_down -Vary\n"
        f"        }}\n"
        f"    }}\n"
        f"}}\n"
    )

    # 4. Frontend block — rolaerpnew32.erp.rolaface.com
    frontend_block = (
        f"\n{frontend_domain} {{\n"
        f"    encode zstd gzip\n"
        f"    reverse_proxy localhost:{FRONTEND_PORT}\n"
        f"}}\n"
    )

    # 5. Append both blocks to Caddyfile
    all_blocks = backend_block + frontend_block
    write_proc = subprocess.run(
        ["sudo", "tee", "-a", CADDYFILE_PATH],
        input=all_blocks,
        capture_output=True,
        text=True
    )

    if write_proc.returncode != 0:
        frappe.log_error(f"Caddyfile write failed: {write_proc.stderr}", "Caddy Error")
        frappe.throw("Failed to write Caddy config. Contact support.")

    # 6. Reload Caddy
    reload_proc = subprocess.run(
        ["sudo", "/usr/bin/caddy", "reload", "--config", CADDYFILE_PATH],
        capture_output=True,
        text=True
    )

    if reload_proc.returncode != 0:
        frappe.log_error(f"Caddy reload failed: {reload_proc.stderr}", "Caddy Error")
        frappe.throw("Failed to reload Caddy. Contact support.")

    frappe.logger().info(f"Caddy: {backend_domain} and {frontend_domain} added successfully.")