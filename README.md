# Automated Threat Intelligence Firewall

This project builds a fully automated security response system. It simulates how a SecOps team would automatically ingest third-party threat intelligence (a list of "bad" IPs) and programmatically update the cloud network firewall to block those threats.

This system is serverless, resilient, and fully automated.

## Skills Demonstrated
* **Security Automation (SOAR):** Built a complete, serverless SOAR (Security Orchestration, Automation, and Response) pipeline.
* **Cloud-Native Automation (Python):** Wrote a Python **Cloud Function** that uses the Google API Client Library to perform "Infrastructure as Code" actions, by programmatically modifying firewall rules.
* **Threat Intelligence Integration:** Integrated a live, public threat intelligence feed (the FireHOL blocklist) directly into the network's security posture.
* **Scheduling & Orchestration (Cloud Scheduler):** Used Cloud Scheduler to create a "cron job" that automatically runs the update process daily, ensuring the blocklist is always current.
* **IAM & Service Accounts:** Correctly configured a service account with the necessary permissions for the Cloud Function to modify network resources.

---

## The Automated Response Pipeline

### 1. The "Before" State: The Firewall Rule
I began by manually creating a "deny" firewall rule named `automated-ip-blocklist`. This rule has a high priority and is set to deny all traffic from a single placeholder IP. This rule acts as the "dynamic blocklist" that our automation will target.

![Before picture of the automated-ip-blocklist rule](Screenshot%20(15).png)

### 2. The "Engine": The Python Cloud Function
I wrote and deployed a Python Cloud Function to act as the brains of the operation. Every time it runs, it performs these steps:
1.  **Fetches** a list of IPs from the FireHOL public blocklist.
2.  **Authenticates** to the Google Compute Engine API.
3.  **Updates** the `automated-ip-blocklist` firewall rule, replacing the old list of IPs with the new, comprehensive list.

![Deployed Cloud Function details page](Screenshot%20(26).png)

### 3. The "Trigger": The Cloud Scheduler
To make this a true "hands-off" automation, I created a Cloud Scheduler job. This job is configured with a cron schedule (`0 0 * * *`) to trigger the Cloud Function's HTTP URL once every 24 hours.

![The Cloud Scheduler job showing the daily frequency](Screenshot%20(30).png)

### 4. The "After" State: The Automated Update
I ran the scheduler job manually to test the end-to-end system. The Cloud Function executed successfully, fetched thousands of IPs from the blocklist, and programmatically updated the firewall rule.

![After picture of the firewall rule's details page, now showing thousands of malicious IPs](Screenshot%20(34).png)



* **ML for Anomaly Detection:** Instead of just trusting a public list, I would log all *denied* traffic from this rule to BigQuery. I would then build a **Vertex AI Anomaly Detection** model to find:
    * Which of my *internal* VMs are trying to *talk to* the blocklist most often? (This VM is likely compromised).
    * Are there *new* IPs (not on my list) that are attacking me in a similar way? This could be an emerging, unknown threat.
