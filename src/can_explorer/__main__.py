import argparse
import sys

from can_explorer import app
from can_explorer.resources.demo import demo_config

parser = argparse.ArgumentParser()
parser.add_argument("--demo", action="store_true")
args = parser.parse_args()


if args.demo:
    app.main(demo_config)
else:
    app.main()

sys.exit()
