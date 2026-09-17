# Operations

## Normal five-minute cycle

1. LibreNMS selects the active `panos_license` service.
2. It executes the plugin as the `librenms` operating-system user.
3. The plugin loads `/etc/librenms/panos-license/<HOST>.json`.
4. It queries the PAN-OS XML API over HTTPS.
5. It evaluates licence expiry dates.
6. It prints one safe Nagios-compatible result and exits.
7. LibreNMS stores the state and message for the Services page.

## Manual health check

```bash
sudo -u librenms \
  /usr/lib/nagios/plugins/check_panos_license \
  -H 192.0.2.10 -w 60 -c 30
```

## Full LibreNMS service check

```bash
cd /opt/librenms
sudo -u librenms ./check-services.php -d
```

Do not add `-d` to cron.

## Inspect stored state

```bash
sudo mysql -D librenms -e "
SELECT service_id,
       device_id,
       service_type,
       service_status,
       FROM_UNIXTIME(service_changed) AS last_state_change,
       service_message
FROM services
WHERE service_type = 'panos_license'
ORDER BY device_id, service_id;"
```

`Last Changed` represents the last state transition—for example, OK to Warning—not
the most recent poll time.

## Rotate an API key

1. Generate a replacement key on the corresponding firewall.
2. Edit only that firewall's protected JSON file.
3. Run the plugin manually as `librenms`.
4. Confirm the API check succeeds.
5. Revoke the old credential when supported by the platform/account workflow.
6. Confirm the next scheduled LibreNMS service run.

## Update the plugin

```bash
git pull --ff-only
./scripts/check_repository.sh
sudo ./scripts/install.sh
cd /opt/librenms
sudo -u librenms ./check-services.php -d
```

The installer does not overwrite files under `/etc/librenms/panos-license/`.

