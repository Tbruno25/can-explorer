# CanoPy

Canopy is a visualization tool for plotting CAN bus message payloads. 

## Installation

```bash
$ git clone https://github.com/Tbruno25/canopy
# cd into the /canopy directory
$ pip install .
```

## Usage

Run `canopy` from the command line with the appropriate settings per your adapter. 
For example `canopy -i socketcan -c can0 -b 500000`
Refer to the python-can [docs](https://python-can.readthedocs.io/en/master/configuration.html#in-code) for more info.

Press `i` on your keyboard to ignore all currently displayed id's.
Use `arrow up` or `arrow down` to adjust message buffer size. 

## Screenshot 

![](https://i.ibb.co/ynrNndq/Screenshot-from-2021-04-16-12-23-26.png)

## License
[MIT](https://choosealicense.com/licenses/mit/)