# Security policy

`codechu-cli` is a small CLI primitives library. It writes to stderr,
reads stdin, and manipulates terminal state via `termios`. It does
not touch the network or `subprocess`. The threat model is therefore
narrow — but a CLI that mishandles terminal state can leave a shell
unusable, and we treat that as security-relevant.

## Supported versions

| Version | Supported |
|---|:---:|
| `main` branch | ✅ |
| Latest minor release (0.x) | ✅ |
| Older releases | ❌ |

Pre-1.0.0 period — only the latest minor receives security fixes.

## Reporting a vulnerability

### Preferred path — GitHub Security Advisory (private)

Open a **private** advisory at
[github.com/codechu/cli-py/security/advisories/new](https://github.com/codechu/cli-py/security/advisories/new).
The disclosure stays non-public until a fix lands, and a CVE can be
requested automatically.

### Alternative — Email

Write to `security@codechu.com`.

## Scope — what to report

**In scope:**

- **Terminal-state leak** — `select` / `multiselect` exits without
  restoring `termios` (echo disabled, cbreak mode left enabled).
- **Unbounded input buffering** — a `prompt()` / `confirm()` flow
  that keeps reading until OOM on a hostile stdin.
- **Escape-sequence injection** — `banner()` or `Color` rendering
  caller-supplied text that lets an attacker rewrite arbitrary
  terminal regions via an unfiltered escape.
- **Password echo** — `prompt(password=True)` printing keystrokes to
  stderr/stdout.

**Out of scope:**

- A non-Unicode terminal not rendering emoji — by design; pass
  `CODECHU_CLI_EMOJI=never` or set `LANG=C`.
- Dependency vulnerabilities in `pytest` / `ruff` (dev-only).
- Misuse of the API (passing a closed stream to `Spinner`, etc.).

## Process

Reports are reviewed on a best-effort basis — no fixed SLA. We aim
for coordinated disclosure within **90 days** of the report,
extendable by mutual agreement if a fix is non-trivial.

Public disclosure is coordinated after the fix is released
(together with the reporter).

## Public disclosure

Once a confirmed fix is released:

- A summary is added to the CHANGELOG under the `### Security`
  category (with the reporter's name if they want credit).
- A GitHub Security Advisory is published.
- If a CVE was assigned, its number is referenced.
