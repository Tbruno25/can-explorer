import argparse
import sys

from can_explorer import CanExplorer
from can_explorer.resources.demo import demo_config

parser = argparse.ArgumentParser()
parser.add_argument("--demo", action="store_true")
args = parser.parse_args()

app = CanExplorer()

if args.demo:
    app.run(test_config=demo_config)
else:
    app.run()

sys.exit()
