## Getting started with gateway preparation

Before you start to run the first codelines follow the steps below:
  1. Make sure your RaspberryOS is up to date
    - `sudo apt-get update` + `sudo apt-get upgrade`
  2. Install BlueZ in order to use the advertisement functions of the gateway
    - `sudo apt-get install bluez bluez-hcidump`
  3. Follow the instructions of the `docs\git_installation_on_raspberrypy.md`

## Installation

To install the project on your Raspberry Pi switch to the direcory where you find git-clone.

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
## Set time on sensor


## Get sensor data

1. Use your git bash or any terminal you'd like to use and make sure you are working on your Raspberry Pi. 

2. Exectue the following python file

`python3 demo_advertisement_logging.py`

3. You will get a message like this:
```2021-12-12 19:10:00,523 - SensorGatewayBleak - WARNING - Abort workloop task via timeout()!
2021-12-12 19:10:01,002 - sensor_hub - WARNING - Warning: To stop the advertisementlogging, you need to interrupt the kernel!
Press any key to confirm!
```
  As written, please press any key to continue, for example "enter". 

4. If a sensor was found, the sensor_hub generates an object sensor and stores it in myHub.sensorlist. The last collected sensor date will come up on your screen. You can exit it by pressing the keys: CTRL-C

5. The data will be stored automatically in a CSV file on your Raspberry. To open the file, write the following code line with your correct date.

`nano advertisement-2021-12-13`

If you are not sure what the correct date is, type

`ls`

to find on the top left side the correct name of the CSV file.
It will open a file, inwhich you see your collected data. 