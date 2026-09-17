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

## TLS certificate failure

Configure the issuing CA using `ca_file` or the Ubuntu trust store. Use
`--insecure` only to prove that certificate validation is the cause; do not add
it permanently to LibreNMS service parameters.

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

