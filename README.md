# CanoPy

Canopy is a visualization tool for plotting CAN bus message payloads. 

## Installation

```
$ git clone https://github.com/Tbruno25/canopy
$ cd canopy
$ pip install .
```

## Usage

Run `canopy` from the command line with the appropriate arguments per your adapter.  
Refer to the python-can [docs](https://python-can.readthedocs.io/en/master/configuration.html#in-code) for argument info.

```
$ canopy -i socketcan -c can0 -b 500000
```

Pressing `i` on your keyboard will ignore and clear all currently displayed id's.  
Using `arrow up` or `arrow down` will adjust message buffer sizes. 

Alternatively, a saved log file can be visualized by redirecting the output to a virtual interface.

First ensure the interface is up
```
$ sudo modprobe vcan
$ sudo ip link add dev vcan0 type vcan
$ sudo ip link set up vcan0
```

Then start CanoPy
```
$ canopy -i socketcan -c vcan0
```

And use `canplayer` to replay the log file while redirecting output
```
$ canplayer -I candump-messages.log vcan0=can0
```

## Screenshot 

![](https://i.ibb.co/ynrNndq/Screenshot-from-2021-04-16-12-23-26.png)

## Todo

- Display id's sorted from min to max
- Add a way to remove specific id's 

## License
[MIT](https://choosealicense.com/licenses/mit/)
