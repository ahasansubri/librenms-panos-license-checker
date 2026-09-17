# Publish as a Separate GitHub Repository

Recommended repository name:

```text
librenms-panos-license-checker
```

Recommended description:

```text
PAN-OS XML API licence expiry checker for LibreNMS Services
```

Do not place this project inside the earlier combined
`librenms-license-checkers` repository. Create a new, empty GitHub repository.

## GitHub repository creation

When creating the repository, do not initialize it with:

- README;
- `.gitignore`;
- licence.

Those files are already handled locally, except the intentionally absent
licence.

## Command-line publication

```bash
git init
git add .
git commit -m "Initial release: PAN-OS licence checker for LibreNMS"
git branch -M main
git remote add origin \
  https://github.com/YOUR-USERNAME/librenms-panos-license-checker.git
git push -u origin main
```

If Git does not know your identity:

```bash
git config --global user.name "YOUR NAME"
git config --global user.email "YOUR VERIFIED GITHUB EMAIL"
```

## Windows Git GUI

1. Extract the repository package.
2. Open Git GUI and choose **Create New Repository** using the extracted folder.
3. Configure identity under **Edit → Options** when required.
4. Select **Stage Changed**.
5. Before committing, open Git Bash in the repository and preserve the Linux
   executable modes:

   ```bash
   git update-index --chmod=+x plugins/check_panos_license
   git update-index --chmod=+x scripts/install.sh
   git update-index --chmod=+x scripts/preflight.sh
   git update-index --chmod=+x scripts/check_repository.sh
   git ls-files -s plugins/check_panos_license scripts
   ```

   Each executable should show mode `100755`.

6. Return to Git GUI, use the commit message shown above, and select **Commit**.
7. After the first commit, run `git branch -M main` in Git Bash.
8. In Git GUI, choose **Remote → Add**, name it `origin`, and enter the empty
   repository URL.
9. Choose **Remote → Push** and push `main`.

A branch cannot be created from an empty revision. Make the first commit before
renaming `master` to `main`.

## Before every push

```bash
./scripts/check_repository.sh
git status --short
git diff --check
git diff --cached
```

Inspect the staged changes for API keys, internal addresses, hostnames, serial
numbers, Authcodes, and complete production API responses.

## File mode check

Git must store the plugin and shell scripts as executable:

```bash
git ls-files -s plugins/check_panos_license scripts/*.sh
```

Expected mode:

```text
100755
```

Correct it when necessary:

```bash
git update-index --chmod=+x plugins/check_panos_license
git update-index --chmod=+x scripts/install.sh
git update-index --chmod=+x scripts/preflight.sh
git update-index --chmod=+x scripts/check_repository.sh
```

## First release

```bash
git tag -a v1.0.0 -m "PAN-OS licence checker v1.0.0"
git push origin v1.0.0
```

Use the `CHANGELOG.md` version entry for the GitHub Release notes.

## Licence status

This repository intentionally has no `LICENSE` file. Add one only if you decide
to grant explicit rights to reuse, modify, and redistribute the code.
