# DNS Updater

## Description
This script uses a Flask app and the Fortigate API to update DNS records based on DHCP events.
When a FortiGate is acting as a DNS & DHCP server, DNS entries are not automatically updated when DHCP assigns addresses. This script addresses the aforementioned shortcoming.

## Create API User, Access profile & API key on FortiGate
### Create API User Access Profile
```
config system accprofile
 edit **accprofile-name**
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
 edit **api-username**
  set accprofile **accprofile-name**
  set vdom "root"
 next
end
```

### Create API User Access Profile
```
exec api-user generate-key **api-username**
```

## Installation
1. Install Flask and any other necessary libraries: `pip install flask`.
2. Set the API_TOKEN environment variable: `export API_TOKEN=your_api_token_here`.
3. Make sure the script is executable: `chmod +x dns_updater.py`.

## Usage
To start the Flask app, run: `./dns_updater.py`.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
