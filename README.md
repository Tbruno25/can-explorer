# CanoPy

Canopy is a visualization tool for plotting CAN bus message payloads. 

## Installation

```bash
$ git clone https://github.com/Tbruno25/canopy
# cd into the /canopy directory
$ pip install -r requirements.txt
```

## Usage

Edit `config.py` with the corresponding settings for your adapter. Refer to the python-can [docs](https://python-can.readthedocs.io/en/master/configuration.html#in-code) for more info.

Run `canopy.py` to view a real time plot for each id.

Press `i` on your keyboard to ignore all currently displayed id's.
Use `arrow up` or `arrow down` to adjust message buffer size. 

## Screenshot 

![](https://i.ibb.co/ynrNndq/Screenshot-from-2021-04-16-12-23-26.png)

## License
[MIT](https://choosealicense.com/licenses/mit/)