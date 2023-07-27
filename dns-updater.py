import os
import requests
import time

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# API endpoints
FGT_DNS_URL = os.getenv('FGT_DNS_URL', 'https://192.168.1.1/api/v2/cmdb/system/dns-database/')
FGT_DHCP_URL = os.getenv('FGT_DHCP_URL', 'https://192.168.1.1/api/v2/monitor/system/dhcp')

# The Fortigate database name and API token should be stored securely
DATABASE_NAME = os.getenv('DATABASE_NAME', 'local')  # default to 'local' if DATABASE_NAME is not set
API_TOKEN = os.getenv("API_TOKEN")

headers = {'Authorization': f'Bearer {API_TOKEN}'}

def get_dhcp_data():
    response = requests.get(FGT_DHCP_URL, headers=headers, verify=False)
    data = response.json()
    return data.get('results', [])

def delete_dns_database():
    response = requests.delete(f'{FGT_DNS_URL}{DATABASE_NAME}', headers=headers, verify=False)
    if response.status_code not in [200, 204]:  # accept both 200 and 204 as successful status codes
        print(f"Failed to delete DNS database {DATABASE_NAME}. Response: {response.text}")
    else:
        print(f"Deleted DNS database {DATABASE_NAME}")

def create_dns_database():
    new_db_data = {
        "name": DATABASE_NAME,
        "domain": "localdomain",
        "ttl": 300
    }
    response = requests.post(FGT_DNS_URL, json=new_db_data, headers=headers, verify=False)
    if response.status_code != 200:
        print(f"Failed to create DNS database {DATABASE_NAME}. Response: {response.text}")
    else:
        print(f"Created DNS database {DATABASE_NAME}")

def update_dns_database():
    dhcp_data = get_dhcp_data()
    
    # Delete the DNS database
    delete_dns_database()

    # Wait for 3 seconds
    time.sleep(3)

    # Create a new DNS database
    create_dns_database()

    # Prepare data for DNS entries based on DHCP data
    dns_entries = []
    for dhcp_entry in dhcp_data:
        ip = dhcp_entry.get('ip', None)
        hostname = dhcp_entry.get('hostname', None)
        # Only add a DNS entry if both the IP and hostname are present
        if ip and hostname:
            new_entry = {
                "status": "enable",
                "type": "A",
                "ttl": 300,
                "preference": 65535,
                "ip": ip,
                "hostname": hostname
            }
            dns_entries.append(new_entry)

    # Update DNS database with new entries
    put_data = {"name": DATABASE_NAME, "dns-entry": dns_entries}
    response = requests.put(f'{FGT_DNS_URL}{DATABASE_NAME}', json=put_data, headers=headers, verify=False)
    print(f"Added new DNS entries.")

if __name__ == '__main__':
    while True:
        try:
            update_dns_database()
        except Exception as e:
            print(f"An error occurred during the execution of update_dns_database: {e}")
        time.sleep(305)  # Wait for 305 seconds before the next iteration
