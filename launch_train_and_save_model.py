from constants import DEFAULT_FILENAME
from mi_bci import MI_analyse, MI_classifier
import argparse


def main():
    """
    Runs the model training

    This takes the file name (without the file extension) and gives it
    to MI_analyse for processing and then to MI_classifier for training
    of the model
    """
    parser = argparse.ArgumentParser(
        description="A script to train a model using recorded data"
    )
    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        type=str,
        help="Name to use for reading and writing CSV and SAV files: String",
    )
    args = parser.parse_args()

    # Apply default filename if they have not been supplied
    if args.filename is None:
        args.filename = DEFAULT_FILENAME

    # Using recorded data and saved files, create an LDA model
    exg_file = args.filename + "_ExG.csv"
    markers_file = args.filename + "_Marker.csv"

    trial = MI_analyse(
        exg_file, markers_file, lf=7, hf=30, sf=250, t_min=1.0, t_max=6.0, p2p_max=80
    )

    data, labels = trial.get_training_data()

    classifier = MI_classifier(data, labels, args.filename, load_model=False)
    classifier.cross_val_model(save_model=True)  # saves the model as a .sav file


if __name__ == "__main__":
    main()
