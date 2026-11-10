# 03 — Intercepting & Analysing API Requests

**This week's task:** *Intercept and analyze various API requests (e.g., login,
user profile access).*

With the proxy configured, we now capture and read real requests/responses
against the local Fitness API. All commands assume the API is running
(`python app/fitness_api.py`) and that you are sending traffic through Burp
(`-x http://127.0.0.1:8080`).

---

## 1. Intercepting the login request

1. In Burp: **Proxy → Intercept → Intercept is on**.
2. Trigger a login (browser form, or `curl` below):

```bash
curl -x http://127.0.0.1:8080 \
     -X POST http://127.0.0.1:5000/api/login \
     -H 'Content-Type: application/json' \
     -d '{"email":"alice@fitnesshub.test","password":"Sunshine2023"}'
```

3. Burp pauses on the paused request. You see the raw HTTP:

```http
POST /api/login HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/json
Content-Length: 63

{"email":"alice@fitnesshub.test","password":"Sunshine2023"}
```

4. Click **Forward**. Turn **Intercept off** and open **HTTP history** to read
   the response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"message":"login successful","token":"jaLem5rnee6yPsd1",
 "token_type":"Bearer","user_id":1001}
```

### What to note (analysis)
- **Credentials are sent in the clear JSON body.** Over plain HTTP they are
  trivially readable — the service must enforce HTTPS.
- **The token is short (16 chars, URL-safe base64).** Paste it into **Decoder**:
  it decodes to 12 random bytes with no user data bound to it. That is better
  than an encoded `user_id`, but the token is not signed and the server keeps no
  expiry — flag for the hardening phase.
- **No `Set-Cookie`, no CSRF token** — this is a bearer-token API, so each
  protected request must carry `Authorization: Bearer <token>`.

## 2. Intercepting an authenticated profile request

Send a profile request with the token from step 1:

```bash
curl -x http://127.0.0.1:8080 \
     http://127.0.0.1:5000/api/users/1001/profile \
     -H 'Authorization: Bearer jaLem5rnee6yPsd1'
```

Response:

```json
{"email":"alice@fitnesshub.test","full_name":"Alice Mwansa",
 "goal":"Run a half marathon","plan":"premium","user_id":1001,"weight_kg":64.5}
```

### Analysis — the interesting part
The URL contains the object identifier `1001`. In Burp, send this request to
**Repeater** (right-click → *Send to Repeater*), change the path to
`/api/users/1003/profile`, and **Send**:

```json
{"email":"coach@fitnesshub.test","full_name":"Coach Tembo",
 "goal":"Help clients hit their targets","plan":"staff","user_id":1003, ...}
```

Alice's token just read **Coach Tembo's** profile. This is **Broken Object
Level Authorization (BOLA / IDOR)** — OWASP API Security Top 10 **API1:2023**.
The endpoint authenticates the *token* but never checks that the token's owner
is allowed to read the requested `user_id`. Captured here, fixed in a later
week.

## 3. Analysing the error responses (user enumeration)

Intercept two failed logins and compare the responses:

```bash
# wrong password for a REAL account
curl -x http://127.0.0.1:8080 -X POST http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@fitnesshub.test","password":"wrong"}'
# -> HTTP 401 {"error":"incorrect password"}

# an account that does NOT exist
curl -x http://127.0.0.1:8080 -X POST http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"ghost@fitnesshub.test","password":"wrong"}'
# -> HTTP 404 {"error":"no account found for that email"}
```

The **status code and message differ** (401 "incorrect password" vs 404 "no
account found"). An attacker can therefore enumerate valid accounts before
brute-forcing passwords. This is the signal our brute-force step sorts on, and
it maps to **API2:2023 Broken Authentication**. Fix: one generic message
(`"invalid email or password"`) and a uniform `401` for both cases.

## 4. Reading the HTTP history as evidence

**Proxy → HTTP history** is the running log. For each row you can see method,
URL, status, length, and MIME type, and the full request/response in the lower
panes. Columns to sort/filter on during analysis:

- **Status** — spot the 200 among 401s (successful login during a brute force).
- **Length** — a different response length often reveals a logic difference even
  when status codes match.
- **MIME type / extension** — filter to JSON to cut noise.

The local API also keeps a parallel log you can diff against Burp:

```bash
curl -s http://127.0.0.1:5000/api/_debug/requests | python -m json.tool
```

## 5. Summary of findings from interception

| # | Observation | OWASP API Top 10 | Severity |
|---|-------------|------------------|----------|
| 1 | Credentials/token sent over plain HTTP | API8 (Misconfig) / transport | High |
| 2 | Profile endpoint honours any `user_id` (BOLA/IDOR) | API1:2023 | High |
| 3 | Login errors distinguish unknown-user vs bad-password | API2:2023 | Medium |
| 4 | No rate limiting on login (see doc 04) | API4:2023 | High |
| 5 | Bearer token unsigned, no expiry | API2:2023 | Medium |

---

**Next:** [`04-burp-intruder-bruteforce.md`](04-burp-intruder-bruteforce.md) —
automate password guessing on `/api/login` with Burp Intruder.
