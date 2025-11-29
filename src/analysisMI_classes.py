# Import helper functions
from .helper_functions import *

# class to visualise / analyse and classify motor imagery
import pandas as pd
import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
from .constants import MI_CODE, REST_CODE
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


class MI_analyse:
    """
    Takes in the recorded EEG data along with the parameters for slicing the trials
    out and parameters for processing.

    Used to provide clean training data for the model.
    """

    def __init__(self, exg_file, markers_file, lf, hf, sf, t_min, t_max, p2p_max=70):
        """
        Initialises parameters required for motor imagery analysis

        filename: name of the exg file containing eeg data
        exg: extracts eeg data into dataframe
        markers: extracts corresponding marker data into dataframe
        n_ch: number of channels used
        CH_LABELS: channel locations in order of electrodes - follows our pre-agreed order of channel set up
        lf: low cut off frequency
        hf: high cut off frequency
        sf: sampling rate
        t_min: start of epoch window following event
        t_max: end of epoch window following event
        p2p_max: max peak to peak amplitude for epoch rejection criteria
        """

        # load in the csv files
        self.filename = f"{exg_file=}".split("=")[0]
        self.exg = pd.read_csv(exg_file)
        self.markers = pd.read_csv(markers_file)
        self.n_ch = self.exg.shape[1] - 1  # minus one for marker column
        self.CH_LABELS = []
        self.lf = lf
        self.hf = hf
        self.sf = sf
        self.t_min = t_min
        self.t_max = t_max
        self.p2p_max = p2p_max

        # This is assuming we only ever use these
        if self.n_ch == 7:
            self.CH_LABELS = ["Fz", "Fc1", "Fcz", "Fc2", "C3", "Cz", "C4"]
        elif self.n_ch == 8:
            self.CH_LABELS = ["Fz", "Fc1", "Fcz", "Fc2", "C3", "Cz", "C4", "x"]
        elif self.n_ch == 4:
            self.CH_LABELS = ["Fcz", "C3", "Cz", "C4"]
        else:
            print("Please use a channel configuration we are used to", self.n_ch)

    # The processing of each individual trial is done here
    # TODO make sure separate_epochs only separates epochs and doesn't process jack shit
    def separate_epochs(
        self,
        epoch_type1,
        epoch_type2,
        lf=None,
        hf=None,
        sf=None,
        t_min=None,
        t_max=None,
        p2p_max=70,
    ):
        """
        Returns two arrays each of a specified type of epoch ie. Rest, Right or Left
        epoch_type1, epoch_type2: needs to be entered as the corresponding code found in src.constants file
        """

        # these should have been attributed when class is first called, otherwise can change parameters
        if lf is None:
            lf = self.lf
        if hf is None:
            hf = self.hf
        if sf is None:
            sf = self.sf
        if t_min is None:
            t_min = self.t_min
        if t_max is None:
            t_max = self.t_max

        ts_sig = self.exg["TimeStamp"].to_numpy()
        ts_markers_epoch_type1 = self.markers[self.markers.Code.isin([epoch_type1])][
            "TimeStamp"
        ].to_numpy()
        ts_markers_epoch_type2 = self.markers[self.markers.Code.isin([epoch_type2])][
            "TimeStamp"
        ].to_numpy()
        sig = self.exg[["ch" + str(i) for i in range(1, self.n_ch + 1)]].to_numpy().T
        sig -= sig[0, :] / 2

        # Pipeline start
        # Cz re-reference
        Cz_ind = self.CH_LABELS.index("Cz")
        sig_cz = Cz_rereference(arr=sig, Cz_ind=Cz_ind)

        # get the epochs
        type1_epochs = self.extract_epochs(
            sig_cz, ts_sig, ts_markers_epoch_type1, t_min, t_max, sf
        )
        type2_epochs = self.extract_epochs(
            sig_cz, ts_sig, ts_markers_epoch_type2, t_min, t_max, sf
        )

        # filter them
        type1_epochs_filt = filter_epochs(epochs=type1_epochs, low=lf, high=hf, sf=sf)
        type2_epochs_filt = filter_epochs(epochs=type2_epochs, low=lf, high=hf, sf=sf)

        # get rid of shit epochs
        type1_epochs_filt = self.reject_bad_epochs(type1_epochs_filt, p2p_max)
        type2_epochs_filt = self.reject_bad_epochs(type2_epochs_filt, p2p_max)
        # Pipeline end

        return type1_epochs_filt, type2_epochs_filt

    def extract_epochs(self, sig, sig_times, event_times, t_min, t_max, sf):
        """Extracts epochs from signal
        Args:
            sig: EEG signal with the shape: (N_chan, N_sample)
            sig_times: Timestamp of the EEG samples with the shape (N_sample)
            event_times: Event marker times
            t_min: Starting time of the epoch relative to the event time
            t_max: End time of the epoch relative to the event time
            sf: Sampling rate
        Returns:
            (numpy ndarray): EEG epochs
        """
        offset_st = int(t_min * sf)
        offset_end = int(t_max * sf)
        epoch_list = []
        for i, event_t in enumerate(event_times):
            try:
                idx = np.argmax(sig_times > event_t)
                if idx + offset_end <= sig.shape[1]:
                    epoch_list.append(
                        np.array(sig[:, idx + offset_st : idx + offset_end])
                    )
                else:
                    print(f"Skipping epoch {i} due to insufficient data")
            except Exception as e:
                print(f"Error in epoch {i}: {e}")
        return np.array(epoch_list)

    def reject_bad_epochs(self, epochs, p2p_max):
        """Rejects bad epochs based on a peak-to-peak amplitude criteria
        Args:
            epochs: Epochs of EEG signal
            p2p_max: maximum peak-to-peak amplitude

        Returns:
            (numpy ndarray):EEG epochs
        """
        temp = epochs.reshape((epochs.shape[0], -1))
        res = epochs[np.ptp(temp, axis=1) < p2p_max, :, :]
        print(
            f"{temp.shape[0] - res.shape[0]} epochs out of {temp.shape[0]} epochs have been rejected."
        )
        return res

    # TODO fix/test/restructure plotting functions
    def plot_time_series(self, epoch_type1, epoch_type2):
        """
        Plots the time series data per channel of a given exg file.
        compares two epoch types
        """
        type1_epochs, type2_epochs = self.separate_epochs(epoch_type1, epoch_type2)

        erp_type1_epoch = type1_epochs.mean(axis=0)
        erp_type2_epoch = type2_epochs.mean(axis=0)

        t = np.linspace(self.t_min, self.t_max, erp_type2_epoch.shape[1])
        _, axes = plt.subplots(figsize=(20, 10), nrows=2, ncols=self.n_ch // 2)

        for i, ax in enumerate(axes.flatten()):
            ax.plot(t, erp_type1_epoch[i, :], label=f"{epoch_type1=}".split("=")[0])
            ax.plot(
                t,
                erp_type2_epoch[i, :],
                "tab:orange",
                label=f"{epoch_type2=}".split("=")[0],
            )
            ax.plot([0, 0], [-30, 30], linestyle="dotted", color="black")
            ax.set_ylabel("\u03bcV")
            ax.set_xlabel("Time (s)")
            ax.set_title(self.CH_LABELS[i])
            ax.set_ylim([-10, 20])
            ax.legend()
        plt.tight_layout()
        plt.show()

    def get_PSD_data(self):
        """
        Calculates and returns average psd of trials of same type, and frequency resolution
        """
        rest, mi = self.separate_epochs(REST_CODE, MI_CODE)

        all_psd_MI, freqs = PSD_epochs(mi, self.sf, self.lf, self.hf)
        all_psd_rest, freqs = PSD_epochs(rest, self.sf, self.lf, self.hf)

        return all_psd_rest, all_psd_MI, freqs

    # TODO fix/test/restructure plotting functions
    def plot_PSD_ch(self):
        """
        Plot each average PSD per channel according to the two types of epochs
        """
        rest_PSD, mi_PSD, freqs = self.get_PSD_data()
        all_psd_rest = rest_PSD.mean(axis=0)
        all_psd_MI = mi_PSD.mean(axis=0)

        fig, axes = plt.subplots(figsize=(20, 10), nrows=2, ncols=(self.n_ch + 1) // 2)
        for i, ax in enumerate(axes.flatten()):
            ax.plot(freqs, all_psd_rest[i, :], label="LEFT")
            ax.plot(freqs, all_psd_MI[i, :], "tab:orange", label="RIGHT")
            ax.set_ylabel("dB")
            ax.set_xlabel("Frequency (Hz)")
            ax.set_title(self.CH_LABELS[i])
            ax.set_xlim([0, 40])
            ax.set_ylim([0, 6])
            ax.legend()
        plt.tight_layout()
        plt.show()

    # TODO fix/test/restructure plotting functions
    def plot_PSD_RvL(self):
        """
        Compare channel C3 and C4 for each of Right or Left hand motor imagery
        """
        rest_PSD, mi_PSD, freqs = self.get_PSD_data()

        all_psd_rest = rest_PSD.mean(axis=0)
        all_psd_MI = mi_PSD.mean(axis=0)

        C3_ind = self.CH_LABELS.index("C3")
        C4_ind = self.CH_LABELS.index("C4")

        fig, axes = plt.subplots(2, figsize=(8, 8), sharex=True)
        axes[0].plot(freqs, all_psd_rest[C3_ind, :], label="C3")
        axes[0].plot(freqs, all_psd_rest[C4_ind, :], "tab:orange", label="C4")
        axes[0].set_title("LEFT")
        axes[1].plot(freqs, all_psd_MI[C3_ind, :], label="C3")
        axes[1].plot(freqs, all_psd_MI[C4_ind, :], "tab:orange", label="C4")
        axes[1].set_title("RIGHT")
        for i, ax in enumerate(axes.flatten()):
            ax.set_ylabel("dB")
            ax.set_xlabel("Frequency (Hz)")
            ax.set_xlim([0, 40])
            ax.set_ylim([0, 6])
            ax.legend()
        plt.tight_layout()
        plt.show()

    def get_training_data(self):
        """
        Label training data
        """
        restPSD, miPSD, freqs = self.get_PSD_data()

        # Create dataset
        X = np.vstack([restPSD, miPSD])
        y = np.array([0] * restPSD.shape[0] + [1] * miPSD.shape[0])

        print(X.shape, restPSD.shape, miPSD.shape)
        print(100 * "=")
        return X, y


class MI_classifier:
    """
    Takes in the processed EEG data, and optionally to load a model

    Allows for the training, cross evaluation, inference (called evaluate_model),
    and saving of a model
    """

    def __init__(self, data, labels, filename, load_model=True):
        """
        data is PSD for each trial in the channels of interest
        filename should be of format MI_name1 etc.
        if create True, use data to create new model
        """
        self.data = data
        self.labels = labels
        self.filename = filename

        if load_model:
            self.model = self.load_model()

    # TODO make the model a parameter somehow as part of a higher level pipeline
    # Like, it shouldn't be called in here and then if we have to change it
    # and all the other places that have the defined model
    def cross_val_model(self, save_model=True):
        """
        evaluates a model using cross validation and gives average score
        ie. train and test on same data set
        """
        model = LDA(solver="eigen", shrinkage="auto")
        select_scores = cross_val_score(
            model, self.data, self.labels, cv=KFold(self.labels.shape[0])
        )
        print(
            "Cross Validation: Accuracy = {0:.2f} \nSt. Dev = {1:.2f}".format(
                select_scores.mean() * 100, select_scores.std()
            )
        )

        # paranoid, so instantiate a new model
        model = LDA(solver="eigen", shrinkage="auto")
        model.fit(self.data, self.labels)

        if save_model:
            model_filename = self.filename + ".sav"
            pickle.dump(model, open(model_filename, "wb"))
            print("LDA Model saved!")

        return model

    def load_model(self):
        """
        model_name should be of form name.sav. Ensure the model is saved in models folder of same path as this python script
        """
        model_folder = os.getcwd() + "/models"
        loaded_model = pickle.load(open(model_folder + self.filename + ".sav", "rb"))
        return loaded_model

    # TODO
    # Consider renaming this to something like infer or anything
    # to do with inference
    def evaluate_model(self):
        """
        Run one instance of model and show confusion matrix
        """
        y_pred = self.model.predict(self.data)

        print(
            ConfusionMatrixDisplay(
                confusion_matrix(self.labels, y_pred), display_labels=["LEFT", "RIGHT"]
            ).plot()
        )
