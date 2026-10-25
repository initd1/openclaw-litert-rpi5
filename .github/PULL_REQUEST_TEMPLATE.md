## Description
Briefly describe the changes introduced by this pull request.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Optimization (performance, thermal, or memory enhancement)
- [ ] Documentation update

## Hardware & Environment Tested
- **Device:** Raspberry Pi 5 (4GB / 8GB / 16GB)
- **OS:** Debian Bookworm 64-bit / Raspberry Pi OS
- **Storage:** NVMe SSD / MicroSD
- **Model:** Gemma 4 E2B `.litertlm`

## Testing Checklist
- [ ] Verified `python src/test_agent.py` executes without error
- [ ] Verified `./scripts/test_endpoints.sh` passes successfully
- [ ] Verified OpenClaw connects and completes agent tasks without schema errors
