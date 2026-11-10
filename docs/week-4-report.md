# Week 4 Report — Manual API Testing with Burp Suite (Part 1)

**Project:** Fitness API Security Assessment & Hardening Framework
**Phase:** Week 4 of 12 — Foundation
**Author:** JPR Solutions Internship Project
**Date:** 2026-11-10

---

## 1. Objective

Begin manual API penetration testing with Burp Suite: install and configure it,
proxy client traffic through it, intercept and analyse API requests, and run a
basic brute-force attack against a login endpoint. All testing was performed
against a **locally-hosted practice API that we built and own** (`app/fitness_api.py`),
in line with authorised, educational security testing.

## 2. Scope

| In scope | Out of scope |
|----------|--------------|
| `http://127.0.0.1:5000` (local Fitness API) | Any third-party or production system |
| `/api/login`, `/api/users/<id>/profile`, `/api/workouts` | Denial-of-service / destructive testing |
| Interception, analysis, single-field login brute force | Automated active scanning |

## 3. Environment

- **Proxy:** Burp Suite Community Edition, listener `127.0.0.1:8080`.
- **Target:** Flask 3.0.3 API on `127.0.0.1:5000` (see `app/`).
- **Clients:** `curl` with `-x http://127.0.0.1:8080`; optionally a browser via FoxyProxy.
- **Supporting script:** `scripts/bruteforce_login.py` (reproducible brute force).

## 4. Work performed

1. **Installed & configured Burp CE** — temporary project, confirmed the proxy
   listener. *(doc 01)*
2. **Configured the proxy** — `curl` and browser routed through `127.0.0.1:8080`;
   documented CA-cert install for future HTTPS targets. *(doc 02)*
3. **Intercepted & analysed requests** — login and authenticated profile access,
   read raw HTTP, inspected the token in Decoder, replayed in Repeater. *(doc 03)*
4. **Brute-forced the login** — Burp Intruder (Sniper) against `/api/login`,
   plus a scripted equivalent for repeatable evidence. *(doc 04)*

## 5. Findings

| # | Finding | OWASP API Top 10 (2023) | Severity | Status |
|---|---------|-------------------------|----------|--------|
| F1 | No rate limiting / lockout on login → brute forceable | API4 / API2 | High | Open |
| F2 | Profile endpoint returns any `user_id` (BOLA/IDOR) | API1 | High | Open |
| F3 | Login errors distinguish unknown user vs wrong password (enumeration) | API2 | Medium | Open |
| F4 | Credentials & token sent over plain HTTP | API8 / transport | High | Open |
| F5 | Bearer token unsigned and non-expiring | API2 | Medium | Open |

### Headline evidence (F1)
A 20-word list recovered `ben@fitnesshub.test` → `password123` in **14
unthrottled attempts (~0.02s)** with no lockout. Full transcript:
`evidence/bruteforce_run_output.txt`.

### F2 proof
Alice's token (`user_id 1001`) read Coach Tembo's profile (`user_id 1003`) by
changing the URL in Repeater — authentication without authorization.

## 6. Recommendations (to be implemented in later hardening weeks)

- **F1:** per-IP + per-account rate limiting, exponential backoff, lockout after
  N failures, optional CAPTCHA/MFA, enforce a strong password policy.
- **F2:** authorise every object access — compare token owner to requested
  `user_id`; return `403`/`404` on mismatch.
- **F3:** single generic auth error and uniform `401` for all login failures.
- **F4:** enforce HTTPS/TLS, HSTS, no secrets over plain HTTP.
- **F5:** signed, expiring tokens (e.g. JWT with short TTL) or opaque tokens with
  server-side expiry and rotation.

## 7. Deliverables produced

- ✅ Documented Burp Suite setup & proxy configuration — `docs/01`, `docs/02`.
- ✅ Interception & analysis notes — `docs/03`.
- ✅ Brute-force notes + reproducible evidence — `docs/04`,
  `evidence/bruteforce_run_output.txt`, `scripts/bruteforce_login.py`.
- ✅ Screenshot placeholders & naming guide — `evidence/README.md`.
- ✅ Local practice target — `app/fitness_api.py`.

## 8. Next week (Week 5 preview)
Deeper manual testing: authorization/BOLA at scale, injection probing, and
beginning to turn these manual findings into custom Python security scripts.
