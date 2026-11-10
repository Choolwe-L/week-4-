# Evidence

Artifacts captured during the Week 4 exercise.

## Files here

- **`bruteforce_run_output.txt`** — captured transcript of
  `scripts/bruteforce_login.py` recovering a password with no lockout.

## Screenshots to add from your own Burp session

Capture these from your Burp Suite run and save them here with these exact
names (referenced from `docs/04-burp-intruder-bruteforce.md`):

| Filename | What it should show |
|----------|---------------------|
| `01-proxy-listener.png` | Proxy settings with a listener running on `127.0.0.1:8080`. |
| `02-login-intercepted.png` | A paused `POST /api/login` in **Proxy → Intercept**. |
| `03-intruder-positions.png` | Intruder **Positions** tab with `§password§` marked and the payload list loaded. |
| `04-intruder-results.png` | Intruder **results** sorted by Status, the single `200` row highlighted. |

### Tips for good screenshots
- Include the full Burp window so the active tab is visible.
- For the results shot, make sure the **Status** and **Length** columns are
  visible — they are what proves the attack succeeded.
- Redact nothing: this is a lab target you own, so the data is safe to show.
