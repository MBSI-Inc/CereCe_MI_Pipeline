import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")
from scipy.signal import welch, butter, filtfilt


def welch_PSD(data, sf, window_sec, dB=False):
    """Get data to plot the Welch's PSD.
    Consider this just a function to get PSD values in dB units.

    Requires MNE-Python >= 0.14.

    Parameters
    ----------
    data : 1d-array
        Input signal in the time-domain.
    sf : float
        Sampling frequency of the data.
    window_sec : float
        Length of each window in seconds for Welch's PSD
    dB : boolean
        If True, convert the power to dB.
    """

    # Compute the PSD
    freqs_welch, psd_welch = welch(data, sf, nperseg=window_sec * sf)

    # Optional: convert power to decibels (dB = 10 * log10(power))
    if dB:
        psd_welch = 10 * np.log10(psd_welch)

    return freqs_welch, psd_welch


def custom_filter(exg, low, high, sf, filt_type, order=4):
    """Butterworth filter of order N

    Use to filter EEG information between a certain frequency
    band in a bandpass or band stop fashion.

    Args:
        exg: EEG signal with the shape: (N_chan, N_sample)
        low: Low cutoff frequency
        high: High cutoff frequency
        sf: Sampling rate
        filt_type: Filter type, 'bandstop' or 'bandpass'
    Returns:
        (numpy ndarray): Filtered signal (N_chan, N_sample)
    """
    N = 4  # Should consider changing this to 8
    b, a = butter(N, [low, high], filt_type, fs=sf)
    return filtfilt(b, a, exg)


def filter_epoch(epoch, low, high, sf):
    """
    Takes in an epoch and applies a filter pipeline:
    - A notch filter to remove powerline noise
    - Bandpass filter

    Assumes a 2D array where rows are channels and columns are data points.
    Gets each channel, filters the 50Hz noise and then filters it between
    a range specified by low and high.

    Returns an array of size channels by data points
    """
    epoch_notch = custom_filter(epoch, 45, 55, sf, "bandstop")
    epoch_notch_bp = custom_filter(epoch_notch, low, high, sf, "bandpass")
    return epoch_notch_bp


def filter_epochs(epochs, low, high, sf):
    """
    Takes in multiple epochs and filters them by calling filter_epoch
    which applies our filtering pipeline.

    Assumes a 3D array, of size epochs x channels x data point

    Returns a numpy array of the same size
    """
    n_tr = epochs.shape[0]
    filtered_epochs = []
    for tr_ind in range(n_tr):
        epoch_filt = filter_epoch(epochs[tr_ind], low, high, sf)
        filtered_epochs.append(epoch_filt)

    return np.array(filtered_epochs)


# TODO generalise this function
def Cz_rereference(arr, Cz_ind):
    """
    Rereferences an array to a channel (Cz)

    Subtracts channel Cz from other channels in the array.
    Assumes rows are channels and columns are data points.

    Returns a numpy array of size (channels - 1) x data points
    """
    arr_cz = arr - arr[Cz_ind, :].reshape(1, arr.shape[1])
    arr_cz = np.delete(arr_cz, Cz_ind, axis=0)
    return arr_cz


def PSD_epoch(epoch, sf, low, high):
    """
    Take an epoch and calculate the Power Spectral Density between
    a frequency range low to high.

    Assumes rows are channels and columns are data points. Takes each
    channel and calculates the PSD.

    Returns a 1D numpy array of size channels x PSD
    """
    n_ch = epoch.shape[0]
    psds = []  # all psds
    for ch in range(n_ch):
        temp_psd, freqs = plt.psd(epoch[ch, :], NFFT=sf, Fs=sf)
        plt.close()  # close the plot, we just use the filtering
        psds.append(temp_psd)
    psds = np.array(psds)

    low_ind = np.where(freqs == low)  # get the index of low pass
    high_ind = np.where(freqs == high)  # get the index of high pass

    # The +1 to make it inclusive
    # psds = psds[:, low_ind[0][0] : high_ind[0][0] + 1]
    psds = psds[:, low_ind[0][0] : high_ind[0][0]]
    # freqs = freqs[low_ind[0][0] : high_ind[0][0] + 1]
    freqs = freqs[low_ind[0][0] : high_ind[0][0]]
    psds = psds.ravel()  # reshape into the shape that the model takes

    return psds, freqs


def PSD_epochs(epochs, sf, low, high):
    """ "
    Takes a list of epochs and calculates the PSD for each of them

    Assumes each epoch has row as channels and columns as data points.
    For each epoch in the list, call PSD_epoch

    Return an array of size epochs x channels x PSD, and the frequencies
    """
    n_tr = epochs.shape[0]
    psds = []
    for epoch_ind in range(n_tr):
        psd, freqs = PSD_epoch(epochs[epoch_ind], sf, low, high)
        psds.append(psd)
    return np.array(psds), freqs
