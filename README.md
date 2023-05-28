# DNS Updater

## Description
This script uses a Flask app and the Fortigate API to update DNS records based on DHCP events.
When a FortiGate is acting as a DNS & DHCP server, DNS entries are not automatically updated when DHCP assigns addresses. This script addresses the aforementioned shortcoming.

## Create API User, Access profile & API key on FortiGate
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

### Create API User Access Profile
```
exec api-user generate-key <api-username>
```

## Create Automation Stitch on FortiGate

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
1. Install Flask and any other necessary libraries: `pip install flask`.
2. Set the API_TOKEN environment variable: `export API_TOKEN=your_api_token_here`.
3. Set the DATABASE_NAME environment variable: `export DATABASE_NAME=localdb`
4. Set the FGT_URL environment variable: `export FGT_URL=https://192.168.1.1/api/v2/cmdb/system/dns-database/`
5. Make sure the script is executable: `chmod +x dns_updater.py`.

## Usage
To start the Flask app, run: `./dns_updater.py`.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
