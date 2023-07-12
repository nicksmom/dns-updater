# DNS Updater

## Description
This script uses a Flask app and the Fortigate API to update DNS records based on DHCP events.
When a FortiGate is acting as a DNS & DHCP server, DNS entries are not automatically updated when DHCP assigns addresses. This script addresses the aforementioned shortcoming.

## On FortiGate, Create API User, Access profile & API_TOKEN
### Create API User Access Profile
```
config system accprofile
 edit <accprofile-name>
  set secfabgrp read
  set ftviewgrp read
  set authgrp read
  set sysgrp read-write
  set netgrp read-write
  set loggrp read
  set fwgrp read
  set vpngrp read
  set utmgrp read
  set wifi read
 next
end
```

### Create API User
```
config system api-user
 edit <api-username>
  set accprofile <accprofile-name>
  set vdom "root"
 next
end
```

### Generate API_TOKEN
```
exec api-user generate-key <api-username>
```

## On FortiGate, create Automation Stitch
### Create Automation Trigger based on DHCP event log

```
config system automation-trigger
 edit "DHCP Ack"
  set event-type event-log
  set logid 26001 26004
 next
end
```

### Create Automation Action webhook
#### Update URI as needed for your environment
#### URI must point to system running Flask app

```
config system automation-action
 edit "Send DHCP IP & Hostname to Flask"
  set action-type webhook
  set uri "192.168.1.2/dns_update"
  set http-body "{
 \"ip\": \"%%log.ip%%\",
 \"mac\": \"%%log.mac%%\",
 \"hostname\": \"%%log.hostname%%\"
}"
  set port 5000
  config http-headers
   edit 1
    set key "Content-Type"
    set value "application/json"
   next
  end
 next
end
```

### Create Automation Stitch using previously created trigger & action

```
config system automation-stitch
 edit "Add DNS Entry from DHCP Log"
  set trigger "DHCP Ack"
  config actions
   edit 1
    set action "Send DHCP IP & Hostname to Flask"
    set required enable
   next
  end
 next
end
```

## Installation
1. Install Flask and any other necessary libraries: `pip install flask jsonify`.
2. Set the API_TOKEN environment variable: `export API_TOKEN=your_api_token_here`.
3. Clone repository: `git clone https://github.com/nicksmom/dns-updater.git`
4. Set the DATABASE_NAME environment variable: `export DATABASE_NAME=localdb`
5. Set the FGT_URL environment variable: `export FGT_URL=https://192.168.1.1/api/v2/cmdb/system/dns-database/`
6. Make sure the script is executable: `chmod +x dns_updater.py`.

## Enable Service
1. Edit /etc/systemd/system/dns-update.service
```
[Unit]
Description=DNS Updater Service for FortiGate
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/your_script/dns-updater.py
WorkingDirectory=/path/to/your_script
Restart=always
User=pi
Environment="API_TOKEN=your_api_token"
Environment="DATABASE_NAME=my_database"
Environment="FGT_URL=https://192.168.1.1/api/v2/cmdb/system/dns-database/"

[Install]
WantedBy=multi-user.target
```
2. Reload the systemd daemon to read the new file: sudo systemctl daemon-reload
3. Enable service to start on boot: sudo systemctl enable dns-updater.service
4. Start service: sudo systemctl start dns-updater.service

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
