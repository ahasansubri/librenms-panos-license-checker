# Troubleshooting

## JSON validation prints nothing

This is expected when output is redirected to `/dev/null`:

```bash
python3 -m json.tool /etc/librenms/panos-license/192.0.2.10.json >/dev/null
```

Check the exit code or append a confirmation:

```bash
python3 -m json.tool \
  /etc/librenms/panos-license/192.0.2.10.json >/dev/null \
  && echo "JSON syntax valid"
```

## Configuration file not found

The filename must match the value passed by LibreNMS with `-H`:

```text
/etc/librenms/panos-license/<HOST>.json
```

Use `check-services.php -d` to see the exact host value.

## Works as root but not as librenms

```bash
namei -l /etc/librenms/panos-license/192.0.2.10.json
sudo -u librenms test -r \
  /etc/librenms/panos-license/192.0.2.10.json \
  && echo "Configuration readable"
```

Expected ownership/modes:

```text
Directory: root:librenms 0750
File:      root:librenms 0640
```

## HTTP 401, 403, or PAN-OS API error

- Confirm the key came from the same firewall being queried.
- Confirm the administrator exists and is enabled.
- Confirm the role permits XML API Operational Requests.
- Confirm the PAN-OS configuration was committed.

## TLS Certificate Verification Failure

A TLS verification error means the checker can reach the PAN-OS management interface, but Python cannot establish trust in the HTTPS certificate.

Common causes include:

* The firewall uses a self-signed certificate.
* The certificate was issued by an internal CA that Ubuntu does not trust.
* The certificate has expired.
* The certificate hostname does not match the address used by the checker.
* An intermediate CA certificate is missing.
* The configured `ca_file` does not exist or is unreadable by `librenms`.

### Confirm that TLS verification is the problem

Run the checker once with `--insecure`:

```bash
sudo -u librenms \
  /usr/lib/nagios/plugins/check_panos_license \
  -H 192.0.2.10 \
  -w 60 -c 30 \
  --insecure
```

If the check succeeds with `--insecure` but fails without it, certificate verification is the likely cause.

> **Warning:** Do not add `--insecure` permanently to the LibreNMS service parameters. It disables certificate authenticity and hostname verification for that execution.

### Temporarily disable TLS verification in the device configuration

For controlled testing, edit the firewall’s configuration file:

```bash
sudo nano /etc/librenms/panos-license/192.0.2.10.json
```

Set:

```json
{
  "host": "192.0.2.10",
  "api_key": "PASTE_THE_RESTRICTED_API_KEY_HERE",
  "verify_tls": false,
  "ca_file": "",
  "timeout": 20,
  "ignore_features": []
}
```

Validate the JSON:

```bash
python3 -m json.tool \
  /etc/librenms/panos-license/192.0.2.10.json >/dev/null \
  && echo "JSON syntax valid"
```

Confirm that the `librenms` account can read it:

```bash
sudo -u librenms test -r \
  /etc/librenms/panos-license/192.0.2.10.json \
  && echo "Configuration readable"
```

Test the checker:

```bash
sudo -u librenms \
  /usr/lib/nagios/plugins/check_panos_license \
  -H 192.0.2.10 \
  -w 60 -c 30
```

When `"verify_tls": false`, the checker does not validate the firewall certificate and the `ca_file` setting is ignored.

This configuration can be used during initial testing, but trusted certificate validation is recommended for production.



### Recommended final production configuration

When the CA is installed in Ubuntu’s trust store:

```json
{
  "host": "panos-fw01.example.net",
  "api_key": "PASTE_THE_RESTRICTED_API_KEY_HERE",
  "verify_tls": true,
  "ca_file": "",
  "timeout": 20,
  "ignore_features": []
}
```

When using a checker-specific private CA bundle:

```json
{
  "host": "panos-fw01.example.net",
  "api_key": "PASTE_THE_RESTRICTED_API_KEY_HERE",
  "verify_tls": true,
  "ca_file": "/etc/librenms/panos-license/ca/panos-management-ca.pem",
  "timeout": 20,
  "ignore_features": []
}
```

When temporarily bypassing certificate verification:

```json
{
  "host": "192.0.2.10",
  "api_key": "PASTE_THE_RESTRICTED_API_KEY_HERE",
  "verify_tls": false,
  "ca_file": "",
  "timeout": 20,
  "ignore_features": []
}
```


## Connection refused or timeout

- Confirm routing from LibreNMS to the management interface.
- Confirm TCP/443 is permitted.
- Confirm HTTPS management/API access is enabled.
- Confirm `host` in the JSON file is correct.
- Increase `timeout` only after resolving network issues.

## No parseable licence entries

The API request succeeded but returned no supported expiring licence records.
Run the direct API test from `FIREWALL_API_SETUP.md`. Sanitize the output before
sharing it: remove the API key, serial number, Authcode, internal address, and
organization-specific details.

## CRITICAL and exit code 2

If the message lists an expired or near-expiry licence, the plugin is working.
Nagios exit code `2` means Critical—not a Python error.

## Services menu missing

```bash
sudo -u librenms /opt/librenms/lnms config:get show_services
sudo -u librenms /opt/librenms/lnms config:get nagios_plugins
```

Refresh the browser or sign out and back in after correcting the settings.

## GUI does not refresh automatically

Refreshing the Services page does not execute the plugin. Verify that exactly
one service scheduler is configured and run:

```bash
cd /opt/librenms
sudo -u librenms ./check-services.php -d
```

## Duplicate licence rows

A manual service and a template-created service may both exist. Identify them
first, then delete only the confirmed older manual service through the GUI.

