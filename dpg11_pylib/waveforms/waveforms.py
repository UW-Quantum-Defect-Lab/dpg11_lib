# Module for the creation of waveforms and other nice things like that
import numpy as np

# Create on off waveform that is a numpy array
#TODO: Fix these names, add the docstrings
def offOnArray(size=1, length=64):
    # returns an array of zeros-ones, of the specified length. Step size is determined from size
    arr = np.array([int(np.ceil((i + 1 + size) / size) % 2) for i in range(length)])
    return arr

#TODO: Fix the names of these functions
def onOffArray(size=1, length=64):
    # returns an array of ones-zeros, of the specified length. Step size is determined from size
    arr = np.array([int(np.ceil((i + 1) / size) % 2) for i in range(length)])
    return arr