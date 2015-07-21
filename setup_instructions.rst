*********************************
ODROID-W display smartmeter setup
*********************************

Download Raspbian
#################

Download latest version of Rasbian from:

<<<<<<< HEAD
`<https://www.raspberrypi.org/downloads/>`
=======
https://www.raspberrypi.org/downloads/
>>>>>>> 3ea73c78ae987e2d6972cfea5b204efdd73804eb

The version we used was *2015-05-05-raspbian-wheezy.img*.


Burn image to SD card
#####################

Use at least a 4GB class 4 SD card.

    .. code:: bash
 
        df -h
        dd if=filename.img of=/dev/mmcblk0]s bs=4M
        sync
        
Start Odroid W.
    
    
Connect to WIFI
###############

    .. code:: bash
<<<<<<< HEAD
        sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
        
add:
    
    ..code::
=======
    
        sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
        
add:
    .. code:: bash
>>>>>>> 3ea73c78ae987e2d6972cfea5b204efdd73804eb
    
        network={
                 ssid="SSID"
                 psk="PASSWORD"
        }
    

Install python-dev and python-pip
<<<<<<< HEAD
#################################sudo n
=======
#################################
>>>>>>> 3ea73c78ae987e2d6972cfea5b204efdd73804eb

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
<<<<<<< HEAD
=======


Install paramiko
################

    .. code:: bash
        
        git clone https://github.com/paramiko/paramiko
        cd paramiko
        sudo python setup.py install  
>>>>>>> 3ea73c78ae987e2d6972cfea5b204efdd73804eb
        
       
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
    
<<<<<<< HEAD
        sudo reboot       


=======
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
>>>>>>> 3ea73c78ae987e2d6972cfea5b204efdd73804eb
