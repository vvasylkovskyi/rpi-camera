echo "Enabling Raspberry Pi low-power mode..."

### 1. Disable HDMI output
xrandr --output HDMI-1 --off 2>/dev/null || true
echo " - HDMI disabled"

# # Activity LED
# if [ -f /sys/class/leds/led1/brightness ]; then
#     echo 0 | sudo tee /sys/class/leds/led1/brightness >/dev/null
#     echo " - Activity LED disabled"
# fi

# echo "Raspberry Pi Underclock Script"
# echo "----------------------------------"

# # Loop through CPUs and apply underclock
# for cpu in 0 1 2 3; do
#     CPU_PATH="/sys/devices/system/cpu/cpu$cpu/cpufreq/scaling_cur_freq"
#     MAX_PATH="/sys/devices/system/cpu/cpu$cpu/cpufreq/scaling_max_freq"

#     if [ -f "$CPU_PATH" ]; then
#         OLD_FREQ=$(cat $CPU_PATH)
#         echo 600000 | sudo tee $MAX_PATH >/dev/null
#         NEW_FREQ=$(cat $CPU_PATH)

#         echo "⚡ $TIMESTAMP | CPU$cpu: was ${OLD_FREQ} kHz → now ${NEW_FREQ} kHz"
#     else
#         echo "⚠️  CPU$cpu not found!"
#     fi
# done

# echo ""
# echo "All CPUs capped at 600 MHz"

echo "Disabling Bluetooth for power saving..."

# Bluetooth
sudo systemctl stop bluetooth
sudo systemctl disable bluetooth
echo "Bluetooth disabled."

echo "Disabling USB ports for power saving..."

echo '1-1' | sudo tee /sys/bus/usb/drivers/usb/unbind
echo "USB ports disabled."