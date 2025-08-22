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

### Measuring remaining battery time

With a little bit of math we can also estimate how much time we have left until the battery is dead. This is going to be a rough estimate since the consumption values fluctuate. Nevertheless a good information to have with a little bit of python code: 

```python
battery_voltage_nominal = 3.7  # V
battery_capacity_mAh = 1820  # mAh

voltage = self.pijuice.status.GetBatteryVoltage()["data"] / 1000  # mV → V
current = self.pijuice.status.GetBatteryCurrent()["data"] / 1000  # mA → A
charge_pct = self.pijuice.status.GetChargeLevel()["data"]  # 0–100%

# Energy remaining in Wh
energy_wh = (
    battery_capacity_mAh / 1000 * battery_voltage_nominal * (charge_pct / 100)
)

power_w = voltage * current

if power_w > 0:
    time_remaining_h = energy_wh / power_w
    time_remaining_min = time_remaining_h * 60
else:
    time_remaining_min = float("inf")  # charging or zero draw

print(f"Estimated battery life remaining: {time_remaining_min:.1f} minutes") # 120 minutes
```

In the code above the `battery_voltage_nominal` and `battery_capacity_mAh` are the hardcoded values that can be found on the battery details. It varies from manufacturer to manufacturer. The ideia of the script is to use the full battery capacity, get the remaining one by multiplying by `charge_pct` and obtain the Watts hours. Once we have Watt hours it is only a matter of dividing them per amount of power consumed per second which is `power_w`.

### Reducing unnecessary battery consumption

So now we know how much energy we consume, let's try and reduce the consumption. So how do we reduce energy consumption on a general purpose electronics device such as raspberry pi? Surpisingly from my research there is not that much that one can do programmatically, but rather architecturally. I have attempted to reduce CPU/GPU clocks and disable unnecessary IOs such as HDMI, Bluetooth and USB ports, however didn't alot of meaningful reduction. Nevertheless I will talk about how you can do that bellow.

Another more effective approach is to put your main device to sleep most of the time, and use micro-controllers to wake-up the main device on event. This is where your energy savings may shine. The main idea is to your main Raspberry Pi device to sleep most of the time, thus saving considerable amounts of energy. This raises challenge of waking up the device, questions such as: How to wake up my main device to do meaningful work, and then put it back to sleep? There are mainly two approaches: 



#### Using real time clock (RTC) on Battery Systems

Many battery systems such as PiJuice include the real time clock which allows to wake up device at the specified time. While useful, it is still limited since this doesn't allow for an event-based wake-up that is useful for features like user requested control, or motion based wake up. For those, we have to use micro-controllers.

I haven't implemented that behavior myself - feature work for me. However, if you are curious, you can try it out from [PiJuice documentation of I2C commands](https://github.com/PiSupply/PiJuice/tree/master/Software#i2c-command-api). 

#### Using micro-controllers to send events to the Battery System

Micro controllers shine at this tiny work such as waking up the main Rpi because they can be attached to the same battery and be awake for longer times, since they consume considerably less energy. By keeping the setup like that, you can live the main device for days without recharding. The idea is to attach micro-controller physically to the main device and the battery system, and send signals to the battery system, which then will awake main device. The device does work, and then goes back to sleep. With this setup you can achieve cool results such as:  

  - Motion-based wake-up
  - Network event based wake-up. For instance, when a user requests Live view via apps.

Here I also haven't done much of experimentation. Example of some resources converting such approach: 

  - [Todd's Technical Treasures - wake up rpi from halt](https://tstellanova.github.io/docs/rpi-wake-from-halt-energy.html)
  - [ESP32 External Wake Up from Deep Sleep](https://randomnerdtutorials.com/esp32-external-wake-up-deep-sleep/)
  - [Raspberry Pi + Battery UPS HAT with Python Integration](https://docs.sixfab.com/docs/sixfab-power-getting-started)



### Reducing Main Device Power

Bellow we will describe how  to reduce CPU/GPU clocks and disable unnecessary IOs such as HDMI, Bluetooth and USB ports, however didn't alot of meaningful reduction. Nevertheless I will talk about how you can do that bellow. Let's begin by writing a bash script to do that:

```sh
echo "Enabling Raspberry Pi low-power mode..."

### 1. Disable HDMI output
/usr/bin/tvservice -o
echo " - HDMI disabled"

echo "Disabling Bluetooth for power saving..."

# Bluetooth
sudo systemctl stop bluetooth
sudo systemctl disable bluetooth
echo "Bluetooth disabled."

echo "Disabling USB ports for power saving..."

echo '1-1' | sudo tee /sys/bus/usb/drivers/usb/unbind
echo "USB ports disabled."
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

Managing energy consumption on a Raspberry Pi—especially when running on a limited battery supply—requires both measurement and thoughtful optimization. As we saw, simply disabling unused peripherals or lowering CPU clocks may provide small gains, but the real savings often come from rethinking the system’s architecture: keeping the Pi asleep for most of the time and relying on low-power microcontrollers or RTC triggers for event-based wakeups. By combining careful monitoring with selective hardware and software strategies, it becomes possible to stretch limited battery life from just a couple of hours into something far more practical. Ultimately, the key insight is that efficiency comes not only from reducing power draw at the component level, but also from designing the workload and system behavior around energy awareness.