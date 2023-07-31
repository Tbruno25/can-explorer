<h1 align="center">
  <a href="https://github.com/tbruno25/can-explorer">
    <!-- Please provide path to your logo here -->
    <img src="https://github.com/Tbruno25/can-explorer/raw/main/docs/images/logo.png" alt="Logo" width="200" height="200">
  </a>
</h1>

<div align="center">
  can-explorer
  <br />
  <a href="https://github.com/tbruno25/can-explorer/issues/new?assignees=&labels=bug&template=01_BUG_REPORT.md&title=bug%3A+">Report a Bug</a>
  ·
  <a href="https://github.com/tbruno25/can-explorer/issues/new?assignees=&labels=enhancement&template=02_FEATURE_REQUEST.md&title=feature%3A+">Request a Feature</a>
  ·
  <a href="https://github.com/tbruno25/can-explorer/issues/new?assignees=&labels=question&template=04_SUPPORT_QUESTION.md&title=support%3A+">Ask a Question</a>
</div>

<div align="center">
<br/>


[![PyPI version](https://img.shields.io/pypi/v/can-explorer?color=mediumseagreen)](https://pypi.org/project/can-explorer/)
[![Python Versions](https://img.shields.io/pypi/pyversions/can-explorer?color=mediumseagreen)](https://pypi.org/project/can-explorer/)
[![Stars](https://img.shields.io/github/stars/tbruno25/can-explorer?color=mediumseagreen)](https://github.com/Tbruno25/can-explorer/stargazers)
</div>

---

## About

`can-explorer` is a CAN bus visualization tool designed to aid in reverse engineering.

![Demo](https://github.com/Tbruno25/can-explorer/raw/main/docs/images/demo.gif)

### How does this help me?
By continuously plotting all payloads for each CAN id, spotting trends that correspond to a specific action can become signicantly easier to identify. 

Please refer to this [prior article](https://tbruno25.medium.com/car-hacking-faster-reverse-engineering-using-canopy-be1955843d57) I wrote for a working example of how this approach can be used to find which id includes speedometer data.


### Built With


[![DearPyGui](https://github.com/Tbruno25/can-explorer/raw/main/docs/images/dearpygui-logo.png)](https://github.com/hoffstadt/DearPyGui)
[![PythonCan](https://github.com/Tbruno25/can-explorer/raw/main/docs/images/pythoncan-logo.png)](https://github.com/hardbyte/python-can)

## Getting Started

### Installation

[pipx](https://pypa.github.io/pipx/) is recommended although any package manager that supports `pyproject.toml` files can be used.

```sh
pipx install can-explorer
``` 

## Usage

The gui can be launched by running one of the below commands from a terminal.
```sh 
can-explorer
``` 

```sh 
python3 -m can_explorer
``` 

Before starting the viewer, you ***must*** navigate to the settings tab and input your interface adapter configuration to create a bus instance. Please refer to the [python-can docs](https://python-can.readthedocs.io/en/stable/index.html) for more information regarding the various interfaces supported. 

The gui can also be launched with a demo flag which will auto select the virtual interface option and start streaming simulated CAN data in a background process.

```sh 
can-explorer --demo
``` 

## Support

Reach out to the maintainer at one of the following places:
- [GitHub issues](https://github.com/tbruno25/can-explorer/issues/new?assignees=&labels=question&template=04_SUPPORT_QUESTION.md&title=support%3A+)
- Contact options listed on [this GitHub profile](https://github.com/tbruno25)

If you want to say **thank you** or/and support active development of can-explorer consider adding a [GitHub Star](https://github.com/tbruno25/can-explorer) to the project.


## Contributing

Please read [our contribution guidelines](docs/CONTRIBUTING.md)

For a full list of all authors and contributors, see [the contributors page](https://github.com/tbruno25/can-explorer/contributors).

## License

This project is licensed under the **GNU General Public License v3**.

See [LICENSE](LICENSE) for more information.
