[![gateway unittest](https://github.com/bchwtz-fhswf/gateway/actions/workflows/gateway_unittest.yml/badge.svg?branch=main)](https://github.com/bchwtz-fhswf/gateway/actions/workflows/gateway_unittest.yml)
[![docs](https://github.com/bchwtz-fhswf/gateway/actions/workflows/docs.yml/badge.svg)](https://github.com/bchwtz-fhswf/gateway/actions/workflows/docs.yml)

# Gateway-Library

The gateway library serves as an interface between a `Bluetooth Low Energy` device (e.g. sensor like RuuviTag) and any backend. The library offers basic functionalities, such as searching for BLE devices, mutual communication and includes one-sided communication (`listen_advertisements`). The `gateway` contains the classes `hub`, `sensor` and `experimental`. The high-level idea behind this division is to create a twin of the hardware sensor with all possible functionalities and manage it via a hub. Thus the `hub` serves the search for possible sensors and the generation of the twin, as well as the recording of the cyclical advertisements. The `hub` saves a found sensor as an object of the class `sensor`. Via the `sensor object`, the functions described in the following, can be called as methods of `sensor object` and can be called by e.g. `sensor1.get_config()`.
All function calls are executed on the corresponding `sensor` object. The sensors are initially generated by a name and a MAC address, so that these values can also be called to describe the sensor in more detail (`sensor.mac` and `sensor.name`).


## Getting started with gateway preparation

Before you start to run the first codelines follow the steps below:
  1. Make sure your RaspberryOS is up to date
    - `sudo apt-get update` + `sudo apt-get upgrade`
  2. Install BlueZ in order to use the advertisement functions of the gateway
    - `sudo apt-get install bluez bluez-hcidump`
  3. Follow the instructions of the `docs\git_installation_on_raspberrypy.md`

## Installation

To install the project on your Raspberry Pi switch to the gateway-main directory.

`cd /path/to/gateway-main`

Install this project as python package.

`sudo python3 setup.py install`

If the installation was successful, a large output follows. The last line should start with: 
`Finished processing dependencies ...`

The software can be installed via command line.

```{code-block} python
pip3 install -e git+https://<access token>@github.com/bchwtz-fhswf/gateway.git@develop#egg=gateway
```
```{admonition} Note
The token is displayed by github only once for copy in plain text.
If the token is lost, the process must be repeated.
```

## Get the docs

To get detailed informations about functions and classes its recommanded to read the 
full documentation. To do so you can run the following command after you have installed the 
package as explained above:

```{code-block} python
make html
```
This command should trigger the sphinx framework and it should generate an outpult like below:

```{code-block} python
phinx v4.4.0 in Verwendung
making output directory... erledigt
WARNING: html_static_path entry '_static' does not exist
[autosummary] generating autosummary for: gateway.experimental.flashing.rst, gateway.experimental.mqttThing.rst, gateway.experimental.rst, gateway.hub.rst, gateway.sensor.rst, git_installation_on_raspberry.md, index.rst, intro_to_sphinx.rst, link_to_readme.md
Failed to import gateway.experimental.mqttThing.
```

```{admonition} Note
If yout run the `make html` command, before you run the installation process, the make file will probably not work
or the autodoc-funktions will raise multiple error caused by import and ModuleNotFound errors. 
```
The documentation will be stored under `docs/_build` as html files.
To remove this file you can simply run `make clean` in terminal.

## Get sensor advertisments
The Advertisements of the sensor contain values like humidity, temperature, pressure as well as acceleration data, battery and movement information. 

1. Use your git bash or any terminal you'd like to use and make sure you are working on your Raspberry Pi on `demos/` directory. 

2. Exectue the following python file

`python3 demo_advertisement_logging.py`

3. You will get a message like this:
```
2021-12-12 19:10:00,523 - SensorGatewayBleak - WARNING - Abort workloop task via timeout()!
2021-12-12 19:10:01,002 - sensor_hub - WARNING - Warning: To stop the advertisementlogging, you need to interrupt the kernel!
Press any key to confirm!
```
  As written, please press "enter" to continue. 

4. If a sensor was found, the sensor_hub generates an object sensor and stores it in myHub.sensorlist. The last collected sensor date will come up on your screen. You can exit it by pressing the keys: CTRL-C

5. The data will be stored automatically in a CSV file on your Raspberry. To open the file, write the following code line with your correct date.

`nano advertisement-2021-12-13`

If you are not sure what the correct date is, type

`ls`

to find on the top left side the correct name of the CSV file.
It will open a file, inwhich you see your collected data. 


## Get sensor accelerations

1. Change to `demos/` directory

2. Exectue the following python file

`python3 demo_accelerometer_logging.py`

Please note, acceleration logging status 1 means "is active" and -1 means "is inactive". 

## Set acceleration parameter

If you like to understand how the configurations can be set, use in ´demo/` directory 

`python3 demo_set_acceleration_config.py`

If you like to set the config parameters easily, follow the instructions:

1. Switch to directory tools/

2. Type 

`python3 set_acceleration_config.py`

and before pressing enter, 

3. add the parameters you would like to change:

`-s` or `--sampling_rate` for sampling rate  
`-r` or `--sampling_resolution` for sampling resolution  
`-m` or `--measuring_range` for measuring range  
`-d` or `--divider` for divider  

plus the parameter number. 

4. For example if you would like to change all three values, type:

`python3 set_acceleration_config.py -s 100 -r 10 -m 16 -d 4`

5. You can open the help menu, where you find all accepted parameters with

`python3 set_acceleration_config.py --help`

### Parameter options

In the following paragraph, you will find the possible options:

Sampling rate: 1, 10, 25, 50, 100, 200, 400

Sampling resolution: 8, 10, 12
  
Measuring Range: 2, 4, 8, 16

Divider: Every decimal number allowed

## Device Firmware Update with `gateway.experimental.flashing`

To update the firmware of an tag, you can use the flashing module, which can be 
found under `gateway.experimental`. The main class class to handle the update procedure
is the class `device_firmwar_upgrade`. To initialize an object of this class, you need to pass
the following arguments:
  - `path_to_dfu_zip`: Absolut path to the compressed firmware file (e.g. /home/pi/Downloads/firmwar.zip)
  - `destination_path_to_unzip`: Absolute path to unpack the zip file (e.g /home/pi/Desktop/)
  - `sensor.sensor`: Sensor object
The flashing procedure may take some minute to complete.
A demo skript can be found in the `demos/` subdirectory.

## Set_ and Get_Heartbeat

The heartbeat discribes the intervall in which advertisements are sent.
It is also the time in which a connection can be established.
The heartbeat can be set between 200 [ms] and ~65.000 [ms].
The value will be encoded in two bytes.

200 = 00 C8
65.000 = FD E8
