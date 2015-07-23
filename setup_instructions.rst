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
        
       
Enable SPI on the Odroid W
##########################

    .. code:: bash 
     
        sudo raspi-config
        
Select "Advanced Options -> SPI Enable/Disable automatic loading"

   
Enable fb1 (if needed)
######################

    .. code:: bash 
    
        curl -SLs https://apt.adafruit.com/add | sudo bash
        sudo apt-get install -y adafruit-pitft-helper
        sudo nano /boot/config.txt
        
Add the following lines:
 
    .. code::
         
        [pi1]
        device_tree=bcm2708-rpi-b-plus.dtb
        [pi2]
        device_tree=bcm2709-rpi-2-b.dtb
        [all]
        dtparam=spi=on
        dtparam=i2c1=on
        dtparam=i2c_arm=on
        dtoverlay=pitft28c,rotate=90,speed=32000000,fps=20
        
        
    .. code:: bash 
    
        sudo reboot       




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

