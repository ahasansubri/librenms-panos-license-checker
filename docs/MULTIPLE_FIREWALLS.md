# Multiple Firewalls and HA Pairs

## One file and one service per firewall

Every physical PAN-OS firewall requires its own:

- restricted API account/key;
- configuration file;
- LibreNMS device;
- `panos_license` service instance.

This applies even when two firewalls form an HA pair.

## Determine required filenames

List PAN-OS devices from LibreNMS:

```bash
sudo mysql -D librenms -e "
SELECT device_id, hostname, sysName
FROM devices
WHERE os = 'panos'
ORDER BY device_id;"
```

For every returned `hostname`, create:

```text
/etc/librenms/panos-license/<hostname>.json
```

Example documentation addresses:

```text
/etc/librenms/panos-license/192.0.2.10.json
/etc/librenms/panos-license/192.0.2.11.json
/etc/librenms/panos-license/192.0.2.12.json
```

Each file must contain the API key generated directly from that firewall.

## Add another firewall

```bash
sudo install -o root -g librenms -m 0640 \
  examples/config.json.example \
  /etc/librenms/panos-license/192.0.2.11.json

sudo nano /etc/librenms/panos-license/192.0.2.11.json

sudo -u librenms \
  /usr/lib/nagios/plugins/check_panos_license \
  -H 192.0.2.11 -w 60 -c 30
```

Only apply or create the LibreNMS service after the manual test succeeds or
returns an expected Warning/Critical licence state.

## New dynamic-group members

With `discover_services_templates` enabled, LibreNMS can add the service when a
new device joins the Palo Alto group. Prepare its JSON file first. Otherwise,
the first check returns:

```text
PANOS LICENCE UNKNOWN - configuration file not found
```

