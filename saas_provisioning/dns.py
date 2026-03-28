# saas_manager/api/signup.py
import frappe
import subprocess

CADDYFILE_PATH = "/etc/caddy/Caddyfile"
BENCH_SITES_PATH = "/srv/apps/erp/backend/master-bench/sites"

def add_caddy_domain(site_name: str):
    """
    Appends a new site block to Caddyfile and reloads Caddy.
    Called after bench new-site succeeds.
    """
    # 1. Read current Caddyfile
    with open(CADDYFILE_PATH, "r") as f:
        content = f.read()

    # 2. Check if domain already exists (avoid duplicates)
    if site_name in content:
        frappe.logger().info(f"Caddy: {site_name} already exists, skipping.")
        return

    # 3. Build the new Caddy block
    new_block = (
        f"\n{site_name} {{\n"
        f"\n"
        f"    @assets path /assets/*\n"
        f"    root * {BENCH_SITES_PATH}\n"
        f"    file_server @assets\n"
        f"\n"
        f"    @files path /files/*\n"
        f"    root * {BENCH_SITES_PATH}/{site_name}\n"
        f"    file_server @files\n"
        f"\n"
        f"    reverse_proxy 127.0.0.1:8004\n"
        f"}}\n"
    )

    # 4. Append to Caddyfile using sudo tee -a (no overwrite)
    write_proc = subprocess.run(
        ["sudo", "tee", "-a", CADDYFILE_PATH],
        input=new_block,
        capture_output=True,
        text=True
    )

    if write_proc.returncode != 0:
        frappe.log_error(f"Caddyfile write failed: {write_proc.stderr}", "Caddy Error")
        frappe.throw("Failed to write Caddy config. Contact support.")

    # 5. Reload Caddy
    reload_proc = subprocess.run(
        ["sudo", "/usr/bin/caddy", "reload", "--config", CADDYFILE_PATH],
        capture_output=True,
        text=True
    )

    if reload_proc.returncode != 0:
        frappe.log_error(f"Caddy reload failed: {reload_proc.stderr}", "Caddy Error")
        frappe.throw("Failed to reload Caddy. Contact support.")

    frappe.logger().info(f"Caddy: {site_name} added and reloaded successfully.")