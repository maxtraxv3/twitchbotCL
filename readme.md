# WARNING USING THIS IN MALICE OR IN AWAY NOT INTENDED WILL GET YOUR ACCOUNT BANNED IN CLANLORD.


- The CL Listener  
- The Twitch Bot  
- How they communicate  
- Installation  
- Setup  
- Testing  
- Troubleshooting  
- Systemd  
- Security  
- Architecture diagrams  
- Everything a user needs to get the whole system running  

---

# **CL Automation System**
A complete Twitch → Local → Clan Lord automation pipeline for Linux.  
This project contains two components:

1. **CL Listener** — a local HTTP service that injects commands into Clan Lord using `xdotool`.  
2. **Twitch Bot** — a chat bot that listens to Twitch chat and forwards allowed commands to the listener.

Together, they allow Twitch viewers to interact with your Clan Lord character in real time using chat commands.

---

## **Table of Contents**
- [Overview](#overview)  
- [Architecture](#architecture)  
- [Features](#features)  
- [Requirements](#requirements)  
- [Installation](#installation)  
- [Component 1: CL Listener](#component-1-cl-listener)  
- [Component 2: Twitch Bot](#component-2-twitch-bot)  
- [Running the System](#running-the-system)  
- [Testing](#testing)  
- [Allowed Commands](#allowed-commands)  
- [Cooldown System](#cooldown-system)  
- [Running as a Systemd Service](#running-as-a-systemd-service)  
- [Troubleshooting](#troubleshooting)  
- [Security Notes](#security-notes)  
- [License](#license)

---

# **Overview**
This project enables Twitch chat to control your Clan Lord character through a safe, rate‑limited, whitelisted command system.

It is designed for:

- Streamers  
- Clan Lord automation  
- Interactive Twitch content  
- Custom bot integrations  

The system is modular — you can use the listener alone, the bot alone, or both together.

---

# **Architecture**

```
Twitch Chat
   ↓
Twitch Bot (Python)
   ↓  POST http://localhost:5005/cl
CL Listener (Flask)
   ↓  xdotool
Clan Lord Client
```

OBS is **not** part of this chain.  
The listener runs independently in the background.

---

# **Features**
### **CL Listener**
- Local HTTP endpoint  
- Safe xdotool injection  
- Global cooldown  
- Per‑user cooldown  
- Per‑command cooldown  
- Command whitelist  
- Logging  
- JSON validation  
- Window validation  

### **Twitch Bot**
- Connects to Twitch IRC  
- Parses chat messages  
- Sends allowed commands to listener  
- Handles reconnects  
- Supports cooldowns  
- Easy to extend  

---

# **Requirements**
- Linux  
- Python 3.8+  
- `xdotool`  
- Clan Lord running in a visible window  
- Twitch account + OAuth token  
- A terminal  

Install dependencies:

```
sudo pacman -S xdotool
pip install flask websockets requests
```

---

# **Installation**
Clone the repository:

```
git clone https://github.com/<yourname>/cl-automation.git
cd cl-automation
```

(Optional) Create a virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

---

# **Component 1: CL Listener**
The listener receives HTTP POST requests and injects commands into Clan Lord.

### **Start the listener**
```
python3 cl_listener.py
```

You should see:

```
CL Listener running on http://localhost:5005
```

### **Listener API**
Endpoint:

```
POST /cl
```

Payload:

```json
{
  "user": "viewer123",
  "text": "!heal bob"
}
```

Response examples:

```
{"status": "ok", "sent": "/heal bob"}
{"status": "blocked"}
{"status": "user_cooldown"}
{"status": "command_cooldown"}
{"status": "global_cooldown"}
{"status": "cl_not_found"}
```

---

# **Component 2: Twitch Bot**
The bot connects to Twitch chat and forwards commands to the listener.

### **Configure the bot**
Edit:

```
TWITCH_OAUTH = "oauth:xxxxxxxxxxxx"
TWITCH_NICK = "your_bot_username"
TWITCH_CHANNEL = "your_channel"
```

### **Run the bot**
```
python3 twitch_bot.py
```

You should see:

```
Connected to Twitch IRC
```

---

# **Running the System**
Start the listener:

```
python3 cl_listener.py
```

Start the bot:

```
python3 twitch_bot.py
```

Open Clan Lord.

Your viewers can now type:

```
!heal bob
!balance
!wave
```

And your character will perform the actions.

---

# **Testing**
### **Test the listener directly**
```
curl -X POST http://localhost:5005/cl \
     -H "Content-Type: application/json" \
     -d '{"user":"tester","text":"!balance"}'
```

### **Test the bot**
Type in your Twitch chat:

```
!heal bob
```

---

# **Allowed Commands**
Defined in `ALLOWED = { ... }`:

| Command | Output |
|--------|--------|
| `!heal bob` | `/heal bob` |
| `!boost bob` | `/boost bob` |
| `!share bob` | `/share bob` |
| `!balance` | `/balance` |
| `!wave` | `/wave` |
| `!walk north` | `/move north walk` |

You can add more easily.

---

# **Cooldown System**
The listener enforces:

### **Global Cooldown**
Prevents command storms.

### **Per‑User Cooldown**
Stops individual spam.

### **Per‑Command Cooldown**
Prevents repeated ability spam.

All values are configurable:

```
GLOBAL_COOLDOWN = 1.2
USER_COOLDOWN = 3.0
COMMAND_COOLDOWN = 2.0
```

---

# **Running as a Systemd Service**
Create:

```
/etc/systemd/system/cl-listener.service
```

Contents:

```
[Unit]
Description=Clan Lord Listener
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/cl_listener.py
WorkingDirectory=/path/to/
Restart=always
User=yourusername

[Install]
WantedBy=multi-user.target
```

Enable + start:

```
sudo systemctl enable cl-listener
sudo systemctl start cl-listener
```

---

# **Troubleshooting**

### **Clan Lord window not found**
Check:

```
xdotool search --name "Clan Lord"
```

If it returns nothing, update:

```
CL_WINDOW = "Clan Lord"
```

### **Commands not triggering**
Cooldowns may be blocking them.

### **Bot says “blocked”**
Command not in whitelist.

### **Nothing happens in CL**
Clan Lord must not be minimized — xdotool cannot type into minimized windows.

### **Bot not connecting**
Check your Twitch OAuth token.

---

# **Security Notes**
- Listener only accepts **local** connections  
- Cannot be accessed remotely  
- Only executes whitelisted commands  
- Cannot run arbitrary shell commands  
- Safe to run while streaming  
