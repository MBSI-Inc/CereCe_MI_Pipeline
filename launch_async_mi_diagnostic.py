## script to launch online motor imagery experiment

import argparse
from mi_bci import AsyncMIDiagnostic
import constants


# Connects to an Explore and begins online MI
# Assumes existence of an already trained model for classification
def main():
    """
    Runs async MI with UI output for MI detection display.
    Does not support interaction.
    """
    # Main window
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
        dest="use_trigger",
        type=bool,
        help="whether to only pull data on keyboard input",
    )
    parser.add_argument(
        "-m",
        "--mockfilename",
        dest="mock_file",
        type=str,
        help="name of csv file for mock data source",
    )
    args = parser.parse_args()

    if args.name is None:
        args.name = constants.DEFAULT_EEG_NAME
    if args.filename is None:
        args.filename = constants.DEFAULT_FILENAME

    try:
        diagnostic = AsyncMIDiagnostic(args.name, args.filename, args.mock_file)
        diagnostic.run()
    except KeyboardInterrupt:
        print("Async MI Core interrupted by keyboard interrupt")
        pass


if __name__ == "__main__":
    main()
