# 01 — Burp Suite Community Edition: Install & Setup

**Project:** Fitness API Security Assessment & Hardening Framework
**Week:** 4 of 12 — Manual API Testing with Burp Suite (Part 1)
**Deliverable:** Documented Burp Suite setup and proxy configuration

---

## 1. What Burp Suite is and why we use it

Burp Suite is an intercepting (man-in-the-middle) proxy for HTTP/HTTPS. We point
our client (browser or `curl`) at Burp instead of letting it talk directly to
the API. Burp sits in the middle, so every request and response passes through
it where we can **read it, pause it, edit it, replay it, and fuzz it**.

For API penetration testing this lets us:

- See the exact JSON, headers, and tokens the client sends.
- Modify a request before it reaches the server (e.g. change a `user_id`).
- Replay a captured request many times with different values (Intruder).
- Keep a full history of traffic as evidence.

The **Community Edition** is free. Compared with Professional it lacks the
active scanner and runs Intruder at a throttled speed, but it is fully capable
of the manual interception, Repeater, and (slow) Intruder work this project
needs.

## 2. Install

### Option A — Official installer (recommended)
1. Download Burp Suite Community Edition from PortSwigger:
   <https://portswigger.net/burp/communitydownload>
2. Run the installer for your OS:
   - **Windows:** run the `.exe`, accept defaults.
   - **macOS:** open the `.dmg`, drag Burp to Applications.
   - **Linux:** `chmod +x burpsuite_community_linux_*.sh && ./burpsuite_community_linux_*.sh`
3. Launch Burp → choose **Temporary project** → **Use Burp defaults** → **Start Burp**.

> Community Edition cannot *save* projects to disk; a "Temporary project" is the
> only option and is fine for this exercise. Export findings/evidence manually.

### Option B — Already bundled
Burp ships pre-installed in offensive-security Linux distributions such as Kali
and Parrot OS (`Applications → Web Application Analysis → burpsuite`).

### Requirement: Java
Burp bundles its own JRE in the installer builds, so a separate Java install is
usually **not** required. If you run the plain `.jar`, install a JDK (17+)
first and launch with `java -jar burpsuite_community.jar`.

## 3. First-run tour (the tabs we will use)

| Tab | Purpose in this project |
|-----|-------------------------|
| **Proxy → Intercept** | Pause requests/responses and edit them in-flight. |
| **Proxy → HTTP history** | Chronological log of every request Burp saw. Primary evidence source. |
| **Target → Site map** | Tree of discovered endpoints. |
| **Repeater** | Send one request repeatedly, tweaking it by hand. |
| **Intruder** | Automate a request with payload sets (brute force / fuzzing). |
| **Decoder** | Base64 / URL / hex encode & decode tokens. |

## 4. Verify the install

Open **Proxy → Proxy settings** (older builds: **Proxy → Options**) and confirm a
listener is running on **`127.0.0.1:8080`**. That is the address we will point
the browser / `curl` at in the next document.

A green/"running" listener on `127.0.0.1:8080` means Burp is installed and ready
for proxy configuration.

---

**Next:** [`02-proxy-configuration.md`](02-proxy-configuration.md) — point the
browser and `curl` at Burp, including the HTTPS CA certificate.
