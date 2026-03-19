# saas_manager/api/signup.py
import frappe
import re
import os
import json
import subprocess



CADDYFILE_PATH = "/etc/caddy/Caddyfile"
TENANTS_MARKER = "# TENANTS_END"
CADDY_EMAIL = "you@yourapp.com"

def add_caddy_domain(site_name: str):
    """
    Appends a new site block to Caddyfile and reloads Caddy.
    Called after bench new-site succeeds.
    """
    # 1. Build the new Caddy block
    new_block = f"""
                    {site_name} {{
                        reverse_proxy localhost:8000 {{
                            header_up Host {site_name}
                        }}
                        tls {CADDY_EMAIL}
                    }}

                    """
    
    # 2. Read current Caddyfile
    with open(CADDYFILE_PATH, "r") as f:
        content = f.read()
    
    # 3. Check if domain already exists (avoid duplicates)
    if site_name in content:
        frappe.logger().info(f"Caddy: {site_name} already exists, skipping.")
        return
    
    # 4. Insert before the TENANTS_END marker
    updated_content = content.replace(
        TENANTS_MARKER,
        new_block + TENANTS_MARKER
    )
    
    # 5. Write back
    with open(CADDYFILE_PATH, "w") as f:
        f.write(updated_content)
    
    # 6. Reload Caddy (no downtime — hot reload)
    result = subprocess.run(
        ["caddy", "reload", "--config", CADDYFILE_PATH],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        frappe.log_error(f"Caddy reload failed: {result.stderr}", "Caddy Error")
        frappe.throw("Failed to configure domain. Contact support.")
    
    frappe.logger().info(f"Caddy: {site_name} added and reloaded successfully.")