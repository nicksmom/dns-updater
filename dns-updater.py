from flask import Flask, request, jsonify
import requests
import os
import json
import logging
from logging.handlers import RotatingFileHandler

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

app = Flask(__name__)

<<<<<<< HEAD
# The database name and Fortigate URL should be stored securely
<<<<<<< HEAD
DATABASE_NAME = 'local'
FGT_URL = 'https://192.168.1.1/api/v2/cmdb/system/dns-database/'
=======
DATABASE_NAME = os.getenv('DATABASE_NAME', 'local')  # default to 'local' if DATABASE_NAME is not set
FGT_URL = os.getenv('FGT_URL', 'https://192.168.1.1/api/v2/cmdb/system/dns-database/')  # default to the given URL if FGT_URL is not set

# Setup logging
handler = RotatingFileHandler('dns_update.log', maxBytes=10*1024*1024, backupCount=1)  # Will keep 1 old log file, each 10MB big
handler.setLevel(logging.INFO)  # Log info and above to file
app.logger.addHandler(handler)
>>>>>>> branch2

=======
>>>>>>> dec37ade972140c851680815f4c8546b93e4e120
@app.route('/dns_update', methods=['POST'])
def dns_update():
    data = json.loads(request.data)

    # Check if required data is present
    if not all(key in data for key in ('ip', 'hostname')):
        return jsonify({'message': 'Invalid data, ip and hostname are required'}), 400

    print(f"Received data: {data}") # Print received data
    ip = data['ip']
    hostname = data['hostname']

    headers = {'Authorization': f'Bearer {os.getenv("API_TOKEN")}'}

    response = requests.get(f'{FGT_URL}{DATABASE_NAME}', headers=headers, verify=False)
    print(f"GET Response: {response.text}") # Print GET response
    dns_data = response.json()
    dns_entries = dns_data['results'][0]['dns-entry']

    for entry in dns_entries:
        if entry['ip'] == ip and entry['hostname'] == hostname:
            # If a record already exists that contains the same IP & the same hostname, do nothing.
            print("Record exists with same IP and hostname") # Debug message
            return jsonify({'message': 'Record exists with same IP and hostname'}), 200
        elif entry['hostname'] == hostname or entry['ip'] == ip:
            # If a record already exists with the same hostname but different IP, or same IP but different hostname,
            # execute another API call to delete the old entry (HTTP DELETE)
            response = requests.delete(f'{FGT_URL}{DATABASE_NAME}/{entry["id"]}', headers=headers, verify=False)
            print(f"DELETE Response: {response.text}") # Print DELETE response
            if response.status_code != 204:
                return jsonify({'message': 'Failed to delete record'}), 500

    # If there are no entries present that contain the IP or hostname from DHCP event log,
    # use the HTTP PUT method to add a new entry without removing existing ones.
    new_entry = {
        "status": "enable",
        "type": "A",
        "ttl": 1800,
        "preference": 65535,
        "ip": ip,
        "hostname": hostname
    }
    dns_entries.append(new_entry)

    put_data = {"name": DATABASE_NAME, "dns-entry": dns_entries}

    response = requests.put(f'{FGT_URL}{DATABASE_NAME}', json=put_data, headers=headers, verify=False)
    print(f"PUT Response: {response.text}") # Print PUT response

    if response.status_code != 200:
        return jsonify({'message': 'Failed to create record'}), 500

    return jsonify({'message': 'Record created successfully'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
