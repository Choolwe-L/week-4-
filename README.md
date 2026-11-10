# Fitness API Security Assessment & Hardening Framework

**Internship project · JPR Solutions · Cybersecurity · Fitness & Wellness**

A 12-week project that takes a Flask-based Fitness API through a full API
security lifecycle: reconnaissance, manual and automated penetration testing,
reporting, and hardening with secure cloud deployment.

> **This repository currently covers Week 4 of 12.**

---

## Week 4 — Manual API Testing with Burp Suite (Part 1) · *Foundation*

### The problem
Begin manual API penetration testing using Burp Suite to intercept, inspect, and
modify API requests and responses.

### What was done this week
- Installed and configured **Burp Suite Community Edition**.
- Configured the browser and `curl` to **proxy traffic through Burp** (`127.0.0.1:8080`).
- **Intercepted and analysed** login and user-profile requests.
- Used **Burp Intruder** to run a basic **brute-force attack** on the login endpoint.

### Deliverables (Week 4)
| Deliverable | Where |
|-------------|-------|
| Documented Burp Suite setup & proxy configuration | [`docs/01-burp-suite-setup.md`](docs/01-burp-suite-setup.md), [`docs/02-proxy-configuration.md`](docs/02-proxy-configuration.md) |
| Interception & analysis notes | [`docs/03-intercepting-requests.md`](docs/03-intercepting-requests.md) |
| Brute-force attempt notes + evidence | [`docs/04-burp-intruder-bruteforce.md`](docs/04-burp-intruder-bruteforce.md), [`evidence/`](evidence/) |
| Week 4 written report | [`docs/week-4-report.md`](docs/week-4-report.md) |

---

## Repository layout

```
.
├── app/
│   ├── fitness_api.py        # Local practice target (deliberately insecure Flask API)
│   └── requirements.txt
├── docs/
│   ├── 01-burp-suite-setup.md
│   ├── 02-proxy-configuration.md
│   ├── 03-intercepting-requests.md
│   ├── 04-burp-intruder-bruteforce.md
│   └── week-4-report.md
├── scripts/
│   ├── bruteforce_login.py   # Reproducible login brute-force demo
│   ├── wordlists/common-passwords.txt
│   └── README.md
├── evidence/
│   ├── bruteforce_run_output.txt
│   └── README.md             # screenshot naming guide
└── README.md
```

## Quick start

> ⚠️ **Scope & authorisation.** The target API here is built for this project and
> runs on `localhost`. Only ever use the interception and brute-force techniques
> in this repo against systems you own or have **written permission** to test.

### 1. Run the target API
```bash
cd app
pip install -r requirements.txt
python fitness_api.py          # serves http://127.0.0.1:5000
```

### 2. Send traffic through Burp
```bash
curl -x http://127.0.0.1:8080 -X POST http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@fitnesshub.test","password":"Sunshine2023"}'
```
Follow [`docs/01`](docs/01-burp-suite-setup.md) and [`docs/02`](docs/02-proxy-configuration.md)
to set Burp up first.

### 3. Reproduce the brute-force finding
```bash
cd scripts
python bruteforce_login.py --email ben@fitnesshub.test
```

## Practice target — test accounts
The API ships with three accounts (plaintext passwords *on purpose*, so there is
an obvious finding to report):

| Email | Password | Plan |
|-------|----------|------|
| `alice@fitnesshub.test` | `Sunshine2023` | premium |
| `ben@fitnesshub.test` | `password123` | free |
| `coach@fitnesshub.test` | `Admin!2024` | staff |

## Findings captured this week
See [`docs/week-4-report.md`](docs/week-4-report.md). Summary: no login rate
limiting (brute forceable), BOLA/IDOR on the profile endpoint, user enumeration
via verbose errors, plaintext transport, and weak tokens — all mapped to the
**OWASP API Security Top 10 (2023)** and queued for the hardening phase.

---

*Educational security testing performed against a self-owned local target.*
