# 02 — Proxy Configuration (Browser & `curl`)

**Deliverable:** Documented Burp Suite setup and proxy configuration

The goal: route client traffic through Burp's listener at **`127.0.0.1:8080`**
so we can intercept it. Below are three ways to do it. For this project the
target runs locally at `http://127.0.0.1:5000`, so plain HTTP is enough and the
CA-certificate step is only needed when you later test HTTPS targets.

---

## 1. Confirm Burp's listener

**Proxy → Proxy settings → Proxy listeners.** There should be one entry:

```
Running   Interface        Invisible   Redirect   TLS
  [x]     127.0.0.1:8080      [ ]         —         —
```

If it is not there, click **Add**, set **Bind to port** `8080`, **Bind to
address** `Loopback only`, and **OK**.

## 2. Option A — Browser via FoxyProxy (recommended)

Using the OS/browser proxy for *everything* is noisy. A browser extension lets
you flip the proxy on only when testing.

1. Install **FoxyProxy Standard** (Firefox or Chrome).
2. Add a proxy:
   - Title: `Burp`
   - Proxy type: `HTTP`
   - Host: `127.0.0.1`
   - Port: `8080`
3. Click the FoxyProxy icon → select **Burp** to turn it on; select **Disabled**
   to turn it off.

Browse to `http://127.0.0.1:5000/` — the request appears in **Proxy → HTTP
history**. (Firefox is preferred because it has its own proxy/cert store,
independent of the OS.)

## 3. Option B — System / OS proxy

Set the HTTP proxy to `127.0.0.1:8080` in OS network settings (Windows: *Settings
→ Network → Proxy*; macOS: *System Settings → Network → Proxy*). Simple, but it
proxies **all** apps — remember to turn it off afterwards.

## 4. Option C — `curl` through Burp (what this project leans on)

`curl` is the cleanest way to drive a JSON API through Burp. Use the `-x` flag:

```bash
# Send a login request THROUGH Burp (http)
curl -x http://127.0.0.1:8080 \
     -X POST http://127.0.0.1:5000/api/login \
     -H 'Content-Type: application/json' \
     -d '{"email":"alice@fitnesshub.test","password":"Sunshine2023"}'
```

The request now shows up in Burp's **HTTP history**, and if **Intercept is on**
Burp will pause it until you click **Forward**.

For an HTTPS target you would add Burp's CA (next section) or, for throwaway
local testing only, use `-k` to skip verification:

```bash
# HTTPS target, trusting Burp's interception cert via the exported CA
curl -x http://127.0.0.1:8080 --cacert ~/burp-ca.crt https://target.example/api/...
```

You can also export the proxy for a whole shell session:

```bash
export http_proxy=http://127.0.0.1:8080
export https_proxy=http://127.0.0.1:8080
curl http://127.0.0.1:5000/            # now goes through Burp automatically
unset http_proxy https_proxy           # stop proxying
```

## 5. Installing Burp's CA certificate (for HTTPS)

Burp decrypts HTTPS by presenting its own certificate. Clients reject it until
you trust Burp's CA. **Not required for the plain-HTTP local target**, but
document it for completeness / later weeks:

1. With the proxy active, browse to **`http://burp`** (or `http://burpsuite`).
2. Click **CA Certificate** → download `cacert.der`.
3. Trust it:
   - **Firefox:** *Settings → Privacy & Security → Certificates → View
     Certificates → Authorities → Import*, tick "Trust this CA to identify
     websites".
   - **curl/CLI:** convert and reference it —
     `openssl x509 -inform der -in cacert.der -out burp-ca.crt` then
     `curl --cacert burp-ca.crt ...`.

## 6. Verification checklist

- [ ] Burp listener running on `127.0.0.1:8080`.
- [ ] A request to `http://127.0.0.1:5000/` appears in **Proxy → HTTP history**.
- [ ] With **Intercept on**, the request pauses and **Forward** releases it.
- [ ] (HTTPS only) Burp CA imported; an HTTPS site loads with no cert warning.

Once a login request reliably shows up in HTTP history, the proxy is correctly
configured and we can move on to interception analysis.

---

**Next:** [`03-intercepting-requests.md`](03-intercepting-requests.md)
