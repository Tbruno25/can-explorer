import argparse
import sys

from can_explorer import AppController, AppView, PlotModel
from can_explorer.resources.demo import demo_config

parser = argparse.ArgumentParser()
parser.add_argument("--demo", action="store_true")
args = parser.parse_args()

controller = AppController(PlotModel(), AppView())

if args.demo:
    controller.run(demo_config)
else:
    controller.run()

sys.exit()
