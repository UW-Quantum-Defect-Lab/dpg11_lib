# Module for functions that are helpful when coding
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator, AutoLocator
# import the local libraries
from dpg11_pylib.visualization.colors import get_color, get_color_list

# Define function to find the longest length of a waveform when accounting for different x_starts
def find_longest_waveform(waveforms: list,
                          x_starts: list = None) -> int:
    # TODO: Add the docstrings
    # Add the docstrings
    """
    Find the longest waveform in a list of waveforms.
    
    Parameters
    ----------
    waveforms : list
        List of waveforms to find the longest length of.
    x_starts : list, optional
        List of x_starts for each waveform. Default is None.
        
    Returns
    -------
    int
        Length of the longest waveform.
    """
    
    # Check if the x_starts is None
    if x_starts == None:
        # return the length of the longest waveform
        return max([len(wave) for wave in waveforms])
    # Check if the x_starts is a list
    elif isinstance(x_starts, (list, np.ndarray)):
        # Check if the length of the x_starts is the same as the length of the waveforms
        if len(x_starts) != len(waveforms):
            raise ValueError("Length of x_starts not equal to length of waveforms array!")
        else:
            # return the length of the longest waveform
            return max([(len(wave) + x_starts[i]) for i, wave in enumerate(waveforms)])

"""
I want to create a function to visualize waveforms here, both np arrays and dpg11 waveforms
For the DPG11 waveforms, have the option to visualize the outputs on multiple channels, which is an option.
I will need to write more functions to do this. First, I will create the option to visualize the 
standard numpy arrays.
"""

# Function to visualize waveforms
#TODO: Figure out the right way to name this, is it a camel case situation?
#TODO: Create a function to get the start value
#TODO: Add the ability to deal with only one waveform and label and what not
#TODO: Add the docstrings
def plot_waveforms(waveforms: list,
                   labels: list,
                   x_starts = None,
                   grid_spacing: list = [8, 2],
                   figure_width: int or float = 10):
    # add the docstrings
    # TODO: Add these docstrings
    # Create the color schemes
    # TODO: replace this with a predefined color scheme in the colors library
    # TODO: fix if the colors arr is shorter than the
    colors = ['cyan', 'orange', 'lime', 'violet', 'pink', 'red']
    # Create a colors array
    main_colors = get_color_list(colors, shade=5)
    fill_colors = get_color_list(colors, shade=3)
    
    # Define number of waveforms
    num_waves = len(waveforms)
    # Find the max x-value
    max_x = find_longest_waveform(waveforms, x_starts)
    # Create the x_arrays if they don't already exist
    if x_starts == None:
        # Rename x_starts to be all zeros
        x_starts = np.zeros(num_waves)
    # Create the x_arr from the x_starts
    if isinstance(x_starts, (list, np.ndarray)):
        if len(x_starts) != num_waves:
            raise ValueError("Length of x_starts not equal to length of waveforms array!")
        else:
            # create the x_arrays
            x_arrays = [np.arange(x_starts[i], len(wave) + x_starts[i]) for i, wave in enumerate(waveforms)]
            # print(x_arrays)
    # Throw an error if none of these worked
    else:
        raise ValueError("Improper format for x_starts array, provide list or numpy array")
        
    
    
    # Create the figure where the height is determined by the number of waveforms
    fig = plt.figure(figsize=(figure_width, num_waves))
    # Now create the gridspec that we will use
    gs = gridspec.GridSpec(num_waves, 1, height_ratios=np.ones(num_waves))
    
    # Now loop over and plot everything
    for i, wav in enumerate(waveforms):
        # get the axis
        ax = fig.add_subplot(gs[i])
        # plot the waveform and fill the underneath
        ax.step(x_arrays[i], wav, color=main_colors[i], ls='-', where='post')
        ax.fill_between(x_arrays[i], wav, color=fill_colors[i], alpha=.5, step='post')
        
        # Format the axes
        # Add the label to the y-axis
        ax.set_ylabel(labels[i])
        # remove the x-axis for all but the last entry
        if i != (num_waves-1):
            ax.set_xticklabels([])
        # Get rid of y-axis tick labels
        ax.set_yticklabels([])
        ax.tick_params('y', left=False)
        
        # Now add the grids
        # For the major grid spacing
        ax.xaxis.set_major_locator(MultipleLocator(grid_spacing[0]))
        # For the minor grid spacing
        ax.xaxis.set_minor_locator(MultipleLocator(grid_spacing[1]))
        ax.grid(which='major', axis='x')
        ax.grid(which='minor', axis='x', alpha=0.4, ls='--')
        
        # Set the limits
        ax.set_ylim([0, 1.1])
        # Setting the x limits to show all waveforms even if they are different lengths
        ax.set_xlim([min(x_starts), max_x])
        
        
    # return 
    return
        
    
    