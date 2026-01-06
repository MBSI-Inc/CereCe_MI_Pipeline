from explorepy import Explore
from src.record_MI_class import Record
from constants import DEFAULT_FILENAME, DEFAULT_EEG_NAME
import argparse


def main():
    """
    Runs the recording experiment to collect data for training the model

    This starts the EEG and passes the EEG object to Record
    to run the MI experiment and record offline samples.
    """

    parser = argparse.ArgumentParser(
        description="A script to run recording in an experiment setting"
    )
    parser.add_argument(
        "-n", "--name", dest="name", type=str, help="Name of the EEG device: String"
    )
    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        type=str,
        help="Name to use for reading and writing CSV and SAV files: String",
    )
    args = parser.parse_args()

    # Apply default values if they have not been supplied
    if args.name is None:
        args.name = DEFAULT_EEG_NAME
    if args.filename is None:
        args.filename = DEFAULT_FILENAME

    # Connect to Explore and record data
    explore = Explore()
    explore.connect(device_name=args.name)
    explore.record_data(file_name=args.filename, file_type="csv", do_overwrite=True)

    # Start recording training data
    Record(explore)
    explore.disconnect()


if __name__ == "__main__":
    main()
