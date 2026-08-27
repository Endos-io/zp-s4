Unaffiliated snapshot of https://github.com/zarr-developers/zarr-python
at commit a994a4fc972fed428eab6a26d4f14bb95d22c144.

The source tree is unmodified from that commit. The only changes in this
repository are:

  1. .github/workflows/ replaced with a single baseline workflow
     (reef-baseline.yml, workflow_dispatch only).
  2. This file.
  3. Held-out tests added to tests/ (this commit).
  4. Automation configs removed, so nothing rewrites this snapshot:
       .github/dependabot.yml   (deleted)
       .pyup.yml                (deleted)
       .pre-commit-config.yaml  (the `ci:` block removed; the file is kept,
                                 it is still read by local hooks)

Original licence retained; see LICENSE.txt.
