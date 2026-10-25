# ⚡ Terminal & CLI Cheatsheet: LiteRT + Gemma 4 + OpenClaw on Raspberry Pi 5

A quick-reference cheatsheet for every terminal command used to download, test, benchmark, serve, and debug **Gemma 4 (E2B)** via **Google LiteRT** and **OpenClaw** on the Raspberry Pi 5.

---

## 1. Environment & Model Download Commands

### Activate the Python Virtual Environment
Always run this before executing `litert-lm` or `server.py`:
```bash
source ~/litert-env/bin/activate
```

### Download the CPU/XNNPACK Model (Hugging Face CLI)
*(Note: Requires a free account on [huggingface.co](https://huggingface.co). Run `huggingface-cli login` first. Always grab the generic `.litertlm` build for the Pi 5 Broadcom CPU—never the `_Qualcomm_` NPU variant).*
```bash
# Optional: Authenticate if not already logged in
huggingface-cli login

# Using huggingface-cli
huggingface-cli download litert-community/gemma-4-E2B-it-litert-lm \
  gemma-4-E2B-it.litertlm \
  --local-dir ~/litert-models/models

# Or using the modern standalone hf CLI
hf download litert-community/gemma-4-E2B-it-litert-lm \
  gemma-4-E2B-it.litertlm \
  --local-dir ~/litert-models/models
```

---

## 2. Direct LiteRT Interactive & Single-Prompt CLI Tests

Use these commands to test the `.litertlm` model directly in bash (bypassing FastAPI and OpenClaw) to verify **XNNPACK CPU acceleration**.

### Launch an Interactive Terminal Chat Session
```bash
litert-lm run ~/litert-models/models/gemma-4-E2B-it.litertlm
```
*(Type your questions interactively at the `>>>` prompt. Type `exit` or `quit` or press `Ctrl+C` to leave).*

### Run a Quick One-Shot Prompt Test
```bash
litert-lm run ~/litert-models/models/gemma-4-E2B-it.litertlm \
  --prompt "Explain why edge computing on a Raspberry Pi 5 is useful in two sentences."
```

### Run the Standalone Python Interactive Loop
```bash
python3 -c '
import litert_lm
import os
MODEL_PATH = os.path.expanduser("~/litert-models/models/gemma-4-E2B-it.litertlm")
with litert_lm.Engine(MODEL_PATH) as engine:
    with engine.create_conversation() as conv:
        while True:
            msg = input("\n>>> ")
            if msg.lower() in ["exit", "quit"]: break
            for chunk in conv.send_message_async(msg):
                print(chunk, end="", flush=True)
            print()
'
```

---

## 3. Agentic JSON Schema & FastAPI Server Commands

### Test Zero-Shot JSON Tool-Calling (`test_agent.py`)
Verifies that Gemma 4 E2B outputs raw JSON (`{"tool": "execute_bash_command", ...}`) without conversational fluff:
```bash
python src/test_agent.py
```

### Start the OpenAI-Compatible Bridge Server (`server.py`)
```bash
# Run in foreground (shows live Uvicorn & LiteRT logs)
python src/server.py

# Run in foreground with noisy C++ LiteRT initialization logs muted
python src/server.py 2>/dev/null

# Run persistently in the background (survives terminal close)
nohup python src/server.py > ~/litert-server.log 2>&1 &
```

### Check if Port 4000 is Actively Listening
```bash
ss -tulpn | grep 4000
```

---

## 4. cURL API Verification Commands

Run these from a **second terminal window** while `server.py` is running on port `4000`.

### Test 1: Streaming Chat Completions (`stream: true`)
Simulates OpenClaw's live interactive chat:
```bash
curl -X POST http://127.0.0.1:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "stream": true
  }'
```

### Test 2: Non-Streaming Chat Completions (`stream: false`)
Simulates OpenClaw's background session compaction and summarization requests:
```bash
curl -X POST http://127.0.0.1:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Reply with only the word Pong."}
    ],
    "stream": false
  }'
```

### Test 3: Memory Sync Embeddings (`/v1/embeddings`)
Verifies the local vector endpoint used by OpenClaw's memory watcher:
```bash
curl -X POST http://127.0.0.1:4000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Test string for OpenClaw memory sync vector generation."
  }'
```

---

## 5. OpenClaw Gateway & Session Commands

### Inside the OpenClaw Interactive TUI / Chat
```text
/new        # Clear token history and start a fresh 0-token session (Fixes context overflow!)
/compact    # Manually trigger conversation history summarization
/model      # Check or switch active model (litert-local/gemma-4-E2B-it)
```

### Verify `openclaw.json` Provider URL & Restart Gateway
```bash
# Verify baseUrl explicitly includes :4000/v1
grep -n -C 5 "litert-local" ~/.openclaw/openclaw.json ~/.config/openclaw/openclaw.json 2>/dev/null

# Restart the OpenClaw gateway to flush cached provider URLs
openclaw gateway restart
```

---

## 6. Raspberry Pi 5 Hardware, Thermal & ZRAM Commands

### Check Power & Thermal Throttling Status
```bash
# 0x0 = Healthy (No under-voltage, no thermal throttling)
vcgencmd get_throttled
```

### Live Monitor CPU Temp & ARM Clock Frequency (Updates Every 1s)
```bash
watch -n 1 "vcgencmd measure_temp && vcgencmd measure_clock arm"
```

### Setup & Verify ZRAM Compressed Swap
```bash
# Install ZRAM swap script
curl -L https://githubusercontent.com | bash
sudo reboot

# Verify /dev/zram0 is active after reboot
swapon --show
free -h
```

### Check NVMe SSD Disk Speed & Mount Status
```bash
lsblk
df -h ~
```
