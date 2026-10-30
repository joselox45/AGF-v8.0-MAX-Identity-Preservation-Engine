# AGF v12.3.4 - CHAT KERNEL v0.8.8 (TRANSPARENT)

## 1. TRANSPARENT FAIL-CLOSED (API)
The local API (`api_server.py`) returns a `BLOCKED` JSON with the exact reason extracted from the scorer.
If the user asks why it was blocked, tell them to read the `reason` field in the JSON.
