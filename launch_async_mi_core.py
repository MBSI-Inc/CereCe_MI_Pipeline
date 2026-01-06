## script to launch async mi lite demo
import argparse
import time
import constants
from src.async_mi_core import AsyncMICore
import keyboard


# Connects to an Explore and begins async MI
# Assumes existence of an already trained model for classification
def main():
    """
    Runs async MI with CLI interaction and output. See launch_async_mi_diagnostic for UI output.
    When running, press 'p' to pull the current data out of MI and print to console.
    Press 'k' to kill the process.
    """
    parser = argparse.ArgumentParser(
        description="A script to run a visual motor imagery experiment"
    )
    parser.add_argument(
        "-n", "--name", dest="name", type=str, help="Name of the device."
    )
    parser.add_argument(
        "-f", "--filename", dest="filename", type=str, help="name of csv file"
    )
    parser.add_argument(
        "-t",
        "--trigger",
        dest="pull_trigger_type",
        type=str,
        help="What triggering event to use for pulling data from async MI. Choose from 'Interval' or 'KeyPress'",
    )
    parser.add_argument(
        "-i",
        "--interval",
        dest="time_trigger_interval",
        type=float,
        help="With 'Interval' trigger, this is the number of seconds to wait between data pulls",
    )
    parser.add_argument(
        "-m",
        "--mockfilename",
        dest="mock_file",
        type=str,
        help="name of csv file for mock data source",
    )
    parser.add_argument(
        "-s",
        "--silent",
        dest="is_silent",
        type=bool,
        help="whether the async mi should run silently or not",
    )
    args = parser.parse_args()

    if args.pull_trigger_type not in ["KeyPress", "Interval"]:
        raise Exception(
            f'Invalid value for trigger type. Recieved {args.pull_trigger_type}, expected "Interval" or "KeyPress"'
        )
    if args.pull_trigger_type == "Interval" and not args.time_trigger_interval:
        raise Exception(
            "Time trigger interval must be provided when using Interval type trigger"
        )

    if args.name is None:
        args.name = constants.DEFAULT_EEG_NAME
    if args.filename is None:
        args.filename = constants.DEFAULT_FILENAME

    predicted = -0.5
    predicted_raw = -0.5

    try:
        with AsyncMICore(
            args.name, args.filename, args.mock_file, args.is_silent
        ) as asyncMI:
            while True:
                # Either wait for a period of time or wait for a key press
                # Regardless, async MI should keep processing in a separate thread
                if args.pull_trigger_type == "Interval":
                    time.sleep(args.time_trigger_interval)
                else:
                    keyboard.read_key()

                # Pull the current prediction from asyncMI
                predicted, predicted_raw = asyncMI.getData()
                print(
                    "#Main prediction: {0}, raw prediction: {1}".format(
                        predicted, predicted_raw
                    )
                )
                # ToDo, use functions from unity_connect to send signal to unity

    except KeyboardInterrupt:
        print("Async MI Core interrupted by keyboard interrupt")
        pass


if __name__ == "__main__":
    main()
