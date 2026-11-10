# Brute-Force Attempt — Written Notes (Evidence)

**Deliverable:** *Screenshot/notes of basic brute-force attempts on a login endpoint.*
These written notes are the **notes** form of that deliverable. Burp screenshots
are optional; everything proven by a screenshot is captured here as text.

- **Target:** `POST http://127.0.0.1:5000/api/login` (local practice API, self-owned)
- **Account attacked:** `ben@fitnesshub.test`
- **Method:** Burp Intruder (Sniper, single payload position on `password`), and
  the scripted equivalent `scripts/bruteforce_login.py`
- **Payload set:** `scripts/wordlists/common-passwords.txt` (20 common passwords)
- **Date:** 2026-11-10

---

## 1. How the attack was set up

The `password` field of a captured login request is the single Intruder payload
position:

```http
POST /api/login HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/json

{"email":"ben@fitnesshub.test","password":"§PASSWORD§"}
```

Burp (or the script) then replays this request once per word in the list,
substituting each candidate into the `§...§` position.

## 2. What distinguishes a hit from a miss (the signal)

Every failed guess and the one successful guess differ in **both** status code
and response length — these are the exact columns you sort Intruder results on:

| Outcome | Status | Content-Length | Body |
|---------|--------|----------------|------|
| Wrong password (real account) | `401 UNAUTHORIZED` | **31** | `{"error":"incorrect password"}` |
| **Correct password** | `200 OK` | **95** | `{"message":"login successful","token":"...","token_type":"Bearer","user_id":1002}` |
| Unknown account | `404 NOT FOUND` | 41 | `{"error":"no account found for that email"}` |

So even without reading each body, the single `200` row (and its longer length)
is the valid credential. Raw captured request/response pairs for attempts #1,
#13 and #14 are in [`bruteforce_http_capture.txt`](bruteforce_http_capture.txt).

## 3. Result

- **Password recovered:** `ben@fitnesshub.test` → `password123`
- **Found on:** attempt **14 of 20**
- **Time:** ~0.02–0.03 s for all 20 attempts (scripted; Burp CE is slower only
  because of its built-in Intruder throttle, not because of any server defence)
- **Lockout / rate limiting observed:** **none** — all 20 requests were accepted
  and answered normally

Full run transcript: [`bruteforce_run_output.txt`](bruteforce_run_output.txt).

```
[  13/20] password1            HTTP 401  incorrect password
[  14/20] password123          HTTP 200  login successful  <== MATCH
------------------------------------------------------------
[+] Password found: 'password123' in 14 attempts, 0.03s
[+] No lockout or rate limiting was triggered -> VULNERABLE.
```

## 4. Finding

| Field | Value |
|-------|-------|
| **Vulnerability** | No rate limiting / account lockout on `POST /api/login` |
| **OWASP API Top 10 (2023)** | API4 (Unrestricted Resource Consumption) + API2 (Broken Authentication) |
| **Evidence** | 20 unthrottled guesses; valid password recovered on attempt 14 |
| **Impact** | Any account with a weak/common password is guessable at machine speed |
| **Secondary issue** | Verbose, differing errors (401 vs 404) also allow account enumeration |
| **Remediation (hardening phase)** | Per-IP + per-account rate limiting, exponential backoff, lockout after N failures, CAPTCHA/MFA, a single generic auth error, and a strong-password policy |

## 5. Optional screenshots

If you later run Burp Suite's GUI yourself and want to attach screenshots, the
suggested filenames are listed in [`README.md`](README.md). They are **not
required** — these notes and the two capture files above fully document the
brute-force attempt.
