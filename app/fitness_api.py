"""
Fitness API -- Week 4 target application.

A deliberately simple Flask API that exposes the kinds of endpoints a fitness
tracking product would have (authentication, user profile, workout logging).

This app exists ONLY as a local practice target for the Week 4 manual API
testing exercise. It is meant to be run on localhost and proxied through Burp
Suite so requests and responses can be intercepted, inspected, and fuzzed.

Intentional weaknesses (to be found with Burp and fixed in later weeks):
  * No rate limiting on /api/login   -> allows brute force via Burp Intruder
  * Verbose auth errors ("user not found" vs "wrong password") -> user enumeration
  * Tokens are predictable / not cryptographically bound to the user
  * Profile endpoint trusts the `user_id` in the URL (IDOR / BOLA)

Run:
    pip install -r requirements.txt
    python fitness_api.py
The API listens on http://127.0.0.1:5000
"""

from __future__ import annotations

import base64
import secrets
import time
from functools import wraps

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# In-memory "database". Passwords are stored in plaintext ON PURPOSE so the
# exercise has something obviously wrong to report. Do not copy this pattern
# into a real service.
# ---------------------------------------------------------------------------
USERS = {
    "alice@fitnesshub.test": {
        "user_id": 1001,
        "password": "Sunshine2023",
        "full_name": "Alice Mwansa",
        "plan": "premium",
        "weight_kg": 64.5,
        "goal": "Run a half marathon",
    },
    "ben@fitnesshub.test": {
        "user_id": 1002,
        "password": "password123",
        "full_name": "Ben Phiri",
        "plan": "free",
        "weight_kg": 81.2,
        "goal": "Lose 5kg",
    },
    "coach@fitnesshub.test": {
        "user_id": 1003,
        "password": "Admin!2024",
        "full_name": "Coach Tembo",
        "plan": "staff",
        "weight_kg": 77.0,
        "goal": "Help clients hit their targets",
    },
}

# Map issued tokens -> email so we can look a session back up.
ACTIVE_TOKENS: dict[str, str] = {}

# Simple request log so you can correlate what you see in Burp with the server.
REQUEST_LOG: list[dict] = []


@app.before_request
def _log_request() -> None:
    REQUEST_LOG.append(
        {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "method": request.method,
            "path": request.path,
            "remote": request.remote_addr,
        }
    )


def _issue_token(email: str) -> str:
    """Issue a weak, URL-safe token (intentionally not bound to the user)."""
    token = base64.urlsafe_b64encode(secrets.token_bytes(12)).decode().rstrip("=")
    ACTIVE_TOKENS[token] = email
    return token


def require_token(view):
    """Decorator that checks for a Bearer token in the Authorization header."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "missing or malformed Authorization header"}), 401
        token = auth.split(" ", 1)[1].strip()
        if token not in ACTIVE_TOKENS:
            return jsonify({"error": "invalid or expired token"}), 401
        request.auth_email = ACTIVE_TOKENS[token]  # type: ignore[attr-defined]
        return view(*args, **kwargs)

    return wrapper


@app.get("/")
def index():
    return jsonify(
        {
            "service": "Fitness API",
            "version": "0.1.0-insecure",
            "note": "Local practice target for Week 4 manual API testing.",
            "endpoints": [
                "POST /api/login",
                "GET  /api/users/<user_id>/profile  (requires Bearer token)",
                "GET  /api/workouts                 (requires Bearer token)",
                "GET  /api/_debug/requests          (shows recent request log)",
            ],
        }
    )


@app.post("/api/login")
def login():
    """
    Authenticate a user.

    WEAKNESSES (by design):
      - distinct errors for unknown user vs. wrong password (enumeration)
      - no rate limiting / lockout (brute forceable with Burp Intruder)
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = USERS.get(email)
    if user is None:
        # Verbose: tells an attacker the account does not exist.
        return jsonify({"error": "no account found for that email"}), 404

    if password != user["password"]:
        # Verbose: confirms the account exists but the password was wrong.
        return jsonify({"error": "incorrect password"}), 401

    token = _issue_token(email)
    return jsonify(
        {
            "message": "login successful",
            "token": token,
            "token_type": "Bearer",
            "user_id": user["user_id"],
        }
    )


@app.get("/api/users/<int:user_id>/profile")
@require_token
def profile(user_id: int):
    """
    Return a user's profile.

    WEAKNESS (by design): BOLA / IDOR. The handler returns whatever user_id is
    asked for and never checks it against the authenticated user's own id.
    """
    for email, user in USERS.items():
        if user["user_id"] == user_id:
            return jsonify(
                {
                    "user_id": user["user_id"],
                    "email": email,
                    "full_name": user["full_name"],
                    "plan": user["plan"],
                    "weight_kg": user["weight_kg"],
                    "goal": user["goal"],
                }
            )
    return jsonify({"error": "user not found"}), 404


@app.get("/api/workouts")
@require_token
def workouts():
    """Return a static workout list for the authenticated user."""
    return jsonify(
        {
            "owner": request.auth_email,  # type: ignore[attr-defined]
            "workouts": [
                {"id": 1, "type": "run", "distance_km": 5.2, "duration_min": 28},
                {"id": 2, "type": "strength", "sets": 15, "duration_min": 45},
                {"id": 3, "type": "cycling", "distance_km": 18.0, "duration_min": 55},
            ],
        }
    )


@app.get("/api/_debug/requests")
def debug_requests():
    """Expose the recent request log so you can line it up with Burp's history."""
    return jsonify({"count": len(REQUEST_LOG), "recent": REQUEST_LOG[-25:]})


if __name__ == "__main__":
    # threaded=True so Burp Intruder's parallel requests are handled smoothly.
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
