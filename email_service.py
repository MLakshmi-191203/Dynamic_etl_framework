import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_schema_alert(admin_email, process_name, changes, target_table=None, dialect=None):
    if not admin_email:
        print("⚠️ No admin email provided, skipping alert.")
        return False

    sender_email = os.environ.get("SMTP_USER", "dummy@example.com")
    sender_password = os.environ.get("SMTP_PASS", "")
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))

    subject = f"🚨 Action Required: Schema Changes Detected for {process_name}"
    
    sql_suggestions = ""
    if target_table and dialect:
        sql_suggestions = "\n🚀 Suggested SQL Fixes:\n"
        for change in changes:
            if "RENAME" in change:
                # E.g. "RENAME: order_date -> purchase_date"
                parts = change.split("->")
                old_col = parts[0].split(":")[1].strip()
                new_col = parts[1].strip()
                if dialect.lower() == 'postgresql':
                    sql_suggestions += f"ALTER TABLE {target_table} RENAME COLUMN {old_col} TO {new_col};\n"
                elif dialect.lower() == 'mysql':
                    sql_suggestions += f"ALTER TABLE {target_table} RENAME COLUMN {old_col} TO {new_col};\n" # Or CHANGE for older versions
            elif "NEW COLUMN" in change:
                col_name = change.split(":")[1].strip()
                sql_suggestions += f"ALTER TABLE {target_table} ADD COLUMN {col_name} VARCHAR(255);\n"

    body = f"""
    Hello,

    The pipeline for process '{process_name}' has detected the following schema changes:

    {chr(10).join(['- ' + c for c in changes])}

    {sql_suggestions}

    Please implement the changes on the target system. 
    The dynamic ETL pipeline will pause automated schema evolution until you approve the changes in the Metadata Manager UI.

    Regards,
    Data Drive System
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = admin_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # If dummy or no password, just print to console for simulation
    if sender_password == "":
        print(f"📧 [MOCK EMAIL] To: {admin_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        return True

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Alert email sent to {admin_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False
