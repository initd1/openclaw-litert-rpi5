
🛠️ CLI Commands & Troubleshooting Guide


1. Direct LiteRT CLI Commands (No Server)

Test the downloaded .litertlm model directly from bash before running the API server:
```bash

Single prompt execution

litert-lm run ~/litert-models/models/gemma-4-E2B-it.litertlm \
  --prompt "Explain edge computing in two sentences."

# Interactive terminal chat session
litert-lm run ~/litert-models/models/gemma-4-E2B-it.litertlm
```

## 2. Raspberry Pi 5 Hardware Tuning

### Enable ZRAM Swap
```bash
sudo apt update && sudo apt install -y zram-tools
# Alternatively configure zram-swap or restart
sudo systemctl restart zramswap || sudo reboot
``` 

### Live Thermal & Clock Monitoring
```bash
watch -n 1 "vcgencmd measure_temp && vcgencmd measure_clock arm"
``` 

3. Common Errors Solved in This Repo

• RuntimeError: Failed to create LiteRT-LM engine ... Qualcomm_QCS8275.litertlm: Fixed by using the vendor-neutral CPU model instead of the Snapdragon NPU build.
• list indices must be integers or slices, not str: Solved in src/server.py by adding polymorphic chunk inspection and regex extraction for stringified Python list wrappers ([{'type': 'text', 'text': '...'}]).
• Unrecognized key: "providers" / must not have additional properties: "contextWindow": Solved in configs/openclaw.snippet.json by nesting providers under models.providers, declaring the models array explicitly, and keeping contextWindow strictly inside the model item definition.
• Unknown memory embedding provider: Solved by setting memory.search.provider to "openai" and serving a local /v1/embeddings endpoint in src/server.py.
