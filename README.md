# PiControl
###### Raspberry Pi Control Center

***
## Installation
1. Download the code
    * git clone https://github.com/bcarroll/PiControl.git
    * [Download the repository as a zip file](https://github.com/bcarroll/PiControl/archive/master.zip)
2. Install Operating System dependencies (mostly for SSL support)
    *    ``sudo apt-get update``
    *    ``sudo apt-get install gcc libffi-dev libssl-dev python-dev python-cryptography wiringpi``
3. Install Python dependencies
    *    ``cd /directory/where/you/cloned-or_unzipped``
    *    ``sudo pip install Flask Flask-SSLify flask_sqlalchemy ipaddress netifaces netaddr psutil simplepam wiringpi requests xmltodict``
4. Set executable flag on the PiControl start script
    *    chmod +x /directory/where/you/cloned-or_unzipped/PiControl.sh

    The above command changes the mode of the PiControl.sh script so it can be executed from a shell.

5.    *Optional* - Start PiControl when your Raspberry Pi boots
    *    ``echo "Start PiControl"| sudo tee --append /etc/rc.local``
    *    ``echo "sudo -u pi python /directory/where/you/cloned-or_unzipped/PiControl.sh start &"| sudo tee --append /etc/rc.local``

    The above command adds a new line to /etc/rc.local which will start PiControl as the "pi" user when the Raspberry Pi boots.
    If you remove the "sudo -u pi" part, PiControl will run as "root" (not advised, for security reasons).
    You can also create a new account to run PiControl as with the [adduser](https://www.raspberrypi.org/documentation/linux/usage/users.md) command.

6.    Start PiControl
    *    ``/directory/where/you/cloned-or_unzipped/PiControl.sh start``

***

## Usage
Once you have PiControl installed and running, open a web browser *(either on the Pi itself or another machine (or smartphone) that can communication with the Pi)*

In the web browser, goto **https://ipaddress_of_your_pi:31415**

If you are using a web browser from a UNIX-ish machine (Linux, UNIX, MacOS) and you know the hostname of your Pi, you can access PiControl via **https://hostname.local:31415** (replace "hostname" in the URL with your Pi's actual hostname)

#### *Notice:*
**You will be presented with an SSL Security Error/Warning, because PiControl, by default, uses a self-signed SSL certificate, and your browser doesn't trust self signed certificates.  PiControl uses SSL to make sure the data that is transmitted is encrypted.  To get arounf the certificate error, the web browser will let you add an exception for the URL so the SSL error is not displayed the next time you visit the URL.**

If you do not want to use the included self-signed certificate, you can replace SSL/server.crt and SSL/server.key with a commercial SSL certificate. *- If this applies to you, you probably now how to make that happen.*

Once you get past the SSL warning screen, you will be presented with the PiControl login interface.  Login using your Raspberry Pi credential ("pi") and password.

![PiControl Login Screen](https://bcarroll.github.io/PiControl/Login_sm.png "Login with a valid OS user account: pi")

Login with a valid OS user account (pi)

![PiControl - Main](https://bcarroll.github.io/PiControl/Main_sm.png "PiControl Main screen")

The main screen displays the hostname of your Raspberry Pi in the upper left, a picture of the hardware on the upper right and the Raspberry Pi Model information and hardware details.

The menubar on the left side of the screen allows you to view/control various aspects of your  Raspberry Pi.

***

### System Menu
![PiControl - Processes](https://bcarroll.github.io/PiControl/Processes_sm.png "PiControl Processes screen")

The Processes section displays all running processes

![PiControl - Disk](https://bcarroll.github.io/PiControl/Disk_sm.png "PiControl Disk screen")

The Disk section displays disk usage

![PiControl - Localization](https://bcarroll.github.io/PiControl/Localization_sm.png "PiControl Localization screen")

The Localization section displays locale configuration (Keyboard layout, etc...)

![PiControl - Memory](https://bcarroll.github.io/PiControl/Memory_sm.png "PiControl Memory screen")

The Memory section displays memory (virtual and physical) usage and voltages

![PiControl - Network](https://bcarroll.github.io/PiControl/Network_sm.png "PiControl Network screen")

The Network section displays information about all the available Network Interfaces

![PiControl - Services](https://bcarroll.github.io/PiControl/Services_sm.png "PiControl Services screen")

The Services section displays information for all the configured services

![PiControl - Users](https://bcarroll.github.io/PiControl/Users_sm.png "PiControl Users screen")

The User section displays information about user accounts

![PiControl - Video](https://bcarroll.github.io/PiControl/Video_sm.png "PiControl Video screen")

The Video section displays information about the video configuration

### Hardware Menu
![PiControl - GPIO](https://bcarroll.github.io/PiControl/GPIO_sm.png "PiControl GPIO screen")

The GPIO section displays the current status of all the Raspberry Pi GPIO pins, and allows you to change the values (on/HIGH or off/LOW)
