#TODO: Delete this file once the new version is working properly
# This is the old library that I had created. I will delete this library once I have added everything over

# TODO: Update the info for when this file was created
# 2021-07-06 / last updated on
# This code was made for use in the Fu lab
# by Ethan Hansen

import os
import shutil
import subprocess
import time

import numpy as np

import inspect

# from qt3utils.pulsers import qcsapphire, pulseblaster
# from qt3utils.experiments import cwodmr


# TODO: Get the class updated to work with the script method
# TODO: Add proper docstrings for all of the functions, update the error calling using that new function
# TODO: Organize the workspace

# TODO: Remove all of the verbose from the functions
# TODO: Update all of the docstrings
# DPG11 class for controlling the DPG11 using the script method
class DPG11Device:
    """
    This class contains all of the functions required for communicating with the WavePond DPG11 data
    generators untilizing the script method. 
    """

    # Hardware limited options
    internal_clock_rate_limits_in_hz = [50e6, 2.5e9]
    device_output_channels = [i for i in range(1, 12)]
    memory_limits = [48, 8e6]
    loops_limits = [0, 2 ** 16 - 2]
    pad_limits = [0, 2 ** 12 - 1]
    sequence_limit = 60

    clock_rate = 0  # This is a placeholder that will update once you set the clock frequency

    def __init__(self,
                 driver_path: str,
                 card_number: int = 1,
                 open_api_on_initialization: bool = True,
                 clock_rate=None):
        """
        Initialize DPG11 script method library for controlling the DPG11. This script method is functional but does not return
        the outputs of each command. This is not ideal for troubleshooting or reading out the actual clock frequency of the DPG11
        after setting it, but the dll library provided does not work properly and more time needs to be spent on it. One way to check
        the set frequency is to set it in the actual GUI and read out what it was set to. Acording to WavePond, this should be the same
        as the set value when you use the code.
        In order for the library to work, the GUI.exe file as long as the two .bat files must be in the same folder as the script for now.
        Future changes will include sorting the .txt wavefiles into folders as well as the saved scripts.

        Parameters
        ----------
        # TODO: Add the docstring for the driver path function
        card_number : int
            The DG card number that you wish to control. This is only relevant when using two or more WavePond DG devices, by default 1
        open_api_on_initialization : bool, optional
            If set to True, the .bat will be run to open the api. If False, the API will not be opened and must be 
            opened with open_api() before calling any functions to execute scripts, by default True
        clock_rate
            If not set to None, the clock rate of the data generator will be set to the input value.
        """
        
        # Remove this later, just so the class works for now
        self.verbose = 3
        
        # init the driver path
        self.directory = driver_path
        # check that the driver is in the path provided
        if not os.path.exists(os.path.join(self.directory, 'dax22000_GUI_64.exe')):
            raise ValueError('No driver was found in the path provided. Please input a valid path.')
        # save the scripts, wavefiles, and multi-wavefiles paths
        self.scripts_path = os.path.join(self.directory, 'scripts')
        self.wavefiles_path = os.path.join(self.directory, 'wavefiles')
        self.multi_wavefiles_path = os.path.join(self.directory, 'multi_wavefiles')
        # create the script, wave, and multi-wave folders if they don't exist
        try:
            if not os.path.exists(self.scripts_path):
                os.makedirs(self.scripts_path)
            if not os.path.exists(self.wavefiles_path):
                os.makedirs(self.wavefiles_path)
            if not os.path.exists(self.multi_wavefiles_path):
                os.makedirs(self.multi_wavefiles_path)
        except:
            raise ValueError('The driver path is not valid or there was an issue. Please input a valid path.')
            
        

        # Check for TypeErrors
        annotations = inspect.getfullargspec(self.__init__).annotations
        for i in annotations.keys():
            if type(locals()[i]) != annotations[i]:
                raise TypeError(
                    f'{i} must be of type {annotations[i]} (Received input of type {type(locals()[i])})')

        self.card_number = card_number
        self.open_api_bat = 'Script_API_Test\\dpg11_open_api'
        self.close_api_bat = 'Script_API_Test\\dpg11_close_api'

        # TODO: Add all of the errors for the init inputs

        if open_api_on_initialization:
            # Open batch file to start up the API. The batchfile must be in the same directory 
            self.open_api()

        if clock_rate != None:
            self.set_clk_rate(clock_rate=clock_rate,
                              execute=True)

    def open_api(self):
        """
        Opens the batch file to start up the API.
        \n self.open_api_bat must be the correct name and in the correct location.
        """
        subprocess.call([r'{0}\\{1}.bat'.format(self.directory, self.open_api_bat)])

        print('API Opened')

    def close_api(self):
        """
        Opens the batch file to close the API and kill the .exe.
        \n self.close_api_bat must be the correct name and in the correct location.
        """
        subprocess.call([r'{0}\\{1}.bat'.format(self.directory, self.close_api_bat)])

        print('API Closed')

    def create_script(self,
                      command_list: list,
                      script_name: str = 'temp_script',
                      execute_after_creation: bool = False,
                      overwrite_script: bool = True,
                      save_script: bool = False):
        """
        This function will take in a list of DPG11 functions defined here and format them (in order) into a script for the API to execute.
        Returns the .txt filename of the script, so you can input this function directly into the execute_script function as the script_txt parameter.
        Remember that if the script_name is left as 'temp_script', it will be deleted after execution.
        
        Parameters
        ----------
        command_list : list
            list of commands to be executed by the script. 
            Only the functions from this class that return a str can be input into the command_arr.
        script_name : str, optional
            What to name the script .txt file. Exclude the .txt in the name. 
            If left as the default 'temp_script', then the script file will be deleted at execution, by default 'temp_script'
        execute_after_creation : bool, optional
            If set to true, then the script will be executed immediately after it was created, by default False
        overwrite_script: bool, optional
            If True, then the system will overwrite any existing script with the same file name, by default False
        save_script: bool, optional
            If True, then the script will be saved after execution. Only used if execute_after_creation is used
        
            
        Returns
        -------
        str or int
            Returns the .txt filename str of the script if execute_after_script = False or if execute_after_script = True and save_script = True.
            Returns 0 if execute_after_script = True and save_script = False
        
        Allowable Functions in command_list
        -----------------------------------
        run() \n
        stop() \n
        set_clk_rate() \n
        create_single_segment() \n
        create_multi_segments() \n
        pwr_dwn()
        """
        # TODO: Update the allowable functions list

        # Save script text file local path
        script_path = self.scripts_path + f'/{script_name}.txt'

        if self.verbose > 2:
            print(command_list)
            print('\nscript_path: ' + script_path)

        # Check for TypeErrors
        annotations = inspect.getfullargspec(self.create_script).annotations
        for i in annotations.keys():
            if type(locals()[i]) != annotations[i]:
                raise TypeError(
                    f'{i} must be of type {annotations[i]} (Received input of type {type(locals()[i])})')

        # TODO: Add print-outs for whether the scripts will be deleted or saved or whatever. Also printed after the execution

        # Ensure that all elements in command_list
        if not all(isinstance(elem, str) for elem in command_list):
            raise TypeError(
                'Not all entries in command_list are of type str. Make sure that you are calling only the allowable functions'
            )

        # Ensure proper name
        if ' ' in script_name:
            raise ValueError(
                f'script_name cannot include any spaces (recieved {script_name}'
            )

        # Ensure that we don't save temporary file names for orginization purposes    
        if save_script and script_name == 'temp_script':
            raise ValueError(
                'save_script set to True but received a temporary file name. Please give the script a filename'
            )

        # Check if script_name already exists
        if not overwrite_script and os.path.isfile(path=script_path):
            if script_name == 'temp_script':
                return ValueError(
                    'Previous temporary file with name temp_script was not properly deleted. Please delete this file'
                )
            else:
                return ValueError(
                    'overwrite_script is set to False but script_name already exists. Change script_name or set overwrite_script to True'
                )

        # Format command list for input into .txt file
        script_str = "\n".join(command_list)

        if self.verbose > 2:
            print('script_str: ' + script_str)

        # create the script name
        # Create the file, write the script into it, and save it
        f = open(script_path, "w")
        f.write(script_str)
        f.close()

        # Execute script if true
        if execute_after_creation:
            return self.execute_script(script_txt=script_path, save_script=save_script)
        else:
            if self.verbose > 1:
                print('Script saved as ' + script_path + ' and not executed')
            return script_path

    def execute_script(self,
                       script_txt: str,
                       save_script: bool = True):
        """
        This function copies an existing script for the DPG11 to run over to the dax_cmd.txt file to be executed by the API

        Parameters
        ----------
        script_txt : str
            Full name of the .txt file containing your script
        save_script : bool, optional
            If False, then the script_txt will be deleted after it is executed by the API, by default True
        """
        # Type Errors
        if not isinstance(script_txt, str):
            raise TypeError(
                f'script_txt must be of type str (recevied input of type {type(script_txt)})'
            )

        if not isinstance(save_script, bool):
            raise TypeError(
                f'save_script must be of type bool (recevied input of type {type(save_script)})'
            )

        if len(script_txt.split('.')) != 2:
            raise ValueError(
                'Invalid filename for script_txt'
            )

        if script_txt.split('.')[1] != 'txt':
            raise ValueError(
                f'script_txt must be a .txt file (Recieved {script_txt.split(".")[1]})'
            )

        # Directory Paths
        temp_path = os.path.join(self.directory, script_txt)
        execute_path = os.path.join(self.directory, "dax_cmd.txt")

        if self.verbose > 3:
            print('Script path: ' + temp_path)
            print('Execution path: ' + execute_path)

        # Save or delete the script
        if save_script:
            # Rename file to dax_cmd.txt
            shutil.copyfile(src=temp_path, dst=execute_path)
            if self.verbose > 1:
                print('Script saved as ' + script_txt)
            return script_txt
        else:
            shutil.move(temp_path, execute_path)
            if self.verbose > 1:
                print('Script deleted')
            return 0

    # Function to stop the output
    def stop_ouput(self):
        """
        Sends a command to the API to stop the output of the DPG11
        """
        # Stop the output
        self.create_script([self.stop()],
                           execute_after_creation=True,
                           )

        if self.verbose > 3:
            print('Data Generator output stopped')

    # Function to stop the output and set the clock rate
    def stop_ouput_set_clk(self,
                           clock_rate: float,
                           ):
        """
        Sends a command to the API to stop the output of the DPG11 and set the clock rate
        """
        # Stop the output
        self.create_script([self.stop(),
                            self.set_clk_rate(clock_rate=clock_rate)],
                           execute_after_creation=True,
                           )

        if self.verbose > 3:
            print(f'Data Generator output stopped and clock rate set to {self.get_clock_rate()}')

    # Function to completely shut down the device   
    def shut_down(self):
        """
        Stops the output of the DPG11, powers it down, and closes the API.
        """
        # Stop the output
        self.create_script([self.stop(),
                            self.pwr_dwn()],
                           execute_after_creation=True,
                           )
        time.sleep(2)
        self.close_api()

        if self.verbose > 2:
            print('DPG11 was powered down and the API was closed')

    # Small little function to get the number of points from the filename
    def get_data_from_fn(self,
                         filename: str):
        """
        Simple function to extract the data from single and multi-wave .txt files. 
        The .txt files should be of the form [filename_data.txt], where data is the data we wish to extract.
        For single wave files, the data will be the number of points. For the multi-wave files, it will be the total 
        number of wave files.

        Parameters
        ----------
        filename : str
            The .txt filename that we wish to extract data from. Must be a str and of the form filename_data.txt.

        Returns
        -------
        int
            Data extracted from the filename
        """
        # Check for type errors
        if not isinstance(filename, str):
            raise TypeError(
                f'script_txt must be of type str (received input of type {type(filename)})'
            )

        if len(filename.split('.')) != 2:
            raise ValueError(
                'Invalid filename for script_txt'
            )

        if filename.split('.')[1] != 'txt':
            raise ValueError(
                f'script_txt must be a .txt file (Recieved {filename.split(".")[1]})'
            )

        fn_data = int(filename.split('.')[0].split('_')[-1])

        if self.verbose > 3:
            print(fn_data)
        return fn_data

    # For creating the wave files
    def bin_array_to_decimal(self,
                             bin_arr: None):
        return int(''.join(str(bit) for bit in bin_arr), 2)
    
    def create_decimal_array(self,
                             stack_arr):
        return np.apply_along_axis(self.bin_array_to_decimal, 1, stack_arr)

    #FIXME: Update this to match with the new form for sending wave signals!
    def create_wave_file(self,
                         wave_name: str,
                         wave_dict: dict):
        """
        This functions creates a .txt wavefile from a waveform array in the proper format to be used by the API.

        Parameters
        ----------
        wave_name : str
            What to name the wavefile. Do not include .txt. The final file name will be wave_name_{num_points}.txt
        wave_dict : dict
            Waveform array dictionary of the form {1: 'path for channel 1 array',
                                                   3: 'path for channel 3 array'}
            and so on and so forth, where channel 1 array is the array of 1's and 0 of whether the channel is on or off.
            Note that you do not need to fill any of the off channels.

        Returns
        -------
        str
            Name of the saved wavefile
        """

        num_points = len(wave_dict[list(wave_dict.keys())[0]])
        
        # print('Number of Points: ', num_points)
        # Eventual name for the wave file to be saved as
        # TODO: Fix this, really work on the naming convention, I don't like how I did it
        wave_filename = f'wavefiles/{wave_name}_{num_points}.txt'
        wave_filepath = self.directory + '/' + wave_filename
        # Creating the null array of zeros to be filled to off channels
        null_array = np.zeros(num_points, dtype=int)
        
        # Stacked matrix with each column array with the binary of which channel should be on each cycle
        stacked_arr = np.stack([wave_dict[num] if num in wave_dict.keys() else null_array for num in range(16, 0, -1)], axis=1)
        
        decimal_arr = self.create_decimal_array(stacked_arr)
        
        # Check for correct inputs
        # annotations = inspect.getfullargspec(self.create_wave_file).annotations
        # for i in annotations.keys():
        #     if type(locals()[i]) != annotations[i]:
        #         raise TypeError(
        #             f'{i} must be of type {annotations[i]} (Received input of type {type(locals()[i])})')

        # Check if the name is correct
        if ' ' in wave_name:
            raise ValueError(
                'wave_name cannot include any spaces (Recieved ' + wave_name
            )

        if num_points % 64 != 0:
            raise ValueError('Length of waveform_array must be modulo 64')
        # Open/create the file. Length of the waveform will be in the file name
        temp = open(wave_filepath, 'w')

        # Add waveform array to the new file
        for i, point in enumerate(decimal_arr):
            if i + 1 < len(decimal_arr):
                temp.write("%d\n" % point)
            else:
                temp.write(str(point))

        # Close the new file
        temp.close()
        
        return wave_filename

    # Function to create the .txt file that includes the individual waveforms for the create_segments function
    #FIXME: Change the documentation for this!!!
    def create_multi_wave_file(self,
                               name: str,
                               filename_arr,
                               num_loops_arr,
                               triggered_arr
                               ):
        """
        This function creates the txt file of the format to send multi-wave segments to be used by the create_multi_segments function.

        Parameters
        ----------
        name : str
            What to name multi-wave file. Do not include the .txt. The final filename should be of the form name_{num_waves}.txt
        waves_df : pd.DataFrame
            Dataframe with the multi-wave information. It should have the keys ['filenames', 'num_loops', 'triggered'].

        Returns
        -------
        str
            The filename of the multi-wave txt file that is saved.
        """
        # Check input types
        annotations = inspect.getfullargspec(self.create_multi_wave_file).annotations
        for i in annotations.keys():
            if type(locals()[i]) != annotations[i]:
                raise TypeError(
                    f'{i} must be of type {annotations[i]} (Received input of type {type(locals()[i])})')

        # Get the number of segments to be saved in the filename, and initialize string list
        num_waves = len(filename_arr)
        if self.verbose > 1:
            print('Number of waveforms in wavefile: ' + str(num_waves))

        str_list = []

        # Organize all of the data from the dataframe
        num_points = [self.get_data_from_fn(filename=name) for name in filename_arr]

        if self.verbose > 2:
            print('filenames array: ' + str(filename_arr))
            print('num_points array: ' + str(num_points))
            print('num_loops array: ' + str(num_loops_arr))
            print('triggered array: ' + str(triggered_arr))

        # Format the filename for how it should be saved, where the number is the number of waves in the multi_wave_file
        filename = f'multi_wavefiles/{name}_{num_waves}.txt'
        full_path = self.directory + '/' + filename

        if self.verbose > 1:
            print('Multi-wave filename: ' + filename)

        # Populate the str_list with the entry for each waveform in the dataframe
        for i in range(num_waves):
            str_list.append(f'{filename_arr[i]} {num_points[i]} {num_loops_arr[i]} {triggered_arr[i]}')

        # Convert all of the strings into a single str to be output directly as a text file   
        str_to_write = "\n".join(str_list)

        if self.verbose > 1:
            print('String to write to text file: ' + str_to_write)

        # Create and write to the file
        f = open(full_path, "w")
        f.write(str_to_write)
        f.close()

        return filename

    # TODO: Add all of the type errors and what not for all of these functions and the docstrings
    # All of the functions to be sent to the DPG11 that will output strings for our case
    # Function to run the waveforms 
    def run(self,
            soft_trig: bool = True,
            execute: bool = False):
        """
        Function that will output the string required for the .txt script to run saved waves on a channel

        Parameters
        ----------
        soft_trig : bool, optional
            If True, the DPG11 will send a software trigger to start the saved waveforms, by default True
        execute: bool, optional
            If true, creates an executes a single-line script with just this function, by default False

        Returns
        -------
        str
            Run command string
        """
        # Check for input type errors
        annotations = inspect.getfullargspec(self.run).annotations
        for i in annotations.keys():
            if type(locals()[i]) != annotations[i]:
                raise TypeError(
                    f'{i} must be of type {annotations[i]} (Received input of type {type(locals()[i])})')

                # make bool lower
        soft_trig_lower = str(soft_trig).lower()
        func_str = f'Run {self.card_number} {soft_trig_lower}'

        if execute:
            return self.create_script(command_list=[func_str],
                                      script_name='temp_run',
                                      execute_after_creation=True,
                                      overwrite_script=True,
                                      save_script=False)
        else:
            return func_str

    # Function to stop running the waveforms
    def stop(self,
             execute: bool = False):
        """
        Function to output the Stop command string
        
        Parameters
        ----------
        execute: bool, optional
            If true, creates an executes a single-line script with just this function, by default False

        Returns
        -------
        str
            Stop command string
        """
        func_str = f'Stop {self.card_number}'

        # For running executing a single-line script when execute set to True
        if execute:
            return self.create_script(command_list=[func_str],
                                      script_name='temp_stop',
                                      execute_after_creation=True,
                                      overwrite_script=True,
                                      save_script=False)
        else:
            return func_str

    # Function to set the clock frequency
    def set_clk_rate(self,
                     clock_rate: float,
                     execute: bool = False):
        """
        Function that will output the set_clk_rate command string to be input into the command_list parameter of create_script()

        Parameters
        ----------
        clock_rate : float
            What to set the clock rate of the DPG11 as. Must be between 50 MHz and 2.5 GHz
        execute: bool, optional
            If true, creates an executes a single-line script with just this function, by default False

        Returns
        -------
        str
            SetClkRate command string
        """
        # Check for input type errors     
        annotations = inspect.getfullargspec(self.set_clk_rate).annotations
        for i in annotations.keys():
            if type(locals()[i]) != annotations[i]:
                raise TypeError(
                    f'{i} must be of type {annotations[i]} (Received input of type {type(locals()[i])})')

                # Check range of set frequency
        if not (self.internal_clock_rate_limits_in_hz[0] <= clock_rate <=
                self.internal_clock_rate_limits_in_hz[1]):
            raise ValueError('Data Generator internal frequency input should be between 25e6 Hz and 2.5e9 Hz')

        func_str = f'SetClkRate {self.card_number} {clock_rate}'

        # Update the clock frequency variable
        self.clock_rate = clock_rate

        # For running executing a single-line script when execute set to True
        if execute:
            return self.create_script(command_list=[func_str],
                                      script_name='temp_set_clk_rate',
                                      execute_after_creation=True,
                                      overwrite_script=True,
                                      save_script=False)
        else:
            return func_str

    def select_trigger(self,
                       trigger: bool = False,
                       execute: bool = False):

        func_str = f'SelExtTrig {self.card_number} {str(trigger).lower()}'

        if execute:
            return self.create_script(command_list=[func_str],
                                      script_name='temp_sel_ext_trig',
                                      execute_after_creation=True,
                                      overwrite_script=True,
                                      save_script=False)
        else:
            return func_str

    # Function to create a single segment
    def create_single_segment(self,
                              wave_filename: str,
                              channel_num: int = 1,
                              num_loops: int = 0,
                              pad_begin: int = 2047,
                              pad_end: int = 2047,
                              triggered: int = 1,
                              execute: bool = False):
        """
        Function to output the CreateSingleSegment command string

        Parameters
        ----------
        wave_filename : str
            name of the .txt wavefile that you wish to create a segment out of
        channel_num : int, optional
            CHANNEL NUMBER WILL ALWAYS BE 1 FOR THE DPG11, 
            DIFFERENT CHANNELS ARE TRIGGERED VIA CREATING THE WAVE FILE, by default 1
        num_loops: int
            The number of loops to run. Max number of loops is 65,534. Set to 0 for continuous looping
        pad_begin: int
            Vertical value that the waveform will begin at. Memory is between 0 and 4,095, which goes from 0V to 2V 
        pad_end: int
            Vertical value that the waveform will end at. Memory is between 0 and 4,095, which goes from 0V to 2
        triggered: int
            0 => Waveform starts up first time but cannot be triggered later without shutting down first. 
            1 => Allows waveform to be triggered more than once while running.
        execute: bool, optional
            If true, creates an executes a single-line script with just this function, by default False

        Returns
        -------
        str
            CreateSingleSegment command string
        """
        # Get the number of points from the file name
        num_points = self.get_data_from_fn(wave_filename)

        # Check input types
        annotations = inspect.getfullargspec(self.create_single_segment).annotations
        for i in annotations.keys():
            if type(locals()[i]) != annotations[i]:
                raise TypeError(
                    f'{i} must be of type {annotations[i]} (Received input of type {type(locals()[i])})')

        # Check fto ensure we input a .txt file
        if wave_filename.split('.')[-1] != 'txt':
            raise ValueError(
                f'script_txt must be a .txt file (Recieved {wave_filename.split(".")[-1]})'
            )

        # Check input range errors
        if channel_num not in self.device_output_channels:
            raise ValueError('Output channel number is not in range (1 - 11)')

        if self.pad_limits[0] > pad_begin > self.pad_limits[1]:
            raise ValueError('pad_begin is out of range (0 - 4095')

        if self.pad_limits[0] > pad_end > self.pad_limits[1]:
            raise ValueError('pad_end is out of range (0 - 4095')

        if triggered not in [0, 1]:
            raise ValueError('triggered input must be 0 or 1')

        # The output string
        func_str = f'CreateSingleSegment {self.card_number} {channel_num} {num_points} {num_loops} {pad_begin} {pad_end} {wave_filename} {triggered}'

        # For running executing a single-line script when execute set to True
        if execute:
            return self.create_script(command_list=[func_str],
                                      script_name='temp_create_single_segment',
                                      execute_after_creation=True,
                                      overwrite_script=True,
                                      save_script=True)
        else:
            return func_str

    # Function to create multiple segments
    def create_multi_segments(self,
                              waves_filename: str,
                              channel_num: int = 1,
                              pad_begin: int = 2047,
                              pad_end: int = 2047,
                              loop: bool = False,
                              execute: bool = False):
        """
        Function to output the CreateSegments command string

        Parameters
        ----------
        waves_filename : str
            Name of the .txt wavefile that you wish to create a segment out of
        channel_num : int, optional
            CHANNEL NUMBER WILL ALWAYS BE 1 FOR THE DPG11,
            DIFFERENT CHANNELS ARE TRIGGERED VIA CREATING THE WAVE FILE, by default 1
        pad_begin: int
            Vertical value that the waveform will begin at. Memory is between 0 and 4,095, which goes from 0V to 2V 
        pad_end: int
            Vertical value that the waveform will end at. Memory is between 0 and 4,095, which goes from 0V to 2
        loop : bool, optional
            If true, then the full multi-segment will loop, by default False
        execute: bool, optional
            If true, creates an executes a single-line script with just this function, by default False

        Returns
        -------
        str
            CreateSegments command string
        """
        # Check input types
        annotations = inspect.getfullargspec(self.create_multi_segments).annotations
        for i in annotations.keys():
            if type(locals()[i]) != annotations[i]:
                raise TypeError(
                    f'{i} must be of type {annotations[i]} (Received input of type {type(locals()[i])})')

        # Check input range errors
        if channel_num not in self.device_output_channels:
            raise ValueError('Output channel number is not in range (1 - 11)')
        if self.pad_limits[0] > pad_begin > self.pad_limits[1]:
            raise ValueError('pad_begin is out of range (0 - 4095')

        if self.pad_limits[0] > pad_end > self.pad_limits[1]:
            raise ValueError('pad_end is out of range (0 - 4095')

        # Get the number of waves from the filename, and make the bool lowercase
        num_waves = self.get_data_from_fn(waves_filename)
        loop_lower = str(loop).lower()

        func_str = f'CreateSegments {self.card_number} {channel_num} {num_waves} {pad_begin} {pad_end} {waves_filename} {loop_lower}'

        # For running executing a single-line script when execute set to True
        if execute:
            return self.create_script(command_list=[func_str],
                                      script_name='temp_create_multi_segments',
                                      execute_after_creation=True,
                                      overwrite_script=True,
                                      save_script=True)
        else:
            return func_str

    # Function to power down
    def pwr_dwn(self,
                execute: bool = False):
        """
        Function to output the PWR_DWN command string

        Parameters
        ----------
        execute: bool, optional
            If true, creates an executes a single-line script with just this function, by default False
            
        Returns
        -------
        str
            PWR_DWN command string
        """
        func_str = f'PWR_DWN {self.card_number}'

        # For running executing a single-line script when execute set to True
        if execute:
            return self.create_script(command_list=[func_str],
                                      script_name='temp_pwr_down',
                                      execute_after_creation=True,
                                      overwrite_script=True,
                                      save_script=False)
        else:
            return func_str

    # Function to initialize
    def pwr_dwn(self,
                execute: bool = False):
        """
        Function to output the PWR_DWN command string

        Parameters
        ----------
        execute: bool, optional
            If true, creates an executes a single-line script with just this function, by default False

        Returns
        -------
        str
            PWR_DWN command string
        """
        func_str = f'PWR_DWN {self.card_number}'

        # For running executing a single-line script when execute set to True
        if execute:
            return self.create_script(command_list=[func_str],
                                      script_name='temp_pwr_down',
                                      execute_after_creation=True,
                                      overwrite_script=True,
                                      save_script=False)
        else:
            return func_str

    # Just for getting what the clock rate was last set to
    def get_clock_rate(self):
        return self.clock_rate

    # Function for creating and running a single wave
    def run_single_wave(self,
                        wave_filename: str,
                        clock_rate: float,
                        channel_num: int = 1,
                        num_loops: int = 0,
                        pad_begin: int = 2047,
                        pad_end: int = 2047,
                        triggered: int = 0,

                        save_script: bool = False,
                        script_name: str = 'temp_script',
                        overwrite_script: bool = True,

                        soft_trig: bool = True):
        """
        This function inputs a single wavefile str and desired clock rate, output channel, number of loops, pad, and triggering options,
        and autmatically creates a script and runs it after operation.

        Parameters
        ----------
        wave_filename : str
            [description]
        clock_rate : float
            [description]
        channel_num : int, optional
            [description], by default 1
        num_loops : int, optional
            [description], by default 0
        pad_begin : int, optional
            [description], by default 2047
        pad_end : int, optional
            [description], by default 2047
        triggered : int, optional
            [description], by default 0
        save_script : bool, optional
            [description], by default False
        script_name : str, optional
            [description], by default 'temp_script'
        overwrite_script : bool, optional
            [description], by default True
        soft_trig : bool, optional
            [description], by default True

        """
        # TODO: Update for all of the error raising eventually

        # Creation of the command_list
        command_list = [
            self.stop(),
            self.set_clk_rate(clock_rate=clock_rate),
            self.create_single_segment(wave_filename=wave_filename,
                                       channel_num=channel_num,
                                       num_loops=num_loops,
                                       pad_begin=pad_begin,
                                       pad_end=pad_end,
                                       triggered=triggered),
            self.run(soft_trig)
        ]

        # create and run the script
        return self.create_script(command_list=command_list,
                                  script_name=script_name,
                                  execute_after_creation=True,
                                  overwrite_script=overwrite_script,
                                  save_script=save_script)

    # Function for creating and running multiple segments
    def run_multi_wave(self,
                       waves_filename: str,
                       clock_rate: float,
                       channel_num: int = 1,
                       pad_begin: int = 2047,
                       pad_end: int = 2047,
                       loop: bool = False,

                       save_script: bool = False,
                       script_name: str = 'temp_script',
                       overwrite_script: bool = True,

                       soft_trig: bool = True):

        # Creation of the command_list
        command_list = [
            self.stop(),
            self.set_clk_rate(clock_rate=clock_rate),
            self.create_multi_segments(waves_filename=waves_filename,
                                       channel_num=channel_num,
                                       pad_begin=pad_begin,
                                       pad_end=pad_end,
                                       loop=loop),
            self.run(soft_trig)
        ]

        # create and run the script
        return self.create_script(command_list=command_list,
                                  script_name=script_name,
                                  execute_after_creation=True,
                                  overwrite_script=overwrite_script,
                                  save_script=save_script)

    

    # TODO: Fix these eventually 
    @staticmethod
    def join_pattern_arrays(pattern_list):
        if not (isinstance(pattern_list, np.ndarray) or isinstance(pattern_list, list)):
            raise TypeError('Pattern_list in not numpy.ndarray or list type')
        if not (np.all([isinstance(pattern, np.ndarray) for pattern in pattern_list]) or
                np.all([isinstance(pattern, list) for pattern in pattern_list])):
            raise TypeError('One or more patterns in pattern_list are of different type AND/OR'
                            ' not numpy.ndarray or list type.')

        # take an empty numpy.ndarray and append each pattern given in the pattern list, with index priority
        # (1st pattern is first in the final pattern, 2nd pattern is second in the final pattern etc.)
        final_pattern = np.array(np.concatenate(pattern_list, axis=0))

        return final_pattern

    # TODO: Fix these later, update them to have everything that we need 
    @staticmethod
    def repeat_pattern_array(pattern_array, repetitions):
        if not isinstance(pattern_array, np.ndarray) or not isinstance(pattern_array, list):
            raise TypeError('Pattern_array in not numpy.ndarray or list type')

        # similar to join_pattern_arrays, takes a zero numpy.ndarray & adds to it the given pattern 'repetitions' times
        final_pattern_array = np.array([])
        for j in range(repetitions):
            final_pattern_array = np.append(final_pattern_array, pattern_array)

        return final_pattern_array

    def generate_OFF_pattern_array(self, length=None):
        # returns an array of zeros, of the specified length
        pattern = np.zeros(length, dtype=int)
        return pattern

    def generate_ON_pattern_array(self, length=None):
        # returns an array of ones, of the specified length
        pattern = np.ones(length, dtype=int)
        return pattern

    def generate_OFF_ON_pattern_array(self, size=1, length=None):
        # returns an array of zeros-ones, of the specified length. Step size is determined from size
        pattern = np.array([int(np.ceil((i + 1 + size) / size) % 2) for i in range(length)])
        return pattern

    def generate_ON_OFF_pattern_array(self, size=1, length=None):
        # returns an array of ones-zeros, of the specified length. Step size is determined from size
        pattern = np.array([int(np.ceil((i + 1) / size) % 2) for i in range(length)])
        return pattern
