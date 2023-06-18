#!/usr/bin/env python
import argparse
import json

from monitor.monitor import Monitor
from targets.target import TargetConfig


def setup_monitor(config_path: str):
    with open(config_path) as t:
        config = json.JSONDecoder().decode(t.read())
        if 'monitor_config' in config:
            target_config = TargetConfig(**config['target_config'])
            monitor = Monitor(target_config=target_config, **config['monitor_config'])
            monitor.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--config', help='Monitoring config JSON file location')
    args = parser.parse_args()
    if args.config is not None:
        setup_monitor(args.config)
    else:
        print("Please provide a config to the program using the --config argument")
