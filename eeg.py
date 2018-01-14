#! /usr/bin/env python3

# import mne
import sys
import math
import numpy as np
from scipy.io import loadmat

# from sklearn.pipeline import Pipeline
# from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
# from sklearn.model_selection import ShuffleSplit, cross_val_score

# from mne.decoding import CSP
from matplotlib import pyplot

import argparse
import os


def fourrier(data, sample_rate):
    """ Perfom a fourrier analysis, returns a 2 by n matrix. """
    timestep = 1.0/float(sample_rate)
    power = np.absolute(np.fft.fft(data)) / data.shape[0]
    frequency = np.fft.fftfreq(data.shape[0], d=timestep)

    return np.column_stack((frequency, power))


def bandpass(spectrum, band):
    """ Sample frequency, lower frequency bound, higher frequency bound."""
    new_spectrum = []
    for entry in spectrum:
        if (entry[0] > band[0] and entry[0] < band[1]):
            new_spectrum.append(entry)
    return np.array(new_spectrum)


def spectrum_meanpower(spectrum):
    """ Calculate the mean power of a spectrum. """
    return np.mean(spectrum[:, -1], axis=0)


def trial_meanpower(data, sample_rate, band):
    """ Calculate the mean power of a trial. """
    f = fourrier(data, sample_rate)
    b = bandpass(f, band)
    return spectrum_meanpower(b)


def experiment(c1, c2, sample_rate, band):
    results = [[], []]
    for trial in c1:
        results[0].append(trial_meanpower(trial, sample_rate, band))
    for trial in c2:
        results[1].append(trial_meanpower(trial, sample_rate, band))
    return results


def load_eeg_mat(path, label='data'):
    """ Load the eeg data into a numpy 2D matrix where
        the shape is (#trials, #datapoints)"""
    # Load matrix (# datapoints, # channels,  # tests)
    mat = loadmat(path)[label]
    mat = np.transpose(mat)
    # Remove redundant channel dimension
    mat = mat[:, 0, :]
    return mat

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize eeg readings using \
    python scatterplots. The script uses folders as a representation of \
    conditions. Every folder must contain two channels, c1.mat and c2.mat. ')
    # Specify folder
    parser.add_argument('-f', '--folder', nargs='+', help='Select folders to \
    compare. Each folder must contain both a c1.mat and \
    c2.mat.', required=True)
    # Specify sample rate
    parser.add_argument('-s', '--sample_rate', help='Specify the sample rate \
    of the measurement', default=256)
    # Specify frequency range
    parser.add_argument('-b', '--band', nargs=2, type=int, help="Specify the \
    frequency band in Hz, for example \'--band 8 13\'", default=[8, 13])
    args = parser.parse_args()
    
    folders = args.folder
    band = args.band
    sample_rate = args.sample_rate

    xmin = 1
    ymin = 1
    xmax = 0
    ymax = 0
    plots = []
    for folder in folders:
        p1 = os.path.join(folder, 'c1.mat')
        p2 = os.path.join(folder, 'c2.mat')
        if not os.path.isfile(p1) or not os.path.isfile(p2):
            print("Error: c1.mat and c2.mat could not be found in the" +
                  "specified folders.  Please check if the directories and " +
                  "files are present.")
            exit()
        c1 = load_eeg_mat(p1)
        c2 = load_eeg_mat(p2)
        results = experiment(c1, c2, sample_rate, band)
        xmin = min(results[0] + [xmin])
        xmax = max(results[0] + [xmax])
        ymin = min(results[1] + [ymin])
        ymax = max(results[1] + [ymax])
        plots.append(pyplot.scatter(results[0], results[1]))
    # Use the name of the folder as legend entry
    pyplot.legend(plots, [folder.split("/")[-1] for folder in folders])

    axes = pyplot.gca()
    axes.set_xlim((xmin, xmax))
    axes.set_ylim((ymin, ymax))
    pyplot.show()
    exit()
