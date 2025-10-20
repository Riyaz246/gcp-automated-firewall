import requests
import google.auth
from googleapiclient.discovery import build
import functions_framework

# --- CONFIGURATION ---
# This is a well-known, safe, open-source blocklist of malicious IPs
BLOCKLIST_URL = "https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset"

# Your Project ID 
PROJECT_ID = "automated-firewall-project"

# The name of the firewall rule we created in Part 1
FIREWALL_RULE_NAME = "automated-ip-blocklist"
# --- END CONFIGURATION ---

@functions_framework.http
def update_blocklist(request):
    """
    An HTTP-triggered Cloud Function that:
    1. Fetches a list of malicious IPs.
    2. Updates a GCP firewall rule to block them (without using fingerprint).
    """
    try:
        # 1. FETCH THE BLOCKLIST
        print(f"Fetching blocklist from {BLOCKLIST_URL}...")
        response = requests.get(BLOCKLIST_URL)
        response.raise_for_status() # Raises an error if the download fails

        # Get the text, filter out comments (#), and strip whitespace
        ip_list = [
            line.strip() for line in response.text.splitlines()
            if not line.strip().startswith("#") and line.strip()
        ]
        print(f"Successfully fetched {len(ip_list)} IPs.")

        # 2. AUTHENTICATE WITH GOOGLE CLOUD
        credentials, project = google.auth.default()
        service = build('compute', 'v1', credentials=credentials)

        # 3. VERIFY FIREWALL RULE EXISTS (Optional but good practice)
        # We don't need the fingerprint, but let's check if the rule exists first
        print(f"Verifying existence of firewall rule '{FIREWALL_RULE_NAME}'...")
        service.firewalls().get(
            project=PROJECT_ID,
            firewall=FIREWALL_RULE_NAME
        ).execute()
        print(f"Rule '{FIREWALL_RULE_NAME}' found.")

        # 4. PREPARE THE UPDATE BODY (Without fingerprint)
        update_body = {
            "sourceRanges": ip_list  # Set the new list of IPs
        }

        # 5. EXECUTE THE UPDATE
        print(f"Updating firewall rule with {len(ip_list)} IPs...")
        operation = service.firewalls().patch(
            project=PROJECT_ID,
            firewall=FIREWALL_RULE_NAME,
            body=update_body
        ).execute()

        print(f"Firewall update operation started: {operation['name']}")
        return (f"Successfully updated firewall rule '{FIREWALL_RULE_NAME}' with {len(ip_list)} IPs.", 200)

    except Exception as e:
        # If anything fails, log the error
        print(f"ERROR: {e}")
        # Return a generic 500 error
        return (f"An error occurred: {e}", 500)
