#!/bin/bash
echo "🌡️ Checking Raspberry Pi 5 Thermal & Voltage Status..."
vcgencmd get_throttled
vcgencmd measure_temp
echo "💾 Checking Active Swap / ZRAM..."
swapon --show
