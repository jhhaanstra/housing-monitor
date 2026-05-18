#!/usr/bin/env python
import argparse
import json
import logging
import os
from logging import StreamHandler

from monitor.monitor import Monitor
from targets.target import TargetConfig


def setup_monitor(config_path: str):
    with open(config_path) as t:
        config = json.JSONDecoder().decode(t.read())
        if "monitor_config" in config:
            target_config = TargetConfig(**config["target_config"])
            monitor = Monitor(target_config=target_config, **config["monitor_config"])
            if os.path.isfile("advertisements.txt"):
                with open("advertisements.txt") as file:
                    monitor.stored = [line.rstrip() for line in file]
            monitor.start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler("app.log"), StreamHandler()],
    )

    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("--config", help="Monitoring config JSON file location")
    args = parser.parse_args()
    if args.config is not None:
        setup_monitor(args.config)
    else:
        print("Please provide a config to the program using the --config argument")
