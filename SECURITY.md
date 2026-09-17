# Security Policy

## Secrets

Never commit or publish:

- PAN-OS API keys or administrator passwords;
- live files from `/etc/librenms/panos-license/`;
- internal management addresses or hostnames;
- firewall serial numbers;
- licence Authcodes;
- unredacted XML API responses;
- packet captures or debug logs from production.

The repository contains only a sanitized example using the documentation
address `192.0.2.10`.

## PAN-OS account privilege

Use a dedicated administrator role that permits only XML API Operational
Requests. Do not use a superuser or a normal administrator's API key.

## File permissions

Use:

```text
/etc/librenms/panos-license/        root:librenms 0750
<management-address>.json          root:librenms 0640
check_panos_license                root:root     0755
```

The key must be readable by the `librenms` account but not by unprivileged
local users.

## TLS

Production installations should use `verify_tls: true`. Trust the firewall
certificate through the operating-system trust store or set `ca_file` to the
private CA certificate. Use `verify_tls: false` or `--insecure` only for a
controlled initial test.

## Exposure response

If an API key is disclosed, revoke or regenerate it on the firewall, update the
protected JSON configuration, and retest the service as `librenms`.

## Vulnerability reports

Do not place sensitive findings in a public GitHub issue. Contact the
maintainer privately with a sanitized reproduction.

