# 04 — Burp Intruder: Brute-Force / Fuzzing a Login Endpoint

**This week's task:** *Use Burp Intruder to perform basic brute-force or fuzzing
attacks on login endpoints.*
**Deliverable:** *Screenshot/notes of basic brute-force attempts on a login
endpoint.*

> **Authorisation note.** Everything below targets the **local practice API**
> that ships in this repo (`http://127.0.0.1:5000`), which we own. Password
> guessing against any system you do not own or have **written permission** to
> test is illegal. Keep this strictly on the lab target.

---

## 1. Capture a baseline login request

1. Proxy a single login through Burp (**Intercept off** is fine):

```bash
curl -x http://127.0.0.1:8080 -X POST http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"ben@fitnesshub.test","password":"guess"}'
```

2. In **Proxy → HTTP history**, right-click the `POST /api/login` row →
   **Send to Intruder**. Open the **Intruder** tab.

## 2. Mark the payload position

On **Intruder → Positions**:

1. Click **Clear §** to remove Burp's auto-selected positions.
2. Highlight just the password value in the body and click **Add §**:

```http
POST /api/login HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/json

{"email":"ben@fitnesshub.test","password":"§guess§"}
```

3. **Attack type: Sniper** (one payload set, one position — the classic
   single-field brute force).

## 3. Load the password payload set

On **Intruder → Payloads**:

- **Payload set 1**, type **Simple list**.
- **Load** `scripts/wordlists/common-passwords.txt`, or paste a list.
- (Optional) Under **Payload processing** you could add rules, e.g. capitalise,
  append digits — that is the "fuzzing" variation of the same attack.

## 4. Run the attack and read results

Click **Start attack**.

> **Community Edition** throttles Intruder (a short delay per request), so a
> 20-word list takes a few seconds and a large list is slow. That throttle is a
> CE limitation, **not** rate limiting on the target.

In the results window:

- Add/sort the **Status** column → the single **`200`** row is the valid
  password (every other guess is `401`/`404`).
- Sort by **Length** → the success response is longer because it contains the
  `token`. Length is the key signal when a target returns `200` for everything.
- Select the `200` row and read the **Response** tab to confirm
  `"message":"login successful"` and a `token`.

**Expected result:** the guess **`password123`** returns `200 OK` with a token —
Ben's real password. No lockout or throttling fires on the target, confirming
the missing rate-limit finding.

## 5. Scriptable equivalent (reproducible evidence)

Burp Intruder is point-and-click; for a repeatable artifact we reproduce the
exact same attack with `scripts/bruteforce_login.py`. Captured run:

```
$ python bruteforce_login.py --email ben@fitnesshub.test
[*] Target : http://127.0.0.1:5000/api/login
[*] Email  : ben@fitnesshub.test
[*] Guesses: 20 from wordlists/common-passwords.txt
------------------------------------------------------------
[   1/20] 123456               HTTP 401  incorrect password
[   2/20] password             HTTP 401  incorrect password
...
[  13/20] password1            HTTP 401  incorrect password
[  14/20] password123          HTTP 200  login successful  <== MATCH
------------------------------------------------------------
[+] Password found: 'password123' in 14 attempts, 0.02s
[+] No lockout or rate limiting was triggered -> VULNERABLE.
```

The full transcript is saved at
[`../evidence/bruteforce_run_output.txt`](../evidence/bruteforce_run_output.txt).

## 6. Evidence (notes, with screenshots optional)

The deliverable is "screenshot/**notes**", and the written notes plus raw HTTP
captures fully document the attack:

- [`../evidence/bruteforce_notes.md`](../evidence/bruteforce_notes.md) — written
  notes: setup, the status/length signal, result, and the finding.
- [`../evidence/bruteforce_http_capture.txt`](../evidence/bruteforce_http_capture.txt)
  — raw request/response pairs showing `401`/length 31 (miss) vs `200`/length 95 (hit).
- [`../evidence/bruteforce_run_output.txt`](../evidence/bruteforce_run_output.txt)
  — full brute-force transcript.

Screenshots are **optional**. If you run Burp's GUI yourself and want to add
them, the suggested filenames (`01-proxy-listener.png`, `02-login-intercepted.png`,
`03-intruder-positions.png`, `04-intruder-results.png`) are listed in
[`../evidence/README.md`](../evidence/README.md).

## 7. Finding & remediation summary

| Field | Value |
|-------|-------|
| **Finding** | No rate limiting / account lockout on `POST /api/login` |
| **OWASP** | API4:2023 Unrestricted Resource Consumption (brute force) + API2:2023 Broken Authentication |
| **Evidence** | 14 unthrottled guesses recovered `ben@fitnesshub.test` / `password123` |
| **Impact** | Any account with a weak password is guessable at machine speed |
| **Remediation (later week)** | Rate-limit by IP+account, exponential backoff, lockout after N failures, CAPTCHA, generic errors, MFA, strong password policy |

---

**Back to:** [`../README.md`](../README.md) ·
**Report:** [`week-4-report.md`](week-4-report.md)
