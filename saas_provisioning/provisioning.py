# import frappe
# import subprocess
# import json
# import os
# import shutil
# from saas_provisioning.dns import add_caddy_domain

# from frappe.desk.page.setup_wizard.setup_wizard import get_setup_stages, parse_args, process_setup_stages, sanitize_input

# def create_site_job(site_name, db_name, payload):
#     """
#     Background job to create and configure a new Frappe site.
#     Note: Don't call frappe.destroy() - the job wrapper handles cleanup.
#     """
#     bench_path = frappe.utils.get_bench_path()
    
#     # Log to worker output (visible in worker.log)
#     print(f"🚀 Starting site creation for {site_name}")
#     print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
#     frappe.logger().info(f"Starting site creation for {site_name}")
#     frappe.logger().info(f"Payload: {payload}")

#     try:
#         # 1️⃣ Create site using bench command
#         print(f"⚙️  Running bench new-site command...")
        
#         cmd = [
#             "/home/frappe/.local/bin/bench", "new-site", site_name,
#             "--db-name", db_name,
#             "--admin-password", payload.get("password"),
#             "--install-app", "erpnext",
#             "--mariadb-user-host-login-scope=%"
#         ]

#         # Install additional apps if specified
#         for app in payload.get("apps", []):
#             cmd.extend(["--install-app", app])

#         print(f"📝 Command: {' '.join(cmd)}")

#         result = subprocess.run(
#             cmd, 
#             cwd=bench_path, 
#             check=True,
#             capture_output=True,
#             text=True,
#             timeout=1500  # 5 minute timeout
#         )
        
#         # Log subprocess output
#         if result.stdout:
#             print(f"✅ Bench output:\n{result.stdout}")
#         if result.stderr:
#             print(f"⚠️  Bench stderr:\n{result.stderr}")
        
#         print(f"✅ Site {site_name} created successfully")
#         frappe.logger().info(f"Site {site_name} created successfully")

#         # 2️⃣ Run setup wizard on the new site
#         print(f"🔧 Initializing site context for {site_name}...")
        
#         frappe.init(site=site_name, force=True)
#         frappe.connect()
#         frappe.set_user("Administrator")
#         # ✅ Verify connection
#         print(f"🔍 Connected to site: {frappe.local.site}")
#         print(f"👤 Current user: {frappe.session.user}")
#         print(f"🗄️  Database: {frappe.conf.db_name}")
#         frappe.clear_cache()
#         print("Cache Cleared")
#         # Additional verification - query the database

#         frappe.conf.trigger_site_setup_in_background = True

#         setup_payload = {
#             "currency": payload.get("currency"),
#             "country": payload.get("country"),
#             "timezone": payload.get("timezone"),
#             "language": payload.get("language", "en"),
#             "full_name": payload.get("full_name"),
#             "email": payload.get("email"),
#             "password": payload.get("password"),
#             "company_name": payload.get("company_name"),
#             "company_abbr": payload.get("company_abbr"),
#             "chart_of_accounts": payload.get("chart_of_accounts"),
#             "fy_start_date": payload.get("fy_start_date"),
#             "fy_end_date": payload.get("fy_end_date"),
#             "setup_demo": payload.get("setup_demo", 0),
#         }

#         print(f"🏗️  Running ERPNext setup wizard...")
#         print(f"📋 Setup config: {json.dumps(setup_payload, indent=2, default=str)}")



#         # Step 2 — ✅ ADD THIS LINE — auto-add domain to Caddy
#         add_caddy_domain(site_name)


#         # Run ERPNext setup wizard
#         # from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

#         if frappe.is_setup_complete():
#             print(f"⚠️  Setup wizard already completed for {site_name}, skipping setup.")
#             return {"status": "ok"}

#         kwargs = parse_args(sanitize_input(setup_payload))
#         stages = get_setup_stages(kwargs)
#         is_background_task = frappe.conf.get("trigger_site_setup_in_background")
#         print(f"is_background_task = {is_background_task}")
#         if is_background_task:
#             process_setup_stages.enqueue(stages=stages, user_input=kwargs, is_background_task=True)
#             print(f"🎉 Site provisioning completed successfully!")

#             return {"status": "registered"}
#         else:
#             print(f"🎉 Site provisioning completed successfully!")
            
#             return {
#                 "status": "success",
#                 "site": site_name,
#                 "message": f"Site {site_name} created and configured successfully"
#             }
#             return process_setup_stages(stages, kwargs)

#         # setup_complete(json.dumps(setup_payload))
        
#         # Commit changes
#         # frappe.db.commit()
        
#         print(f"✅ Setup wizard completed for {site_name}")
#         frappe.logger().info(f"Setup wizard completed for {site_name}")

#         # 3️⃣ Send welcome email (optional)
#         # print(f"📧 Sending welcome email to {payload.get('email')}...")
#         # send_welcome_email(payload.get("email"), site_name, payload.get("company_name"))
    

#     except subprocess.CalledProcessError as e:
#         error_msg = f"Bench command failed: {e.stderr}"
#         print(f"❌ ERROR: {error_msg}")
#         frappe.logger().error(error_msg)
#         frappe.log_error(error_msg, "Site Creation Failed")
#         raise  # Re-raise to mark job as failed

#     except Exception as e:
#         error_msg = f"Site setup failed for {site_name}: {str(e)}"
#         print(f"❌ ERROR: {error_msg}")
#         import traceback
#         print(f"📍 Traceback:\n{traceback.format_exc()}")
#         frappe.logger().error(error_msg)
#         frappe.log_error(error_msg, "Site Creation Failed")
#         raise


# def send_welcome_email(email, site_name, company_name):
#     """Send welcome email with site details"""
#     try:
#         frappe.sendmail(
#             recipients=[email],
#             subject=f"Welcome to {company_name} - Your ERP Site is Ready!",
#             message=f"""
#             <h2>Your ERP site is ready! 🎉</h2>
#             <p>Your site has been successfully created and configured.</p>
            
#             <p><strong>Site URL:</strong> <a href="https://{site_name}">https://{site_name}</a></p>
#             <p><strong>Username:</strong> {email}</p>
            
#             <p>You can now log in and start using your ERP system.</p>
            
#             <p>If you have any questions, please contact our support team.</p>
            
#             <p>Best regards,<br>Your ERP Team</p>
#             """,
#             now=True
#         )
#         print(f"✅ Welcome email sent to {email}")
#         frappe.logger().info(f"Welcome email sent to {email}")
#     except Exception as e:
#         # Don't fail the job if email fails
#         print(f"⚠️  Failed to send welcome email: {str(e)}")
#         frappe.logger().error(f"Failed to send welcome email: {str(e)}")
#         frappe.log_error(str(e), "Welcome Email Failed")


# import frappe
# import subprocess
# import json
# import os
# import shutil
# from saas_provisioning.dns import add_caddy_domain

# from frappe.desk.page.setup_wizard.setup_wizard import get_setup_stages, parse_args, process_setup_stages, sanitize_input

# MARIADB_ROOT_USERNAME = "root"
# MARIADB_ROOT_PASSWORD = "root123"  # ✅ Set this

# def create_site_job(site_name, db_name, payload):
#     bench_path = frappe.utils.get_bench_path()

#     print(f"🚀 Starting site creation for {site_name}")
#     frappe.logger().info(f"Starting site creation for {site_name}")

#     try:
#         # 1️⃣ Create site using bench command
#         cmd = [
#             "/home/frappe/.local/bin/bench", "new-site", site_name,
#             "--db-name", db_name,
#             "--admin-password", payload.get("password"),
#             "--install-app", "erpnext",
#             "--mariadb-user-host-login-scope=%",
#             "--mariadb-root-username", MARIADB_ROOT_USERNAME,  # ✅ Prevents interactive prompt
#             "--mariadb-root-password", MARIADB_ROOT_PASSWORD,  # ✅ Prevents interactive prompt
#         ]

#         for app in payload.get("apps", []):
#             cmd.extend(["--install-app", app])

#         print(f"📝 Running bench new-site for {site_name}")

#         result = subprocess.run(
#             cmd,
#             cwd=bench_path,
#             check=True,
#             capture_output=True,
#             text=True,
#             timeout=3600  # ✅ 1 hour — bench new-site takes ~2 mins but give plenty of room
#         )

#         if result.stdout:
#             print(f"✅ Bench output:\n{result.stdout}")
#         if result.stderr:
#             print(f"⚠️  Bench stderr:\n{result.stderr}")

#         print(f"✅ Site {site_name} created successfully")
#         frappe.logger().info(f"Site {site_name} created successfully")

#         # 2️⃣ Initialize site context
#         frappe.init(site=site_name, force=True)
#         frappe.connect()
#         frappe.set_user("Administrator")
#         frappe.clear_cache()

#         frappe.conf.trigger_site_setup_in_background = True

#         setup_payload = {
#             "currency": payload.get("currency"),
#             "country": payload.get("country"),
#             "timezone": payload.get("timezone"),
#             "language": payload.get("language", "en"),
#             "full_name": payload.get("full_name"),
#             "email": payload.get("email"),
#             "password": payload.get("password"),
#             "company_name": payload.get("company_name"),
#             "company_abbr": payload.get("company_abbr"),
#             "chart_of_accounts": payload.get("chart_of_accounts"),
#             "fy_start_date": payload.get("fy_start_date"),
#             "fy_end_date": payload.get("fy_end_date"),
#             "setup_demo": payload.get("setup_demo", 0),
#         }

#         if frappe.is_setup_complete():
#             print(f"⚠️  Setup already completed for {site_name}, skipping.")
#             add_caddy_domain(site_name)
#             return {"status": "ok"}

#         # 3️⃣ Run ERPNext setup wizard
#         kwargs = parse_args(sanitize_input(setup_payload))
#         stages = get_setup_stages(kwargs)
#         is_background_task = frappe.conf.get("trigger_site_setup_in_background")

#         print(f"is_background_task = {is_background_task}")

#         if is_background_task:
#             process_setup_stages.enqueue(
#                 stages=stages,
#                 user_input=kwargs,
#                 is_background_task=True,
#                 timeout=1800
#             )
#         else:
#             process_setup_stages(stages, kwargs)

#         # 4️⃣ Add domain to Caddy AFTER everything succeeds
#         print(f"🌐 Adding {site_name} to Caddy...")
#         add_caddy_domain(site_name)

#         print(f"🎉 Site provisioning completed successfully!")
#         frappe.logger().info(f"Site {site_name} provisioned successfully")

#         return {"status": "success", "site": site_name}

#     except subprocess.CalledProcessError as e:
#         error_msg = f"Bench command failed: {e.stderr}"
#         print(f"❌ ERROR: {error_msg}")
#         frappe.log_error(error_msg, "Site Creation Failed")
#         raise

#     except Exception as e:
#         import traceback
#         error_msg = f"Site setup failed for {site_name}: {str(e)}"
#         print(f"❌ ERROR: {error_msg}")
#         print(f"📍 Traceback:\n{traceback.format_exc()}")
#         frappe.log_error(error_msg, "Site Creation Failed")
#         raise


# def send_welcome_email(email, site_name, company_name):
#     try:
#         frappe.sendmail(
#             recipients=[email],
#             subject=f"Welcome to {company_name} - Your ERP Site is Ready!",
#             message=f"""
#             <h2>Your ERP site is ready! 🎉</h2>
#             <p><strong>Site URL:</strong> <a href="https://{site_name}">https://{site_name}</a></p>
#             <p><strong>Username:</strong> {email}</p>
#             <p>Best regards,<br>Your ERP Team</p>
#             """,
#             now=True
#         )
#         print(f"✅ Welcome email sent to {email}")
#     except Exception as e:
#         print(f"⚠️  Failed to send welcome email: {str(e)}")




# import frappe
# import subprocess
# import json
# import os
# import shutil
# import time
# from saas_provisioning.dns import add_caddy_domain

# from frappe.desk.page.setup_wizard.setup_wizard import get_setup_stages, parse_args, process_setup_stages, sanitize_input

# MARIADB_ROOT_USERNAME = "root"
# MARIADB_ROOT_PASSWORD = "root123"


# def create_site_job(site_name, db_name, payload):
#     bench_path = frappe.utils.get_bench_path()

#     print(f"🚀 Starting site creation for {site_name}")
#     frappe.logger().info(f"Starting site creation for {site_name}")

#     try:
#         # 1️⃣ Create site using bench command
#         cmd = [
#             "/home/frappe/.local/bin/bench", "new-site", site_name,
#             "--db-name", db_name,
#             "--admin-password", payload.get("password"),
#             "--install-app", "erpnext",
#             "--mariadb-user-host-login-scope=%",
#             "--mariadb-root-username", MARIADB_ROOT_USERNAME,
#             "--mariadb-root-password", MARIADB_ROOT_PASSWORD,
#         ]

#         for app in payload.get("apps", []):
#             cmd.extend(["--install-app", app])

#         print(f"📝 Running bench new-site for {site_name}")

#         result = subprocess.run(
#             cmd,
#             cwd=bench_path,
#             check=True,
#             capture_output=True,
#             text=True,
#             timeout=3600
#         )

#         if result.stdout:
#             print(f"✅ Bench output:\n{result.stdout}")
#         if result.stderr:
#             print(f"⚠️  Bench stderr:\n{result.stderr}")

#         print(f"✅ Site {site_name} created successfully")
#         frappe.logger().info(f"Site {site_name} created successfully")

#         # 2️⃣ Initialize site context
#         frappe.init(site=site_name, force=True)
#         frappe.connect()
#         frappe.set_user("Administrator")
#         frappe.clear_cache()

#         # 3️⃣ Check if setup already complete
#         if frappe.is_setup_complete():
#             print(f"⚠️  Setup already completed for {site_name}, skipping.")
#             add_caddy_domain(site_name)
#             return {"status": "ok"}

#         frappe.conf.trigger_site_setup_in_background = True

#         setup_payload = {
#             "currency": payload.get("currency"),
#             "country": payload.get("country"),
#             "timezone": payload.get("timezone"),
#             "language": payload.get("language", "en"),
#             "full_name": payload.get("full_name"),
#             "email": payload.get("email"),
#             "password": payload.get("password"),
#             "company_name": payload.get("company_name"),
#             "company_abbr": payload.get("company_abbr"),
#             "chart_of_accounts": payload.get("chart_of_accounts"),
#             "fy_start_date": payload.get("fy_start_date"),
#             "fy_end_date": payload.get("fy_end_date"),
#             "setup_demo": payload.get("setup_demo", 0),
#         }

#         # 4️⃣ Run ERPNext setup wizard
#         kwargs = parse_args(sanitize_input(setup_payload))
#         stages = get_setup_stages(kwargs)
#         is_background_task = frappe.conf.get("trigger_site_setup_in_background")

#         print(f"is_background_task = {is_background_task}")

#         if is_background_task:
#             # Enqueue setup wizard
#             process_setup_stages.enqueue(
#                 stages=stages,
#                 user_input=kwargs,
#                 is_background_task=True,
#                 timeout=1800
#             )

#             # 5️⃣ Poll until setup wizard completes (max 15 mins)
#             print(f"⏳ Waiting for setup wizard to complete for {site_name}...")
#             setup_complete = False

#             for attempt in range(90):  # 90 x 10s = 15 mins
#                 time.sleep(10)
#                 try:
#                     frappe.init(site=site_name, force=True)
#                     frappe.connect()
#                     frappe.set_user("Administrator")

#                     if frappe.is_setup_complete():
#                         setup_complete = True
#                         print(f"✅ Setup wizard completed for {site_name} (attempt {attempt + 1})")
#                         frappe.logger().info(f"Setup wizard completed for {site_name}")
#                         break
#                     else:
#                         print(f"⏳ Setup not complete yet... attempt {attempt + 1}/90")

#                 except Exception as poll_error:
#                     print(f"⚠️  Poll error on attempt {attempt + 1}: {str(poll_error)}")
#                     continue

#             if not setup_complete:
#                 error_msg = f"Setup wizard timed out after 15 mins for {site_name}"
#                 print(f"❌ {error_msg}")
#                 frappe.log_error(error_msg, "Provisioning Timeout")
#                 raise Exception(error_msg)

#         else:
#             # Synchronous setup
#             process_setup_stages(stages, kwargs)
#             print(f"✅ Synchronous setup completed for {site_name}")

#         # 6️⃣ Add domain to Caddy AFTER setup is fully complete
#         print(f"🌐 Adding {site_name} to Caddy...")
#         add_caddy_domain(site_name)

#         # 7️⃣ Send welcome email
#         send_welcome_email(
#             email=payload.get("email"),
#             site_name=site_name,
#             company_name=payload.get("company_name")
#         )

#         print(f"🎉 Site provisioning completed successfully!")
#         frappe.logger().info(f"Site {site_name} provisioned successfully")

#         return {"status": "success", "site": site_name}

#     except subprocess.CalledProcessError as e:
#         error_msg = f"Bench command failed: {e.stderr}"
#         print(f"❌ ERROR: {error_msg}")
#         frappe.log_error(error_msg, "Site Creation Failed")
#         raise

#     except Exception as e:
#         import traceback
#         error_msg = f"Site setup failed for {site_name}: {str(e)}"
#         print(f"❌ ERROR: {error_msg}")
#         print(f"📍 Traceback:\n{traceback.format_exc()}")
#         frappe.log_error(error_msg, "Site Creation Failed")
#         raise


# def send_welcome_email(email, site_name, company_name):
#     try:
#         frappe.sendmail(
#             recipients=[email],
#             subject=f"Welcome to {company_name} - Your ERP Site is Ready!",
#             message=f"""
#             <h2>Your ERP site is ready! 🎉</h2>
#             <p><strong>Site URL:</strong> <a href="https://{site_name}">https://{site_name}</a></p>
#             <p><strong>Username:</strong> {email}</p>
#             <p>Best regards,<br>Your ERP Team</p>
#             """,
#             now=True
#         )
#         print(f"✅ Welcome email sent to {email}")
#     except Exception as e:
#         print(f"⚠️  Failed to send welcome email: {str(e)}")



import frappe
import subprocess
import json
import os
import shutil
import time
from saas_provisioning.dns import add_caddy_domain

from frappe.desk.page.setup_wizard.setup_wizard import get_setup_stages, parse_args, process_setup_stages, sanitize_input

MARIADB_ROOT_USERNAME = "root"
MARIADB_ROOT_PASSWORD = "root123"


def create_site_job(site_name, db_name, payload):
    bench_path = frappe.utils.get_bench_path()

    print(f"🚀 Starting site creation for {site_name}")
    frappe.logger().info(f"Starting site creation for {site_name}")

    try:
        # 1️⃣ Create site using bench command
        cmd = [
            "/home/frappe/.local/bin/bench", "new-site", site_name,
            "--db-name", db_name,
            "--admin-password", payload.get("password"),
            "--install-app", "erpnext",
            "--install-app", "auth_api",
            "--install-app", "custom_api",
            "--mariadb-user-host-login-scope=%",
            "--mariadb-root-username", MARIADB_ROOT_USERNAME,
            "--mariadb-root-password", MARIADB_ROOT_PASSWORD,
        ]

        for app in payload.get("apps", []):
            cmd.extend(["--install-app", app])

        print(f"📝 Running bench new-site for {site_name}")

        result = subprocess.run(
            cmd,
            cwd=bench_path,
            check=True,
            capture_output=True,
            text=True,
            timeout=3600
        )

        if result.stdout:
            print(f"✅ Bench output:\n{result.stdout}")
        if result.stderr:
            print(f"⚠️  Bench stderr:\n{result.stderr}")

        print(f"✅ Site {site_name} created successfully")
        frappe.logger().info(f"Site {site_name} created successfully")

        # 1️⃣a Run migrate command to apply custom fields from auth_api and custom_api
        print(f"🔄 Running migrate for {site_name}...")
        migrate_cmd = [
            "/home/frappe/.local/bin/bench", "--site", site_name, "migrate"
        ]

        try:
            migrate_result = subprocess.run(
                migrate_cmd,
                cwd=bench_path,
                check=True,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for migrate
            )

            if migrate_result.stdout:
                print(f"✅ Migrate output:\n{migrate_result.stdout}")
            if migrate_result.stderr and "error" in migrate_result.stderr.lower():
                print(f"⚠️  Migrate stderr:\n{migrate_result.stderr}")

            print(f"✅ Migrate completed for {site_name}")
            frappe.logger().info(f"Migrate completed for {site_name}")

        except subprocess.CalledProcessError as migrate_error:
            error_msg = f"Migrate command failed: {migrate_error.stderr}"
            print(f"⚠️  Warning: {error_msg}")
            frappe.logger().warning(error_msg)
            # Don't fail the job — continue with setup wizard
            # Custom fields will be applied during setup wizard if needed

        # 3️⃣ Initialize site context
        frappe.init(site=site_name, force=True)
        frappe.connect()
        frappe.set_user("Administrator")
        frappe.clear_cache()

        # 4️⃣ Check if setup already complete
        if frappe.db.get_single_value("System Settings", "setup_complete"):
            print(f"⚠️  Setup already completed for {site_name}, skipping.")
            add_caddy_domain(site_name)
            return {"status": "ok"}

        # Don't run setup in background — run it synchronously and wait for completion
        setup_payload = {
            "currency": payload.get("currency"),
            "country": payload.get("country"),
            "timezone": payload.get("timezone"),
            "language": payload.get("language", "en"),
            "full_name": payload.get("full_name"),
            "email": payload.get("email"),
            "password": payload.get("password"),
            "company_name": payload.get("company_name"),
            "company_abbr": payload.get("company_abbr"),
            "chart_of_accounts": payload.get("chart_of_accounts"),
            "fy_start_date": payload.get("fy_start_date"),
            "fy_end_date": payload.get("fy_end_date"),
            "setup_demo": payload.get("setup_demo", 0),
        }

        # 5️⃣ Run ERPNext setup wizard synchronously
        print(f"🔧 Running setup wizard for {site_name}...")
        kwargs = parse_args(sanitize_input(setup_payload))
        stages = get_setup_stages(kwargs)

        try:
            # Run setup synchronously — this will complete before proceeding
            process_setup_stages(stages, kwargs)
            print(f"✅ Setup wizard completed successfully for {site_name}")
        except Exception as setup_error:
            print(f"⚠️  Setup wizard encountered an error: {str(setup_error)}")
            frappe.logger().warning(f"Setup wizard error for {site_name}: {str(setup_error)}")
            # Don't fail — continue, the setup may have partially completed
            # and we want the site to be accessible even if setup had issues

        # 5️⃣ Verify setup completion
        print(f"🔍 Verifying setup completion for {site_name}...")
        frappe.init(site=site_name, force=True)
        frappe.connect()
        frappe.set_user("Administrator")
        setup_status = frappe.db.get_single_value("System Settings", "setup_complete")
        print(f"Setup complete status: {setup_status}")

        if not setup_status:
            print(f"⚠️  Setup not marked as complete, but continuing with provisioning...")

        # 6️⃣ Add Caddy domain
        print(f"🌐 Adding {site_name} to Caddy...")
        add_caddy_domain(site_name)

        print(f"🎉 Site provisioning completed successfully!")
        frappe.logger().info(f"Site {site_name} provisioned successfully")

        return {"status": "success", "site": site_name}

    except subprocess.CalledProcessError as e:
        error_msg = f"Bench command failed: {e.stderr}"
        print(f"❌ ERROR: {error_msg}")
        frappe.log_error(error_msg, "Site Creation Failed")
        raise

    except Exception as e:
        import traceback
        error_msg = f"Site setup failed for {site_name}: {str(e)}"
        print(f"❌ ERROR: {error_msg}")
        print(f"📍 Traceback:\n{traceback.format_exc()}")
        frappe.log_error(error_msg, "Site Creation Failed")
        raise


def send_welcome_email(email, site_name, company_name):
    try:
        frappe.sendmail(
            recipients=[email],
            subject=f"Welcome to {company_name} - Your ERP Site is Ready!",
            message=f"""
            <h2>Your ERP site is ready! 🎉</h2>
            <p><strong>Site URL:</strong> <a href="https://{site_name}">https://{site_name}</a></p>
            <p><strong>Username:</strong> {email}</p>
            <p>Best regards,<br>Your ERP Team</p>
            """,
            now=True
        )
        print(f"✅ Welcome email sent to {email}")
    except Exception as e:
        print(f"⚠️  Failed to send welcome email: {str(e)}")