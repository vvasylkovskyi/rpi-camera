# From Zero to SSH: Setting Up Raspberry Pi with OS Lite and Ansible Automation

Once your Raspberry Pi hardware order is complete, the next major step is configuring the SD card with the necessary software to bring your Pi to life. In this guide, you'll learn how to flash Raspberry Pi OS Lite to an SD card and configure a minimal backend setup using `Ansible` — a powerful tool for automating software provisioning and configuration.

Having configured many Raspberry Pi devices in the past, I can confidently say that doing it manually is time-consuming and repetitive. Ansible changes that by letting you define your setup in code and reapply it with ease. Let's dive in!

## Step 1: Installing Raspberry Pi OS Lite

* * Raspberry Pi OS Lite (64-bit): [Download here](https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2025-05-13/2025-05-13-raspios-bookworm-arm64-lite.img.xz). Make sure the OS version matches your hardware’s architecture (e.g., ARM64). Follow the steps below for [Flashing the OS Image](#flash-the-os-image).

### Flash the OS Image

1. Download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. Open Raspberry Pi Imager.
3. Choose the OS (Raspberry Pi OS Lite), select the SD card, and click the settings icon (⚙️) or press `CMD + Shift + X` to open advanced options.
4. Proceed to OS customization (see next section).

## Step 2: Customize the OS for Headless Access

Since OS Lite has no graphical interface, we need to enable SSH and configure credentials ahead of time.

### Enable SSH with Public Key Authentication

1. In the advanced settings menu:

   * ✅ Enable SSH
   * 🔘 Select "Only allow public-key authentication"

You are going to have to create a private/public ssh key pairs on your terminal: 

### Creating SSH Key pair

1. Generate an SSH key pair on your Mac:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Press Enter to accept the default file path (`~/.ssh/<your-key-name>`) and choose a passphrase if desired.

2. Copy the contents of your public key:

```bash
cat ~/.ssh/<your-key-name>.pub
```

Paste this into the SSH public key field in the Raspberry Pi Imager settings.

### Define Username and Network

Back in raspberrry pi imager: 

* Set a username (e.g., `pi`) and optionally leave the password blank.
* Configure wireless LAN settings (SSID, password, and country).
* Set a hostname for easy network discovery (e.g., `raspberrypi`).

Click **Save**, then **Write** to flash the SD card.

## Step 3: Boot the Raspberry Pi

Insert the SD card into your Raspberry Pi and power it on. The device should boot and connect to the network.

Since it's headless, you won't see anything visually—your next interaction will be via SSH.

## Step 4: Connect to the Pi via SSH

To test the setup:

1. Ensure your Mac is on the same network as the Raspberry Pi.
2. Add your private key to the SSH agent:

```bash
# First, enable the ssh agent
eval "$(ssh-agent -s)" 

# Then add the key that you created to the agent
ssh-add ~/.ssh/<your-private-key>

# Finally, connect via hostname or IP to your raspberrypi
ssh pi@raspberrypi.local
```

If you configured everything correctly, you'll be logged in without needing a password.

# Next Steps

Continue to the next step - [Infrastructure automation with Ansible](../ansible-configurations/README.md)