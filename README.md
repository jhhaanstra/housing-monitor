# Housing Monitor
Checks the activated websites on an interval for apartment and sends a notification when a new apartment is found. 

## Installation instructions
When running on Linux, install the `libnotify` package which is required by notify_py used for sending desktop notifications.

1. clone the repository
2. Go to the project root and execute `pip install -r requirements.txt`
3. Set up a config or use the default one in the project root
4. Start the monitor: `python3 ./main.py --config /path/to/config`