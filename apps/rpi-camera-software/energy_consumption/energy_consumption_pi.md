# Reducing Energy Consumption of Raspberry Pi Device

Some projects do not have a constant unlimited energy supply. For example, the devices on edge, often powered by batteries have energy limited to the capacity of the battery. Myself I have a Raspberry Pi 4B which runs a software for the camera device for video recording. Naturally it is not very fun to have video being recorded at my desk, so I got a PiJuice Battery - a 1820 mAh/ 6.7Wh consumption. 

After playing with the device for a bit I noticed that the battery would hold no longer than 2-3 hours even when device is idle. With such a limited amount of time, it is not practical to use my camera for lots of situations. So motivated by this I have adventured into understanding the energy consumption and how to minimize those. 

In this note we will talk about how to measure and reduce energy consumption of the device, especially in the idle state, so that we can enjoy the energy for longer and are more efficient at using it. 

## Measuring Energy Consumption
 
The only way to improve is by measuring first, so lets begin by asking a question: "How much energy is my device consuming right now?". To calculate the consumption in Watt, we will use the well known Ohm's law:

  - Electrical power (P) in watts (W) is the product of:
     - Voltage (V) in volts (V)
     - Current (I) in amperes (A)

$$
P \text{ (W)} = V \text{ (V)} \times I \text{ (A)}
$$

### Measuring Energy with PiJuice APIs

PiJuice has a built-in battery monitoring system, so let's access it and measure power consumption. Let's write this in our Python script

```python
from pijuice import PiJuice

pijuice = PiJuice(1, 0x14)  # bus 1, address 0x14
voltage = self.pijuice.status.GetBatteryVoltage()["data"] / 1000  # mV → V
current = self.pijuice.status.GetBatteryCurrent()["data"] / 1000  # mA → A
power = voltage * current
print(f"Battery power: {power:.2f} W")
return power
```

For me this yielded `8.40W` which seems quite a bit for an idle device. Notice that if your device is charging then the value will be negative which is a consequence of how battery monitoring systems calculate the "net" of charge. 

### Reducing unnecessary battery consumption

So now we know how much energy we consume, let's try and reduce the consumption. So how do we reduce energy consumption on a general purpose electronics device such as raspberry pi? There are several quick wins: 

  - Disable unused outputs such as HDMI, Bluetooth
  - Lower CPU/GPU Clocks (safe underclock)

Let's write a bash script to do that:

```sh
echo "Enabling Raspberry Pi low-power mode..."

### 1. Disable HDMI output
/usr/bin/tvservice -o
echo " - HDMI disabled"
```

### Lowering CPU/GPU clocks

The main energy eaters on Raspberrypi are definitely the CPU/GPU. In my case, on raspberry pi 4b Quad-core Cortex-A72, 64-bit ARM, the CPU is run at frequency of 1.5 GHz by default. Naturally the higher the CPU clock frequency, the higher the energy consumption. We can check how much is the clock of each of the CPU like follows:

```sh
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
# 1800000 (1.8 GHz)
cat /sys/devices/system/cpu/cpu1/cpufreq/scaling_cur_freq
# 600000 (600 MHz)
cat /sys/devices/system/cpu/cpu2/cpufreq/scaling_cur_freq
# ...
cat /sys/devices/system/cpu/cpu3/cpufreq/scaling_cur_freq
# ...
```

The maximum frequency per CPU is defined at 

```sh
cat /sys/devices/system/cpu/<your_cpu_number>/cpufreq/scaling_max_freq
```

So one way to reduce the consumption is to set the clock at 900MHz for instance like follows

```sh
echo 900000 | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq
```

Also, you can see the available frequencies that you can apply to them: 


```sh
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies
# 600000 700000 800000 900000 1000000 1100000 1200000 1300000 1400000 1500000 1600000 1700000 1800000 
```

## Conclusion

I haven't managed to reduce much the consumption yet. More experiments to come.