import os
import json
import requests
import sched, time
from flask import Flask, request, jsonify
from threading import Thread

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

app = Flask(__name__)

# URLs and database name
DATABASE_NAME = os.getenv('DATABASE_NAME', 'local')
FGT_DNS_URL = os.getenv('FGT_DNS_URL', 'https://192.168.1.1/api/v2/cmdb/system/dns-database/')
FGT_DHCP_URL = os.getenv('FGT_DHCP_URL', 'https://192.168.1.1/api/v2/monitor/dhcp')
API_TOKEN = os.getenv('API_TOKEN')

headers = {'Authorization': f'Bearer {API_TOKEN}'}

scheduler = sched.scheduler(time.time, time.sleep)

# Define a function to run the scheduler
def run_scheduler():
    scheduler.run()

def get_dhcp_data():
    response = requests.get(FGT_DHCP_URL, headers=headers, verify=False)
    data = response.json()
    return data['results']

def get_dns_data():
    response = requests.get(f'{FGT_DNS_URL}{DATABASE_NAME}', headers=headers, verify=False)
    return response.json()['results'][0]['dns-entry']

def compare_and_update():
    dhcp_data = get_dhcp_data()
    dns_data = get_dns_data()

    for dhcp_entry in dhcp_data:
        dhcp_ip = dhcp_entry['ip']
        
        # Check if 'hostname' key exists
        if 'hostname' in dhcp_entry:
            dhcp_hostname = dhcp_entry['hostname']
        else:
            # If 'hostname' key doesn't exist, skip this iteration
            continue

        matching_dns_entries = [entry for entry in dns_data if entry['ip'] == dhcp_ip]

        if not matching_dns_entries:
            # Add new DNS entry
            add_dns_entry(dhcp_ip, dhcp_hostname)
        else:
            for dns_entry in matching_dns_entries:
                if dns_entry['hostname'] != dhcp_hostname:
                    # Delete old entry and add new one
                    delete_dns_entry(dns_entry['id'])
                    add_dns_entry(dhcp_ip, dhcp_hostname)

    # Schedule next run
    scheduler.enter(180, 1, compare_and_update)

def add_dns_entry(ip, hostname):
    dns_data = get_dns_data()

    # Check if a DNS entry with the same hostname already exists
    matching_dns_entries = [entry for entry in dns_data if entry['hostname'] == hostname]
    for dns_entry in matching_dns_entries:
        # Delete the old entry
        delete_dns_entry(dns_entry['id'])
        print(f"Deleted existing DNS entry for hostname {hostname}.")

    new_entry = {
        "status": "enable",
        "type": "A",
        "ttl": 1800,
        "preference": 65535,
        "ip": ip,
        "hostname": hostname
    }

    dns_data.append(new_entry)
    put_data = {"name": DATABASE_NAME, "dns-entry": dns_data}

    response = requests.put(f'{FGT_DNS_URL}{DATABASE_NAME}', json=put_data, headers=headers, verify=False)
    print(f"Added new DNS entry for hostname {hostname} with IP {ip}.")


def delete_dns_entry(id):
    response = requests.delete(f'{FGT_DNS_URL}{DATABASE_NAME}/{id}', headers=headers, verify=False)

@app.route('/dns_update', methods=['POST'])
def dns_update():
    data = request.json

    # Check if required data is present
    if not all(key in data for key in ('ip', 'hostname')):
        return jsonify({'message': 'Invalid data, ip and hostname are required'}), 400

    ip = data['ip']
    hostname = data['hostname']

    dns_data = get_dns_data()

    matching_dns_entries = [entry for entry in dns_data if entry['ip'] == ip]

    if matching_dns_entries:
        for dns_entry in matching_dns_entries:
            if dns_entry['hostname'] != hostname:
                # Delete old entry and add new one
                delete_dns_entry(dns_entry['id'])

    add_dns_entry(ip, hostname)

    return jsonify({'message': 'Record updated successfully'}), 200

if __name__ == '__main__':
    # Start the comparison function
    scheduler.enter(0, 1, compare_and_update)

    # Start the scheduler in a new thread
    thread = Thread(target=run_scheduler)
    thread.start()

    app.run(host='0.0.0.0', debug=True)
