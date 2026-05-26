from flask import Flask, request, jsonify
import subprocess
import time
import logging

app = Flask(__name__)

# ============================
# CONFIG
# ============================

CL_WINDOW = "Clan Lord"
GLOBAL_COOLDOWN = 1.2          # minimum delay between ANY commands
USER_COOLDOWN = 3.0            # per-user cooldown
COMMAND_COOLDOWN = 2.0         # per-command cooldown

last_global = 0
user_last = {}
command_last = {}

# !wave in chat = "wave": "/wave", note the last "command" must NOT have a "," at the end
# yes this can trigger macros.
ALLOWED = {
    "heal": "/heal {target}",
    "boost": "/boost {target}",
    "share": "/share {target}",
    "balance": "/balance",
    "wave": "/wave",
    "walk": "/move {target} walk"
}

# ============================
# LOGGING
# ============================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)

# ============================
# XDOTOOl INJECTION
# ============================

def send_to_cl(text):
    """Inject text into Clan Lord safely."""
    logging.info(f"Injecting into CL: {text}")

    # Ensure window exists
    try:
        win = subprocess.check_output(
            ["xdotool", "search", "--name", CL_WINDOW]
        ).decode().strip()
    except subprocess.CalledProcessError:
        logging.error("Clan Lord window not found.")
        return False

    # Activate window
    subprocess.run(["xdotool", "windowactivate", "--sync", win])

    # Type text
    subprocess.run(["xdotool", "type", "--delay", "20", text])

    # Press Enter
    subprocess.run(["xdotool", "key", "Return"])

    return True

# ============================
# ROUTE
# ============================

@app.post("/cl")
def cl():
    global last_global

    # Validate JSON
    if not request.is_json:
        return jsonify({"error": "invalid_json"}), 400

    data = request.json
    text = data.get("text", "").strip()
    user = data.get("user", "unknown")

    if not text.startswith("!"):
        return jsonify({"status": "ignored"})

    parts = text[1:].split()
    cmd = parts[0].lower()
    args = parts[1:]

    # Check whitelist
    if cmd not in ALLOWED:
        return jsonify({"status": "blocked"})

    now = time.time()

    # Global cooldown
    if now - last_global < GLOBAL_COOLDOWN:
        return jsonify({"status": "global_cooldown"})

    # Per-user cooldown
    if now - user_last.get(user, 0) < USER_COOLDOWN:
        return jsonify({"status": "user_cooldown"})

    # Per-command cooldown
    if now - command_last.get(cmd, 0) < COMMAND_COOLDOWN:
        return jsonify({"status": "command_cooldown"})

    # Build command
    template = ALLOWED[cmd]
    target = args[0] if args else ""
    cl_cmd = template.format(target=target)

    # Inject into CL
    ok = send_to_cl(cl_cmd)
    if not ok:
        return jsonify({"status": "cl_not_found"})

    # Update cooldowns
    last_global = now
    user_last[user] = now
    command_last[cmd] = now

    logging.info(f"Sent: {cl_cmd}")
    return jsonify({"status": "ok", "sent": cl_cmd})

# ============================
# MAIN
# ============================

if __name__ == "__main__":
    logging.info("CL Listener running on http://localhost:5005")
    app.run(host="127.0.0.1", port=5005)
