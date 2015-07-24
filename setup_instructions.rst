*********************************
ODROID-W display smartmeter setup
*********************************

Download Raspbian
#################

Download latest version of Rasbian from:

https://www.raspberrypi.org/downloads/

The version we used was *2015-05-05-raspbian-wheezy.img*.


Burn image to SD card
#####################

Use at least a 4GB class 4 SD card.

.. code:: bash
 
    df -h
    dd if=filename.img of=/dev/<add device name> bs=4M
    sync
 
Start Odroid W.


Expand File System and enable SPI
#################################

.. code:: bash 
 
    sudo raspi-config

1. Select "Expand File System"
2. Select "Advanced Options -> SPI Enable/Disable automatic loading"
3. Finish and reboot


Connect to WIFI
###############

Edit *wpa_supplicant.conf*

.. code:: bash
    
    sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

add:

.. code:: bash
    
    network={
             ssid="SSID"
             psk="PASSWORD"
    }
    

Install python-dev and python-pip
#################################

.. code:: bash
 
    sudo apt-get update
    sudo apt-get install python-dev python-pip

    
Install py-spidev and WiringPi2
###############################

.. code:: bash
 
    sudo pip install spidev
    
    git clone https://github.com/Gadgetoid/WiringPi2-Python.git
    cd WiringPi2-Python
    sudo python setup.py install  


Install paramiko
################

.. code:: bash
    
    git clone https://github.com/paramiko/paramiko
    cd paramiko
    sudo python setup.py install  


Enable fb1 for 2.2inch TFT
##########################

For linux kernels >3.15, fbtft and many drivers are already included. Updating the kernel (new bootloader) is not required.

Enable tft driver 

.. code:: bash

    sudo nano /etc/modules

Add the following line:

.. code::

    fbtft_device name=adafruit22a verbose=0 rotate=90


Create key-based SSH login
##########################

Generating RSA Keys

.. code:: bash 
    
    mkdir ~/.ssh
    sudo chmod 700 ~/.ssh
    ssh-keygen -t rsa

Transfer Client Key to Host

.. code:: bash
    
    ssh-copy-id <username>@<host>


(Optional) Enable startup auto-login for Rasbian
################################################

.. code:: bash

    sudo nano /etc/inittab

Replace the following line:

.. code:: bash

    1:2345:respawn:/sbin/getty 115200 tty1

with this one:

.. code:: bash
    
    1:2345:respawn:/bin/login -f pi tty1 </dev/tty1 >/dev/tty1 2>&1


(Optional) Enable startx on startup
###################################

.. code:: bash

    sudo nano /etc/rc.local

add the following line:

.. code::

    su -l pi -c "env FRAMEBUFFER=/dev/fb1 startx &"

Disable the fb0 option in 99-fbturbo.conf

.. code:: bash

    sudo nano /usr/share/X11/xorg.conf.d/99-fbturbo.conf 

comment the following line:

.. code::

    #    Option        "fbdev" "/dev/fb0"

Console at boot: Add kernel argument to file /boot/cmdline.txt

.. code:: bash

    sudo nano /boot/cmdline.txt

add:

.. code::

    fbcon=map:10 

Reboot.
