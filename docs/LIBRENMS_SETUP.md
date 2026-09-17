# LibreNMS Services Setup

## 1. Confirm the Services framework

```bash
sudo -u librenms /opt/librenms/lnms config:get show_services
sudo -u librenms /opt/librenms/lnms config:get nagios_plugins
dpkg -s monitoring-plugins 2>/dev/null | grep '^Status:'
sudo grep -n 'services-wrapper.py' /etc/cron.d/librenms
```

After enabling Services, refresh the browser or sign out and back in if the
Services menu is not immediately visible.

## 2. Ensure one scheduler is active

LibreNMS may run service checks through its Dispatcher Service or through a
cron entry. Do not configure both methods for the same checks.

For the cron method, the standard five-minute entry is:

```cron
*/5 * * * * librenms /opt/librenms/services-wrapper.py 1
```

Do not include `-d` in cron. Debug mode is for manual troubleshooting only.

Before adding that entry, inspect the existing scheduler configuration and
confirm that another Services scheduler is not already active.

Verify the wrapper:

```bash
sudo -u librenms test -x /opt/librenms/services-wrapper.py \
  && echo "Service wrapper is executable"
```

## 3. Add a service for one firewall

Use the corresponding firewall under **Services → Add Service**:

| Field | Value |
|---|---|
| Name | Palo Alto Licence Expiry |
| Device | The PAN-OS firewall |
| Check Type | `panos_license` |
| Description | Palo Alto Licence Expiry |
| Remote Host | Leave blank |
| Parameters | `-w 60 -c 30` |

The device's LibreNMS hostname is passed with `-H`. The checker automatically
opens `/etc/librenms/panos-license/<HOST>.json`.

## 4. Create a template for multiple firewalls

First create a dynamic Palo Alto device group. A typical condition is:

```text
devices.os = "panos"
```

Verify the actual `os` value in your installation before using it.

Open **Services → Service Templates → Add Service Template**:

| Field | Value |
|---|---|
| Name | Palo Alto Licence Expiry |
| Device Type | Static |
| Select Devices | Leave empty |
| Device Groups | Select the Palo Alto dynamic group |
| Check Type | `panos_license` |
| Description | Palo Alto Licence Expiry |
| Remote Host | Leave empty |
| Parameters | `-w 60 -c 30` |

Enable automatic template application if desired:

```bash
sudo -u librenms /opt/librenms/lnms \
  config:set discover_services_templates true
```

Then click **Apply Services** for the template.

Important: automatic service creation does not create API keys. The matching
JSON file must already exist before the new service is polled.

## 5. Detect duplicate services

If a device already has a manually created service, applying the template may
leave two licence services for that device. Check before deleting anything:

```bash
sudo mysql -D librenms -e "
SELECT service_id, device_id, service_type, service_desc, service_status
FROM services
WHERE service_type = 'panos_license'
ORDER BY device_id, service_id;"
```

Retain the template-managed service and delete only the confirmed duplicate
manual service through the LibreNMS GUI.

## 6. Run a complete service debug

```bash
cd /opt/librenms
sudo -u librenms ./check-services.php -d
```

The request should resemble:

```text
'/usr/lib/nagios/plugins/check_panos_license' '-H' '192.0.2.10' '-w' '60' '-c' '30'
```

Then open **Services → All Services** and confirm the state and message.

## 7. Optional alerts

The checker works as a status dashboard without any alert rule. A Critical
service does not send email unless a matching LibreNMS alert rule and transport
exist.

Typical rule conditions are:

```text
services.service_status = 2
```

for Critical, and:

```text
services.service_status = 1
```

for Warning.

Turn off the service's **Alert Status** toggle when it should remain visible but
must never generate an alert.

