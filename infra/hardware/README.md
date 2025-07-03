# Raspberry Pi Camera Hardware

This document outlines the hardware used for this project. 

## Hardware Details

Below follows the list of hardware

### Rapsberry Pi Zero 2WH
The actuall hardware device - raspberry pi 

- https://amzn.eu/d/ehOd6iF
- The actual computer where all software will run. You can buy it in many places, the link above is for reference
- Note the wifi module is mentioned by W letter. 2 refers to rows of GPIO pins. This is important due to the compatibility with the rest of the hardware (PiJuice). The H refers to soldered pins. I prefer to have them already soldered. Note if they are not soldered then you will have to solder them yourself in order to be able to set the PiJuice on top.

### Kingstone SD card - 128GB
Memory SD card to run Raspberry OS Lite

- https://amzn.eu/d/06cuIcV
- This card will be the RPI storage for OS

### Raspberry Pi Zero Case

- https://amzn.eu/d/1PXxTgX
- Simple Case Kit for physical protection of Rpi device

### Batery - PiJuice

The camera is wireless so requires a batery module to function

- Includes UPS system for energy interruption protection
- Is an Rpi HAT
- API access to read batery lifespan programmatically
- https://www.kiwi-electronics.com/en/pijuice-a-portable-power-platform-for-every-raspberry-pi-4234?country=&gad_source=1&gad_campaignid=1906220635&gbraid=0AAAAADuMvufczxpwrTLUWlH7w6j62ICrH&gclid=Cj0KCQjw5ubABhDIARIsAHMighai68woOO4F1skH01CKNOdk4agOCvdgKq9dwnsuoarAV0lcAeTdbx0aAumQEALw_wcB


### AI Camera 
- https://www.raspberrypi.com/documentation/accessories/ai-camera.html 
- Docs - https://www.raspberrypi.com/documentation/accessories/ai-camera.html
- MobileNet Model - https://huggingface.co/learn/computer-vision-course/en/unit2/cnns/mobilenet
- YoLo for object detection - https://huggingface.co/learn/computer-vision-course/en/unit2/cnns/yolo
- Good resources for object detection - https://huggingface.co/learn/computer-vision-course/en/unit6/basic-cv-tasks/object_detection
- Tesseract - for text reading
- OpenCV - camera input and basic image handling

### Waterproof Case
- https://www.electromaker.io/tutorial/blog/build-a-wildlife-camera-using-a-raspberry-pi-and-pijuice 
- TODO  

# Next Steps

Continue to the next step - [Operating system installation and SSH access](../os-setup/README.md)