# PAN-OS Firewall API Setup

Complete this procedure on every physical firewall that will have a licence
service in LibreNMS.

## 1. Create a restricted administrator role

In PAN-OS, create an administrator role named, for example:

```text
LibreNMS-License-Reader
```

Enable only:

```text
XML API → Operational Requests
```

Do not assign superuser privileges. The checker only needs to execute the
licence-information operational request.

## 2. Create the API administrator

Create an administrator such as:

```text
librenms-api
```

Assign the restricted role and commit the firewall configuration.

## 3. Generate an API key safely

Run from the LibreNMS server. Replace `192.0.2.10` with the management address.

```bash
read -rsp "PAN-OS API password: " PAN_PASSWORD
echo

curl -sS -X POST "https://192.0.2.10/api/" \
  --data-urlencode "type=keygen" \
  --data-urlencode "user=librenms-api" \
  --data-urlencode "password=${PAN_PASSWORD}"

unset PAN_PASSWORD
```

If the firewall still uses an untrusted certificate during initial setup, add
`-k` temporarily to `curl`. Correct certificate trust before production use.

A successful response contains:

```xml
<response status="success">
  <result>
    <key>API_KEY_VALUE</key>
  </result>
</response>
```

Do not paste the returned key into chat, documentation, a GitHub issue, a shell
script, or LibreNMS service parameters.

## 4. Test licence retrieval before installing the plugin

```bash
read -rsp "PAN-OS API key: " PAN_API_KEY
echo

curl -sS -X POST "https://192.0.2.10/api/" \
  -H "X-PAN-KEY: ${PAN_API_KEY}" \
  --data-urlencode "type=op" \
  --data-urlencode 'cmd=<request><license><info/></license></request>'

unset PAN_API_KEY
```

Use `-k` only for controlled certificate troubleshooting.

A successful response begins with:

```xml
<response status="success">
```

and contains one or more `License entry:` records or structured licence
entries.

## 5. HA pairs

Repeat the complete process for both HA members. Generate each key directly
from the corresponding physical firewall. Do not assume one member's key or
licence response represents the other member.

