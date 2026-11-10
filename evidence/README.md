# Evidence

Artifacts captured during the Week 4 exercise. The brute-force deliverable
("screenshot/**notes**") is satisfied by the written notes and raw HTTP captures
below — **screenshots are optional**.

## Files here (complete, no action needed)

- **`bruteforce_notes.md`** — written notes of the brute-force attempt: setup,
  the status/length signal, result, and the finding. *This is the primary
  evidence.*
- **`bruteforce_http_capture.txt`** — real raw HTTP request/response pairs for a
  failing guess, another failing guess, and the successful one (shows the
  `401`/Content-Length 31 vs `200`/Content-Length 95 difference).
- **`bruteforce_run_output.txt`** — full transcript of
  `scripts/bruteforce_login.py` recovering the password with no lockout.

## Optional: screenshots (only if you run Burp's GUI yourself)

Not required — the files above already document the attack. If you *do* open
Burp Suite and want to add screenshots, save them here with these names (they
are referenced from `docs/04-burp-intruder-bruteforce.md`):

| Filename | What it would show |
|----------|---------------------|
| `01-proxy-listener.png` | Proxy settings with a listener running on `127.0.0.1:8080`. |
| `02-login-intercepted.png` | A paused `POST /api/login` in **Proxy → Intercept**. |
| `03-intruder-positions.png` | Intruder **Positions** tab with `§password§` marked and the payload list loaded. |
| `04-intruder-results.png` | Intruder **results** sorted by Status, the single `200` row highlighted. |
