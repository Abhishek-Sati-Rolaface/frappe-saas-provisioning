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
    site_name = re.sub(r"[^a-z0-9]", "", company_name.lower())
    site_name = f"api.erp.{site_name}.rolaface.com"
    db_name = site_name.replace(".", "_")

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

# def create_site_job(payload, site_name, db_name):
#     bench_path = frappe.utils.get_bench_path()

#     subprocess.run(
#         [
#             "bench", "new-site", site_name,
#             "--db-name", db_name,
#             "--install-app", "erpnext",
#             "--admin-password", payload.get("password"),
#             "--mariadb-user-host-login-scope=%"
#         ],
#         cwd=bench_path,
#         check=True,
#     )

#     frappe.init(site=site_name)
#     frappe.connect()
#     frappe.set_user("Administrator")

#     try:
#         frappe.enqueue(
#             "frappe.desk.page.setup_wizard.setup_wizard.setup_complete",
#             queue="long",
#             args=(json.dumps(payload),),
#         )
#     finally:
#         frappe.destroy()


# def run_setup_wizard(site_name, setup_data):
#     frappe.init(site=site_name)
#     frappe.connect()
#     frappe.set_user("Administrator")

#     try:
#         frappe.enqueue(
#             "frappe.desk.page.setup_wizard.setup_wizard.setup_complete",
#             queue="long",
#             args=(json.dumps(setup_data),),
#             is_async=True,
#         )
#     finally:
#         frappe.destroy()

