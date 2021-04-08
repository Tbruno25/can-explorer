# CanoPy

Canopy is a visualization tool for plotting CAN bus message payloads. 

## Installation

Use [pip](https://pip.pypa.io/en/stable/) to install the following dependencies.

```bash
pip install python-can
pip install pyqtgraph
pip install PyQt5
```

## Usage

Edit `config.py` with the corresponding settings for your adapter. Refer to the python-can [docs](https://python-can.readthedocs.io/en/master/configuration.html#in-code) for more info.

Run `canopy.py` to view a real time plot for each id.

Press `i` on your keyboard to ignore all currently displayed id's.

## Screenshot 

![](https://i.ibb.co/kJbf0ph/screenshot-from-2021-04-07-19.png)

## License
[MIT](https://choosealicense.com/licenses/mit/)