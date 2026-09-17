# Installation

## 1. Run the preflight check

From the repository directory:

```bash
./scripts/preflight.sh
```

Install the Ubuntu monitoring plugins if they are missing:

```bash
sudo apt update
sudo apt install monitoring-plugins -y
```

## 2. Enable LibreNMS Services

```bash
sudo -u librenms /opt/librenms/lnms config:set show_services true
sudo -u librenms /opt/librenms/lnms \
  config:set nagios_plugins /usr/lib/nagios/plugins
```

Confirm:

```bash
sudo -u librenms /opt/librenms/lnms config:get show_services
sudo -u librenms /opt/librenms/lnms config:get nagios_plugins
```

Expected values:

```text
true
/usr/lib/nagios/plugins
```

## 3. Install the checker

```bash
sudo ./scripts/install.sh
```

The installer creates:

```text
/usr/lib/nagios/plugins/check_panos_license
/etc/librenms/panos-license/
```

Confirm permissions:

```bash
ls -l /usr/lib/nagios/plugins/check_panos_license
sudo ls -ld /etc/librenms/panos-license
```

Expected modes:

```text
-rwxr-xr-x root root     check_panos_license
drwxr-x--- root librenms panos-license
```

## 4. Create the first protected configuration

Replace `192.0.2.10` with the exact hostname/address stored in LibreNMS:

```bash
sudo install -o root -g librenms -m 0640 \
  examples/config.json.example \
  /etc/librenms/panos-license/192.0.2.10.json

sudo nano /etc/librenms/panos-license/192.0.2.10.json
```

Example:

```json
{
  "host": "192.0.2.10",
  "api_key": "PASTE_THE_RESTRICTED_API_KEY_HERE",
  "verify_tls": true,
  "ca_file": "/etc/ssl/certs/organization-root-ca.pem",
  "timeout": 20,
  "ignore_features": []
}
```

If the certificate is trusted through Ubuntu's normal trust store, set
`ca_file` to an empty string.

## 5. Validate JSON and permissions

```bash
python3 -m json.tool \
  /etc/librenms/panos-license/192.0.2.10.json >/dev/null \
  && echo "JSON syntax valid"

sudo -u librenms test -r \
  /etc/librenms/panos-license/192.0.2.10.json \
  && echo "Configuration readable"
```

The JSON validation command intentionally produces no output on success because
its normal output is redirected to `/dev/null`. The `&& echo` confirms success.

## 6. Run a manual check

```bash
sudo -u librenms \
  /usr/lib/nagios/plugins/check_panos_license \
  -H 192.0.2.10 \
  -w 60 -c 30

echo "Exit code: $?"
```

An expired subscription should produce `CRITICAL` and exit code `2`. That is a
successful check result, not an execution failure.

## 7. Continue in LibreNMS

Follow [LibreNMS setup](LIBRENMS_SETUP.md) to configure scheduling and the
service or Service Template.

