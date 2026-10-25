# 🦀 OpenClaw + Google LiteRT (Gemma-4-E2B) on Raspberry Pi 5

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![LiteRT](https://img.shields.io/badge/Google-LiteRT-4285F4.svg)](https://ai.google.dev/edge/litert)
[![Raspberry Pi 5](https://img.shields.io/badge/Raspberry%20Pi-5%20(ARM64)-C51A4A.svg)](https://www.raspberrypi.com/products/raspberry-pi-5/)

Run a fully local, autonomous **OpenClaw AI Agent** powered by **Google’s LiteRT** runtime and **Gemma 4 (E2B)** directly on a **Raspberry Pi 5 CPU**—accelerated with desktop-grade I/O via the **Pimoroni NVMe Base Duo PCIe HAT** and high-speed **M.2 NVMe SSDs**.

---

## ⚡ Why This Stack Matters

1. **Google LiteRT (XNNPACK CPU Acceleration):** Utilizes the Pi 5’s quad-core Arm Cortex-A76 processor via optimized vector pipelines, outperforming experimental Pi GPU drivers with minimal RAM overhead.
2. **Gemma 4 E2B (2-Billion Parameters):** Small enough to run smoothly on ARM CPU cores (sub-10W power draw), yet smart enough to pass strict zero-shot JSON tool-calling schemas required by autonomous agents.
3. **Pimoroni NVMe Base Duo (PCIe HAT + Dual M.2 SSDs):** By routing PCIe lanes through an FFC ribbon to a dedicated expansion board (HAT), this build eliminates traditional MicroSD I/O bottlenecks. Loading multi-gigabyte `.litertlm` flatbuffers and indexing agent workspaces happens with desktop-class NVMe read/write speeds.
4. **Custom FastAPI Bridge -> OpenClaw:** Strips internal `litert_lm` list-dictionary string wrappers on the fly and serves clean OpenAI-compatible Server-Sent Events (SSE) + local memory embeddings on port `4000`.

---

## 📂 Repository Structure

```text
openclaw-litert-rpi5/
├── LICENSE                         # MIT License
├── README.md                       # Project overview & setup guide
├── CHEATSHEET.md                   # Comprehensive CLI & operational cheatsheet
├── CONTRIBUTING.md                 # Contributor guide & standards
├── CODE_OF_CONDUCT.md              # Contributor Covenant CoC
├── SECURITY.md                     # Vulnerability reporting guidelines
├── pyproject.toml                  # Modern Python package specification
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── configs/
│   └── openclaw.snippet.json       # Validated Zod-compliant OpenClaw config
├── src/
│   ├── __init__.py                 # Package marker
│   ├── server.py                   # Production FastAPI OpenAI-compatible bridge
│   └── test_agent.py               # Standalone JSON tool-calling validator
├── scripts/
│   ├── test_endpoints.sh           # cURL test suite for Chat & Embeddings
│   └── check_pi_health.sh          # Pi 5 thermal, voltage & ZRAM diagnostic
└── docs/
    └── CLI_AND_TESTING_GUIDE.md    # Complete CLI commands & troubleshooting
```

---

## 🛠️ Hardware Bill of Materials (BOM)

To replicate this physical edge build with desktop-grade PCIe NVMe storage:

| Component | Specification | Official Reference |
| :--- | :--- | :--- |
| **Single-Board Computer** | Raspberry Pi 5 (8GB recommended) | [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) |
| **PCIe Storage HAT** | Pimoroni NVMe Base Duo | [Pimoroni Shop](https://shop.pimoroni.com/products/nvme-base-duo) |
| **High-Speed Storage** | 2x 1TB M.2 NVMe SSDs (M-Key 2280/2242) | PCIe Gen 2/3 (e.g., Crucial P3 Plus / Samsung 980) |
| **Cooling** | Raspberry Pi Active Cooler | [Active Cooler](https://www.raspberrypi.com/products/active-cooler/) |
| **Power Supply** | Official 27W USB-C PD (5.1V / 5A) | [27W USB-C PSU](https://www.raspberrypi.com/products/27w-power-supply/) |

---

## 🚀 Quick Start

### 1. Prerequisites & Virtual Environment

Ensure you are running 64-bit Raspberry Pi OS (Debian Bookworm) on a Raspberry Pi 5.

```bash
# Clone the repository
git clone https://github.com/your-username/openclaw-litert-rpi5.git
cd openclaw-litert-rpi5

# Create and activate a virtual environment
python3 -m venv litert-env
source litert-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download the Model

Gemma models are hosted on Hugging Face. You will need a free Hugging Face account to download the weights:

1. **Create an account & token:** Sign up at [huggingface.co](https://huggingface.co) and generate a free User Access Token under **Settings -> Access Tokens** (read permissions are sufficient).
2. **Authenticate the CLI:**
   ```bash
   huggingface-cli login
   # Paste your Hugging Face token when prompted
   ```

> ⚠️ **Important:** Download the generic `gemma-4-E2B-it.litertlm` build for the Pi 5 Broadcom CPU—**do not** use the Qualcomm NPU variant.

```bash
# Create directory for models
mkdir -p ~/litert-models/models

# Download via huggingface-cli
huggingface-cli download litert-community/gemma-4-E2B-it-litert-lm \
  gemma-4-E2B-it.litertlm \
  --local-dir ~/litert-models/models
```

*(Optional)* Configure custom model location:
```bash
cp .env.example .env
# Edit LITERT_MODEL_PATH if your model is located elsewhere
```

### 3. Verify Zero-Shot JSON Tool-Calling

Before launching the server, verify that the model correctly outputs clean, raw JSON for agentic tool use without conversational filler:

```bash
python src/test_agent.py
```

### 4. Start the OpenAI Bridge Server

```bash
python src/server.py
```

In a second terminal, verify the streaming chat completions and embeddings endpoints:

```bash
./scripts/test_endpoints.sh
```

### 5. Connect to OpenClaw

Merge the contents of [`configs/openclaw.snippet.json`](file:///configs/openclaw.snippet.json) into your OpenClaw configuration file (typically `~/.openclaw/openclaw.json` or `~/.config/openclaw/openclaw.json`):

```json
{
  "memory": {
    "search": {
      "provider": "openai",
      "remote": {
        "baseUrl": "http://127.0.0.1:4000/v1",
        "apiKey": "not-needed-for-local"
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "litert-local": {
        "baseUrl": "http://127.0.0.1:4000/v1",
        "apiKey": "not-needed-for-local",
        "api": "openai-completions",
        "models": [
          {
            "id": "gemma-4-E2B-it",
            "name": "Gemma 4 E2B Local",
            "contextWindow": 16384
          }
        ]
      }
    }
  },
  "plugins": {
    "entries": {
      "llm-task": {
        "enabled": true,
        "config": {
          "defaultProvider": "litert-local",
          "defaultModel": "gemma-4-E2B-it"
        }
      }
    }
  }
}
```

Restart the OpenClaw gateway to apply the configuration:
```bash
openclaw gateway restart
```

---

## 🛠️ Diagnostics & Maintenance

Check hardware temperatures, CPU clock frequencies, and ZRAM status using the included diagnostic script:

```bash
./scripts/check_pi_health.sh
```

For detailed troubleshooting, CLI commands, and benchmark tips, refer to [`docs/CLI_AND_TESTING_GUIDE.md`](file:///docs/CLI_AND_TESTING_GUIDE.md) and [`CHEATSHEET.md`](file:///CHEATSHEET.md).

---

## 🤝 Contributing

Contributions, bug reports, and hardware benchmark results are warmly welcome! Please review [CONTRIBUTING.md](file:///CONTRIBUTING.md) before opening a pull request.

## 📄 License

This project is licensed under the [MIT License](file:///LICENSE).
