# Main Github Repo for Capstone Group NK01 at TMU

## How to set up Raspberry Pi with VNC

_Disclaimer:_ This is the method I used to run the Pi locally with my laptop there is a good chance that there are other methods will work as well.


### Basic Hardware Setup

You will need an ethernet cable to connect the Pi to your laptop, if your laptop does not have an ethernet port you can get a USB to ethernet adapter.

Plug in the Pi using the power supply, and also plug the Pi into your laptop/computer using the ethernet cable.

### VNC Viewer Setup

I used VNC Viewer (mostly since I already have it for connecting to the lab computers). But, I also heard RealVNC also works quite well.

At the top bar go to File>New Connection. Set the VNC Server to be "raspberrypi.local" and the name can be whatever you want.

VNC Viewer should prompt to enter a username and password, I can provide those to you just message me.

After this you should be at the Desktop for the Raspberry Pi.

## How to clone the repository onto your local computer

When in the "Code" section of the repository, copy the URL under the HTTPS tab. Then navigate to the folder where you want to clone the repository to in your terminal. The type this command into the terminal.

````
git clone <replace this with URL of Repository>
````


## How to pull from main branch of repository

Use this command in the cloned repository on your computer.

````
git pull origin main
````

### Troubleshooting

_If you are having trouble with using the ethernet connection:_

An issue I ran into whilst working with the Pi is related to using the ethernet port. A workaround I found is using the ethernet cable to connect to the Pi, then connecting the Pi to Wifi then connecting to the assigned IP address through VNC. Just replace the "raspberrypi.local" with the wlan0 IP address, which can be found with the command "ifconfig". Doing this seems to solve the connection issue.

_Issues with connecting to University Wifi_

Another issue worth mentioning is we are not able to access the school wifi using the Pi (outside the open house day) ideally we can install everything onto the pi outside of school and just work on the Pi without connecting to the internet. Another alternative is to use something like a restaurant's wifi or a hotspot on your phone, not ideal but it works.
