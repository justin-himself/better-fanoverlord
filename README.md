<p align="center">
    <img src="https://raw.githubusercontent.com/justin-himself/better-fanoverlord/master/icon.png" width="40%" height="40%" alt="FanOverlord">
</p>

# (Better) FanOverlord

![](https://img.shields.io/badge/ARCH-x86-9cf) ![](https://img.shields.io/badge/ARCH-x86_64-red) ![](https://img.shields.io/badge/ARCH-ARM_64-ff69b4) ![](https://img.shields.io/badge/ARCH-ARM_v7-yellow) ![](https://img.shields.io/badge/ARCH-ARM_v6-green) ![](https://img.shields.io/badge/ARCH-PowerPC_64_le-blueviolet) ![](https://img.shields.io/badge/ARCH-IBM_Z-blue) 

This is a Docker container that uses IPMI to monitor and control the fans on a Dell EMC Poweredge server through the iDRAC using raw commands.  
This script will read the CPU temp sensor repetitively and then adjust the fan speed according to a user-defined function.  
The script is based on orlikoski's project [fanoverlord](https://github.com/orlikoski/fanoverlord). 

**Why not let BIOS manages the fan speed?**  

This script actually manages to achieve lower power-efficiency than the default dell bios does. With the power of user-defined function, you can cutomize fan speed in different scenarios.   

Also, in some models (like my R720xd) the bios actually functions incorrectly after plugin addtional PCI-E device such as a graphics card, see [this](https://www.dell.com/community/PowerEdge-Hardware-General/R720-High-Fan-with-GPU/td-p/6223226), [this](https://www.dell.com/community/PowerEdge-Hardware-General/Dell-PowerEdge-T130-Fan-issue/td-p/4774859) and [this](https://www.dell.com/community/PowerEdge-Hardware-General/PowerEdge-T640-fan-full-speed-after-installing-graphic-card/td-p/5849479)

**What if the script fails?**

The script will give back the fan control to BIOS when force exit or malfunction.


### Configure iDRAC
 - [Set IP Address for iDRAC and ensure docker can communicate with it](https://docs.extrahop.com/current/configure-i-drac/)
 - [Enable IPMI in the iDRAC ](http://www.fucking-it.com/articles/dell-idrac/214-dell-idrac-configure-ipmi)

### Choose Your TEMP-RPM Function

To make your fan speed adjustment as smooth as possible, you should choose a function that maps the relationship between CPU temperature and fan speed. The function is expected to have these features:

- Continous                     -       So the transition is smooth
- Monotonically increasing      -       So the temperature always converages

The default function is  <img src="https://user-images.githubusercontent.com/73123028/183273956-da2ef7f4-c0da-4eea-afd2-0f0243b23d9b.png" width="20%" height="20%">, where s is fan speed and t is temperature.   


This function works well when temperature is between 30 degrees and 80 degrees, and provides optimal power consumption in this range.

<p align="center">
    <img src="https://user-images.githubusercontent.com/73123028/183273680-dc27dbf4-04e1-4ef7-b26c-606fb6a75622.png" width="40%" height="40%">
</p>

### Choose your time condition

`TIME_COND` is an argument that sets the condition when fanoverlord should enabled according to time. This is to suit different usage senarios. For example, I only want fanoverlord to be enabled when I'm asleep to lower the fan noise to minimum, but I want the system manages fan for me at day for tasks with heavy CPU consumption. 

Therefore, I can set the following enviroment variable:

```
-e TIME_COND="t.hour in [23,0,1,2,3,4,5,6,7,8,9]"
```

Notice that, `t` equals to `datetime.now().time()`, and only when the condition evaluates to true, fanoverlord is enabled. Otherwise fanoverlord gives control back to system and wait one miniute to check again.

If you don't care about time conditon and want fanoverlord to be always enabled, set `TIME_COND` to `1` to always enable fanoverlord.

### Pull the image and Start the container

To pull the image:

```
docker pull https://hub.docker.com/r/justinhimself/better-fanoverlord
```

To start the container:

```
docker run \
    --name better-fanoverlord \
    --restart on-failure \
    --network host \
    -e TZ=Asia/Shanghai \
    -e CPU_NUM=2 \
    -e IPMI_HOST="192.168.0.120" \
    -e IPMI_USER="root" \
    -e IPMI_PW="calvin" \
    -e SPEED_FUNC="tanh((t-55)/10)*40 + 50" \
    -e TIME_COND=1 \
    -d justinhimself/better-fanoverlord
```


