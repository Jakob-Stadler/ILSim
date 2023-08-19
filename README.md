# ILSim

ILSim is a software simulation of Keyence [IL-Sensors](https://www.keyence.com/products/measure/laser-1d/il/) communicating through a [DL-EN1 communication unit](https://www.keyence.com/products/sensor/network-communication/dl/) written in pure Python without external depenencies.

Its intended use is speeding up development of application software which intends to use IL sensors through a normal TCP/IP ethernet network connection. For an example of such a use case, please check out [ILInspect](https://github.com/Jakob-Stadler/ILInspect).

ILSim allows rapid and continous integration tests early in the production pipeline of application software by eliminating the need to connect to real hardware to verify correct communication protocol handling. Since its completely software controlled, testing with different internal sensor states is as easy as loading a prepared configuration file. No need to fiddle with small buttons on the physical device or risk damaging the sensor hardware to test rare error conditions like overcurrent.

It can be run locally on the same machine as the application software or remotely on another machine in the same network, allowing the use of low-cost single-board computers like the Raspberry Pi to masquerade as a DL-EN1 communication unit with its connected sensors.

ILSim is written based on the official protocols published by Keyence in its [IL](https://www.keyence.com/download/download/confirmation/?dlAssetId=AS_49018&dlSeriesId=WS_SR48219&dlModelId=&dlLangId=&dlLangType=en-GB) and [DL-EN1](https://www.keyence.com/download/download/confirmation/?dlAssetId=AS_83304&dlSeriesId=WS_SR48239&dlModelId=&dlLangId=&dlLangType=en-GB) user manuals (Download requires free account registration). No internal documents or hardware reverse engineering were used in its development so there's no risk of IP infringement.

ILSim is written in Python 3.11 and fully type annotated. It passes both mypy and pyright in their strict analysis modes to ensure reliable type correctness for future developers.

## Installation

ILSim requires at least Python 3.11 since it uses typing features introduced in that version. Make sure its executable path is included in the `PATH` system variable.

Clone / Download this repository and open a terminal window (e.g. bash on Linux or CMD on Windows) in its extracted root folder.

Optionally, create a virtual environment for development. Since ILSim doesn't use any external packages, it should run just fine with the system installation of Python, but using virtual environments is good practise for development.

For Linux:
```bash
$ python -m venv .venv
$ source .venv/bin/activate
```

For Windows (Python Manager required, if you only have one version of Python installed, you can use `python.exe` instead of `py -3`):
```cmd
py -3 -m venv .venv
.venv\Scripts\activate
```

To run a simple demonstation of the sensor communication, run the server and client in two different terminal windows.

For the server:
```bash
$ python ./server.py ./config.json
```

For the client:
```bash
$ python ./client.py <your command here>
```

For example, to read the measurement values of all connected sensors, instruct the client to send the `M0` command with `python ./client.py M0`


## Configuration

Determining the make-up and state of the simulated components is done through simple JSON files. See [config.json](config.json) as an example of how these files are supposed to look like.

```jsonc
{
  // hostname or ip of the server endpoint, use localhost to make it local-only
  // or 0.0.0.0 to make it publically availble to all devices on the network.
  "host": "localhost",

  // port number between 1 and 65535, has to match with client.
  "port": 9999,

  // array of sensors to be simulated
  "sensors": [
    {
      // sensor type, check FACTORY_MAPPING on the very bottom of ilsim/sensor.py
      // to see valid values for type.
      "type": "IL-030",

      // sensor attribute overrides, use the attributes of SensorUnit in 
      // ilsim/sensor.py to set the internal state the sensor
      "overrides": {
        // Special attribute that randomizes the measurement value every time
        // it gets read.
        "randomized": true,

        // Upper limit of the measurement value randomization
        "randomized_upper_limit": 3.0,

        // Lower limit of the measurement value randomization
        "randomized_lower_limit": -3.0
      }
    },
    {  // Add up to 7 more sensors with their own configuration
      ...
    },
    ...
  ]
}
```

## Usage

This project comes with 2 example configs with 6 sensors each. You can run them both simultaneously in two terminal windows.

Terminal 1:
```bash
$ python ./server.py ./config.json
```

Terminal 2:
```bash
$ python ./server.py ./config2.json
```

Now you can use either the included `client.py` to manually communicate with the sensors or use the default configuration of [ILInspect](https://github.com/Jakob-Stadler/ILInspect) to locally connect to the sensors over port 9999 and 9998.

