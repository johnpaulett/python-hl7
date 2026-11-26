# Security Policy

## Supported versions

Security fixes go into `main` and ship in the next release on PyPI.
Older releases are not patched, so please upgrade to the latest version.

| Version | Supported |
| ------- | --------- |
| 0.4.x (latest release and `main`) | Yes |
| < 0.4 | No |

## Reporting a vulnerability

Please do not open a public issue, pull request or discussion for a security problem.

Report it privately through GitHub instead: go to the **Security** tab of this
repository and click **Report a vulnerability**. This opens a private advisory
that only the maintainers can see.

If that button is not shown, open an issue that only asks for a private
contact, with no details of the problem.

Please include:

- the affected version or commit
- what an attacker could do, and under what conditions
- steps to reproduce, ideally a small script or a sample message

## Test data

HL7 messages often carry patient information. Never include real patient data
in a report. Use synthetic or fully de-identified messages only.

## What to expect

python-hl7 is maintained by volunteers, so response times are best effort. We
will confirm the report, work on a fix in the private advisory, and credit you
in the advisory and the changelog unless you ask us not to. Please give us a
reasonable amount of time to release a fix before you disclose the issue
publicly.
