import frappe
import re
import os
import json
@frappe.whitelist(allow_guest=True)
def create_site(**payload):
    company_name = payload.get("company_name")
    email = payload.get("email")
    password = payload.get("password")

    # 1️⃣ Validate input
    if not company_name or not email or not password:
        frappe.local.response["http_status_code"] = 400
        frappe.local.response["message"] = "Missing required fields"
        return

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        frappe.local.response["http_status_code"] = 400
        frappe.local.response["message"] = "Invalid email"
        return

    # 2️⃣ Build site + db name
    # Extract base company name (remove suffixes like "Pvt Ltd", "Ltd", "Inc", etc.)
    clean_name = company_name.strip()
    # Remove common company suffixes
    suffixes = [
        r'\s+(pvt\.?\s+ltd\.?)',
        r'\s+(private\s+limited)',
        r'\s+(ltd\.?)',
        r'\s+(inc\.?)',
        r'\s+(corporation)',
        r'\s+(corp\.?)',
        r'\s+(\&|and|ltd)',
    ]
    for suffix in suffixes:
        clean_name = re.sub(suffix, "", clean_name, flags=re.IGNORECASE)
    
    # Convert to lowercase and remove all non-alphanumeric characters
    site_name = re.sub(r"[^a-z0-9]", "", clean_name.lower())
    site_name = f"api.erp.{site_name}.rolaface.com"
    db_name = site_name.replace(".", "_")
    
    print(f"📝 Company: '{company_name}' → Site: '{site_name}'")

    bench_path = frappe.utils.get_bench_path()
    sites_path = os.path.join(bench_path, "sites", site_name)

    # 3️⃣ Check if site exists
    if os.path.exists(sites_path):
        frappe.local.response["http_status_code"] = 409
        frappe.local.response["message"] = f"Site {site_name} already exists"
        return

    # 4️⃣ Enqueue background job
    frappe.enqueue(
        method="saas_provisioning.provisioning.create_site_job",
        queue="long",
        timeout=1800,  # 30 minutes
        site_name=site_name,
        db_name=db_name,
        payload=payload
        )

    frappe.db.commit()

    # 5️⃣ Immediate response
    return {
        "status": "accepted",
        "site": site_name,
        "message": "Site provisioning started"
    }

