# PAN-OS Licence Checker for LibreNMS

A small, dependency-free Python plugin that reads Palo Alto Networks firewall
licence information through the PAN-OS XML API and displays the result in the
LibreNMS **Services** page.

The LibreNMS check type is:

```text
panos_license
```

## What it does

Every five minutes, LibreNMS can run the checker for each PAN-OS firewall. The
checker:

1. Loads that firewall's protected API key file.
2. Sends the PAN-OS operational request `request license info` over HTTPS.
3. Reads each feature and expiry date.
4. Calculates the number of days remaining.
5. Returns an OK, Warning, Critical, or Unknown result to LibreNMS.

It does **not** use SNMP, an SNMP trap, a database password, or a background
agent on the firewall.

## Default status thresholds

| Exit code | LibreNMS state | Default meaning |
|---:|---|---|
| `0` | OK | All evaluated licences have more than 60 days remaining |
| `1` | Warning | At least one licence has 31–60 days remaining |
| `2` | Critical | A licence has 30 days or fewer remaining, or is expired |
| `3` | Unknown | Configuration, API, TLS, connectivity, or parsing failed |

An exit code of `2` is not a script failure when a licence is actually expired;
it means the checker worked and detected a Critical condition.

## Requirements

- LibreNMS with Services enabled
- Python 3.10 or newer
- HTTPS connectivity from LibreNMS to the PAN-OS management interface
- A restricted PAN-OS administrator with XML API **Operational Requests**
- One API key and protected configuration file per physical firewall

The plugin uses only the Python standard library.

## Beginner quick start

### 1. Create the restricted PAN-OS account

Create an administrator role such as `LibreNMS-License-Reader` and enable only:

```text
XML API → Operational Requests
```

Create an administrator such as `librenms-api`, assign that role, and commit the
PAN-OS configuration.

Full instructions: [Firewall API setup](docs/FIREWALL_API_SETUP.md).

### 2. Install the plugin

```bash
git clone https://github.com/YOUR-USERNAME/librenms-panos-license-checker.git
cd librenms-panos-license-checker
sudo ./scripts/install.sh
```

### 3. Create one protected configuration

The following example uses the documentation address `192.0.2.10`. Replace it
with the firewall management address stored as the LibreNMS hostname.

```bash
sudo install -o root -g librenms -m 0640 \
  examples/config.json.example \
  /etc/librenms/panos-license/192.0.2.10.json

sudo nano /etc/librenms/panos-license/192.0.2.10.json
```

Set the real host and API key. Do not commit that file to Git.

### 4. Test as the LibreNMS user

```bash
sudo -u librenms \
  /usr/lib/nagios/plugins/check_panos_license \
  -H 192.0.2.10 \
  -w 60 -c 30

echo "Exit code: $?"
```

Because the filename matches the host, `--config` is optional. The checker
automatically opens:

```text
/etc/librenms/panos-license/<HOST>.json
```

### 5. Add the LibreNMS service

For one device, create a service using:

| Field | Value |
|---|---|
| Device | The corresponding PAN-OS firewall |
| Check Type | `panos_license` |
| Description | `Palo Alto Licence Expiry` |
| Remote Host | Leave blank |
| Parameters | `-w 60 -c 30` |

For multiple firewalls, use a Service Template assigned to a Palo Alto dynamic
device group. See [LibreNMS setup](docs/LIBRENMS_SETUP.md).

## Important HA rule

Monitor both members of a PAN-OS HA pair. Each physical firewall has its own:

- management address;
- API key;
- serial number;
- subscriptions and expiry dates;
- LibreNMS service state.

Create a separate JSON file and service instance for each member.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Firewall API setup](docs/FIREWALL_API_SETUP.md)
- [Installation](docs/INSTALLATION.md)
- [LibreNMS setup](docs/LIBRENMS_SETUP.md)
- [Multiple firewalls and HA](docs/MULTIPLE_FIREWALLS.md)
- [Operations](docs/OPERATIONS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Publishing to GitHub](docs/PUBLISHING.md)
- [Security policy](SECURITY.md)

Official background documentation:

- [LibreNMS Nagios Plugins and Services](https://docs.librenms.org/Extensions/Services/)
- [Palo Alto Networks: Get Started with the PAN-OS XML API](https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-panorama-api/get-started-with-the-pan-os-xml-api)

## Privacy and output safety

The checker does not print the API key, firewall serial number, or licence
Authcode. It prints only feature names, expiry dates, calculated remaining
days, and the overall state.

## Maintainer

Ahasan Subri

## Licence

No licence file is included. Public visibility alone does not grant permission
to copy, modify, or redistribute this project. An explicit open-source licence
can be added later if the maintainer chooses to grant those rights.
