# Contributing to openclaw-litert-rpi5

First off, thank you for considering contributing to `openclaw-litert-rpi5`! It’s people like you that make edge computing and open-source AI exciting.

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/<your-username>/openclaw-litert-rpi5.git
   cd openclaw-litert-rpi5
   ```

2. Create a virtual environment with Python 3.10+:
   ```bash
   python3 -m venv litert-env
   source litert-env/bin/activate
   pip install -r requirements.txt
   ```

3. Ensure code formatting is clean:
   ```bash
   # Optional lint check
   flake8 src/ || ruff check src/
   ```

## Pull Request Guidelines

1. **Create a topic branch:**
   ```bash
   git checkout -b feature/my-new-feature
   # or
   git checkout -b fix/issue-description
   ```
2. **Keep PRs focused:** Submit smaller, modular PRs rather than massive rewrites.
3. **Preserve compatibility:** Make sure the bridge remains compatible with the OpenAI specification for `/v1/chat/completions` and `/v1/embeddings`.
4. **Hardware validation:** If submitting optimizations for the Raspberry Pi 5 (thermal, memory, scheduling), include benchmark notes or outputs in your PR description.
5. **Commit Messages:** Follow standard conventional commit format (e.g. `fix: handle empty chunk response`, `feat: add model listing endpoint`).

## Reporting Bugs & Suggesting Features

Please use GitHub Issues with the appropriate issue template:
* Include your Raspberry Pi 5 OS version, RAM configuration (4GB / 8GB / 16GB), and storage setup (MicroSD or NVMe SSD).
* Provide full tracebacks or terminal logs where applicable.
