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
    '''
    Creates an array of ones and zeros of length length. The width of the steps are determined by size.
    This is a 50% duty cycle waveform. 
    
    Parameters
    ----------
    size : int
        Width of the steps in the waveform. Default is 1. Maybe be set to the freq. multiplier if 
        downconverting the frequency.
    length : int
        Length of the waveform. Default is 64. The minimum for a dpg11 waveform is 64, and things must be modulo 64,
        so ensure that it is modulo 64 if working with the dpg11.
        
    Returns
    -------
    arr : np.ndarray
        Array of ones and zeros of length length.
    '''
    # returns an array of ones-zeros, of the specified length. Step size is determined from size
    arr = np.array([int(np.ceil((i + 1) / size) % 2) for i in range(length)])
    return arr

# Create function to get the multiplier to downconvert to the DPG11 clock frequency
def downconvert_clock_frequency(clock_frequency: float or int,
                                min_sample_rate: int or int = 25e6) -> (int, int):
    """
    Emulate the clock frequency of the DPG11. It will determine an integer multiplier (frequency_multiplier) to
    multiply the desired frequency (clock_frequency) by to get the sample rate above the minimum limit of the
    DPG11 (min_sample_rate). Each waveform will then have to be multiplied by this frequency_multiplier to
    downconvert the frequency to the desired frequency.
    
    clock_frequency = sample_rate / frequency_multiplier
    
    Parameters
    ----------
    clock_frequency : float | int
        Desired frequency of clock output in Hz.
    min_sample_rate : float
        Minimum sample rate of the device. Default is 25e6.
    sample_rate : float
        Sample rate of the DAQ card in Hz. Default is 1e9.
        
    Returns
    -------
    sample_rate : float
        Sample rate to set the DPG11 to in order to downconvert the frequency.
    frequency_multiplier : int
        Multiplier to downconvert the frequency.
        
    Examples
    --------
    >>> downconvert_clock_frequency(2.5e6)
    (25e6, 10)
    """
    
    # Determine the frequency multiplier
    frequency_multiplier = int(np.ceil(min_sample_rate / clock_frequency))
    
    # Determine the sample rate
    sample_rate = int(clock_frequency * frequency_multiplier)
    
    return sample_rate, frequency_multiplier

# create function to check if a pulse width if mod 64 given the sample rate
# then give the mod 64 duration. If not, give the closest duration. 
def length_mod_64(pulse_width: int,
                  sample_rate: int) -> (int, float):
    """
    Check if the duration of a segment is modulo 64 in samples given the sample rate.
    
    Parameters
    ----------
    pulse_width : int
        Pulse width in seconds to check if modulo 64 given the sample rate
    sample_rate : int
        Sample rate of the device.
        
    Returns
    -------
    num_samples_64 : int
        Number of samples that is modulo 64
    new_duration : float
        New duration of the segment in seconds that is mod 64
    """
    # get the number of samples from the pulse duration
    num_samples = pulse_width * sample_rate
    # Make the number of samples to be modulo
    num_samples_64 = int(np.ceil(num_samples/64)*64)
    # and change the pulse width to match
    duration_64 = num_samples/sample_rate

    
    return num_samples_64, duration_64

# Define function to pad a given waveform (with either 1s or 0s) to a given length (on the right or left)
def pad_waveform(waveform: np.ndarray or list,
                 length: int,
                 pad_value: int = 0,
                 pad_side: str = 'right') -> np.ndarray:
    """
    Pad a waveform with either 1s or 0s to a given length. 
    
    Parameters
    ----------
    waveform : np.ndarray
        Waveform to pad.
    length : int
        Length to pad the waveform to.
    pad_value : int
        Value to pad the waveform with. Default is 0.
    pad_side : str
        Side to pad the waveform on. Default is 'right'.
        
    Returns
    -------
    waveform : np.ndarray
        Padded waveform.
    """
    # Determine the length of the waveform
    waveform_length = len(waveform)
    
    # Determine the number of samples to pad
    num_samples_to_pad = length - waveform_length
    
    # Raise error if wrong pad value
    if pad_value not in [0, 1]:
        raise ValueError('pad_value must be either 0 or 1')
    
    # Pad the waveform
    if pad_side == 'right':
        waveform = np.pad(waveform, (pad_value, num_samples_to_pad), constant_values=pad_value).astype(int)
    elif pad_side == 'left':
        waveform = np.pad(waveform, (num_samples_to_pad, pad_value), constant_values=pad_value).astype(int)
    else:
        raise ValueError('pad_side must be either "right" or "left"')
    
    return waveform

# Function to convert a decimal number to an 11 bit binary array (for the dpg11)
def dec2bin_array(dec_num: int) -> np.ndarray:
    """
    Convert a decimal number to an 11 bit binary array (for the dpg11). Left is the least significant bit.
    
    Parameters
    ----------
    dec_num : int
        Decimal number to convert to binary.
        
    Returns
    -------
    bin_array : np.ndarray
        Binary array of length 11.
    """
    # Convert the decimal number to binary
    bin_num = bin(int(dec_num))[2:]
    
    
    # Convert the binary number to an array
    bin_array = [int(i) for i in bin(dec_num)[2:].zfill(11)]
    bin_array.reverse()
    
    return np.array(bin_array)

# Function to fully convert a wavefile to a list of arrays with each entry being a channel
def wavefile2arrays(wavefile: str) -> list or np.ndarray:
    """
    Convert a wavefile to a list of arrays with each entry being a channel. ie wavefile_arrays[0] is channel 1.
    
    Parameters
    ----------
    wavefile : str
        Path to the wavefile to convert.
        
    Returns
    -------
    wavefile_arrays : list | np.ndarray
        List of arrays with each entry being a channel.
    """
    # Open the wavefile
    dec_waveforms = np.loadtxt(wavefile).astype(int)
        
    # Convert each decimal waveform to binary
    bin_waveforms = np.array([dec2bin_array(i) for i in dec_waveforms])
    # Transpose the data
    waveforms_arr = bin_waveforms.T
    
    return waveforms_arr