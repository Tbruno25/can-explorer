from argparse import ArgumentParser
from .canopy import can, CanoPy

def main():
    parser = ArgumentParser(
        description="""
        Refer to the following doc for parameters | 
        https://python-can.readthedocs.io/en/master/configuration.html#incode
        """
    )
    parser.add_argument("-i", "--interface", type=str, required=True)
    parser.add_argument("-c", "--channel", type=str, required=True)
    parser.add_argument("-b", "--bitrate", type=int, default=0)
    args = parser.parse_args()

    canopy = CanoPy(
        can.Bus(
            interface=args.interface,
            channel=args.channel,
            bitrate=args.bitrate,
        )
    )
    canopy.run()