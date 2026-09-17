# Contributing

Contributions should preserve the following behavior:

- Python standard-library-only execution;
- Nagios return codes `0`, `1`, `2`, and `3`;
- no secrets, serial numbers, or Authcodes in output;
- compatibility with both structured and CLI-style PAN-OS XML API results;
- one protected configuration file per firewall.

Before submitting a pull request:

```bash
python3 -m py_compile plugins/check_panos_license
python3 -m unittest discover -s tests -p 'test_*.py' -v
./scripts/check_repository.sh
```

Sanitize every API response, screenshot, log, hostname, and address included in
an issue or pull request.

