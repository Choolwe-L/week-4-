# Scripts

Supporting scripts for the Week 4 manual API testing exercise.

## `bruteforce_login.py`

Reproduces the Burp Intruder login brute force as a small, repeatable Python
script, so the finding has a text artifact in addition to Burp screenshots.

**Authorisation:** defaults to the local target (`http://127.0.0.1:5000`) and
**refuses non-loopback hosts** unless you pass `--i-have-authorisation`. Only
run password-guessing tools against systems you own or have written permission
to test.

### Usage

```bash
# from the scripts/ directory, with the API running
python bruteforce_login.py --email ben@fitnesshub.test

# custom wordlist and a small delay between attempts
python bruteforce_login.py --email alice@fitnesshub.test \
    --wordlist wordlists/common-passwords.txt --delay 0.1
```

Exit codes: `0` password found · `1` not found · `2` usage/authorisation error.

## `wordlists/common-passwords.txt`

A short demonstration list of common weak passwords. It includes
`password123` (Ben's password on the practice target) so the demo finds a match.
Real engagements use curated lists such as SecLists under proper authorisation.
