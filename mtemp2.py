'''
Module for all the functions needed when processing M-Temp data. This is to be
used within the main.py processing code.

Last Updated: 10/16/2024
Author: Andrew McGallian

Ideas for further functions:
    - Something that generates a subset dataframe based on added columns
'''

# Imports

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import os as os
import io as io

# Configurations for Cart DAQ Set Ups

configs = {
    "Cart 1 Temp": {'AI0 (°C)': '1.8 ft (°C)',
                'AI1 (°C)': '5.4 ft (°C)',
                'AI2 (°C)': '0.6 ft (°C)',
                'AI3 (°C)': '3.6 ft (°C)',
                'AI4 (°C)': '7.2 ft (°C)',
                'AI5 (°C)': '9.0 ft (°C)',
                'AI6 (°C)': '3.6 ft b (°C)' ,
                'AI7 (°C)': '5.4 ft b (°C)'
                },

    "Cart 1 IR": {'AI0 (V)':'IR Raw (V)'},

    "Cart 2 Temp": {'AI2 (°C)': '1.8 ft (°C)',
                'AI1 (°C)': '0.6 ft (°C)',
                'AI3 (°C)': '3.6 ft (°C)',
                'AI4 (°C)': '3.6 ft b (°C)',
                'AI0 (°C)': '5.4 ft (°C)',
                'AI5 (°C)': '5.4 ft b (°C)',
                'AI6 (°C)': '7.2 ft (°C)' ,
                'AI7 (°C)': '9.0 ft (°C)'
                },

    "Cart 2 IR": {'AI0 (V)':'IR Raw (V)',
                  'AI1 (V)':'Raw RH 0.0ft',
                  'AI3 (V)':'Raw RH 1.8ft',
                  'AI2 (V)':'Raw RH 7.2ft',
                  'AI4 (V)':'Raw RH 9.0ft'}

}

# Functions

def load_excelsheet() -> dict[int, list[str | int]]:
    '''
    Loads the excel reference sheet and turns it into a dictionary. This
    function should be used first before loading any data since those functions
    will depend on that dictionary scheme for accessing file paths. The
    function should automatically find the excel file in the main directory
    the script is running in. This function should run on program start.

    Currently, the scheme should be as follows:
        - The key will be the test number (int), i.e., 1
        - The "value" will be a list with the associated excel sheet columns
        being:
            [folders, temperature data, ir/rh data, gps data, date,
            testing route, cart, set up, config]

    Inputs:
        None

    Returns:
        dict[int, list[str | int]]: Dictionary with a list of relevant
        information such as filepath, configuration, and more for each test
        name available in the excel spreadsheet.
    '''
    tests = {}

    current_directory = os.getcwd()
    filepath = os.path.join(current_directory, 'testlist.xlsx')

    try:
        df = pd.read_excel(filepath)

        for index, row in df.iterrows():
            test_number = int(row['Test Number'])
            test_info = [
                str(row['Test Folder']),
                str(row['Temperature Data']),
                str(row['IR/RH Data']),
                str(row['GPS Data']),
                row['Test Date'],
                row['Testing Route'],
                row['Cart'],
                row['Set Up'],
                str(row['Temperature Configuration']),
                str(row['IR/RH Configuration'])
            ]
            tests[test_number] = test_info

    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return {}
    except KeyError as e:
        print(f"Error: Missing expected column in the Excel sheet: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}

    return tests


def load_test(test_num: int, test_dict: dict[int, list[str|int]]
              ) -> tuple[str, str]:
    '''
    This function will load tests after the excel file has been loaded based on
    the test number. Will give back a tuple of the folder and filepath of the
    test.

    Inputs:
        test_num (int): The test number to identify the specific output folder
        test_dict (dict[int, list[str|int]]): The dictionary containing all the
        relevant test references.

    Returns:
        tuple[str, str]: The folder and filepath of the test.
    '''
    test_folder = "Test_Folders/" + test_dict[test_num][0]
    test_file = test_dict[test_num][1]
    return (test_folder, test_file)


def get_headers(folders: str, filename: str) -> dict[str, str]:
    '''
    Gets relevant metadata about the test file.

    Inputs:
        folders (str): Folder where file is.
        filename (str): Name of the file itself.

    Returns:
        dict[str, str]
    '''
    dheaders = {}
    with io.open(folders + filename, mode='r', encoding='UTF-8-sig') as csus:
      for i, row in enumerate(csus):
          if(i>5):
              pass
          else:
            row = row.replace('"', '')
            num1 = row.split(':', 1)[0].strip('"')
            num2 = row.split(':', 1)[1]
            num2 = num2.strip()
            num2 = num2.strip('\n')
            dheaders[num1] = num2

    dheaders["folders"] = folders
    dheaders["filename"] = filename
    return dheaders


def load_temp_daq(folder: str,
                  file: str,
                  headers: dict[str, str],
                  ) -> tuple[pd.DataFrame, str]:
    '''
    Cleans temperature DAQ data and turns it into a DataFrame. Uses the excel
    sheet to find the filepath based on the Test Folder and Temperature Data
    column.

    Inputs:
        test_num (int): The test number associated with the desired temperature
        data in the excel sheet.
        tests_dict (dict[int, list[str|int]]): Dictionary containing test
        information.

    Returns:
        pd.core.frame.DataFrame: DataFrame of temperature DAQ.
    '''
    cart = None
    daqnum = headers["Serial Number"]
    if (daqnum == "21AD4B7" or daqnum =="2082107"):
        cart = "Cart 1"
    if daqnum == "1DE5504" or daqnum == "2082107bbbb":
        cart = "Cart 2"
    test_folder = folder
    temp_data_file = file
    temp_data_path = os.path.join(test_folder, temp_data_file)
    temp_data = pd.read_csv(temp_data_path, skiprows=6)
    if 'AI0 (°C)' in temp_data.columns:
        temp_data.rename(columns=configs[cart], inplace=True)
        if '0.6 ft (°C)' not in temp_data.columns:
            temp_data.rename(columns={'0.0 ft (°C)': '0.6 ft (°C)'}, inplace=True)
    elif '0.0 ft (°C)' in temp_data.columns:
        temp_data.rename(columns={'0.0 ft (°C)': '0.6 ft (°C)'}, inplace=True)
    temp_data['Time'] = pd.to_datetime(temp_data['Date/Time'])
    temp_data['Time'] = temp_data['Time'].dt.strftime('%H:%M:%S')
    temp_data = temp_data.set_index(pd.DatetimeIndex(temp_data['Time']))
    temp_data = temp_data.drop(['Sample', 'Date/Time', 'Time'], axis=1)
    if '3.6 ft b (°C)' in temp_data.columns:
        temp_data = temp_data[['0.6 ft (°C)', '1.8 ft (°C)', '3.6 ft (°C)',
                               '3.6 ft b (°C)', '5.4 ft (°C)', '5.4 ft b (°C)',
                               '7.2 ft (°C)', '9.0 ft (°C)']]
    else:
        temp_data = temp_data[['0.6 ft (°C)', '1.8 ft (°C)', '3.6 ft (°C)',
                               '5.4 ft (°C)', '7.2 ft (°C)', '9.0 ft (°C)']]
    temp_data = convertCtoF(temp_data)
    return temp_data


def convertCtoF(cdfcol: pd.DataFrame|gpd.GeoDataFrame
                ) -> pd.DataFrame|gpd.GeoDataFrame:
    '''
    Using a (Geo)DataFrame it creates a new column that is the conversion of
    another temperature column in °C to °F.

    Inputs:
        cdfcol (pd.DataFrame|gpd.GeoDataFrame): (Geo)Dataframe with temperature
        data in °C to be converted to °F.

    Returns:
        pd.DataFrame|gpd.GeoDataFrame: (Geo)DataFrame with new column of the
        temperature data converted to °F from °C.
    '''
    for col in cdfcol.columns:
        if '(°C)' in col:
            cdfcol[col[:-4] + '(°F)'] = cdfcol[col] * (9/5) + 32
    return cdfcol


def timeseries(dataframe: pd.DataFrame|gpd.GeoDataFrame,
               temp: bool=True,
               ir: bool=False,
               rh: bool=False,
               b: bool=True,
               yminmax: None|tuple[int|float, int|float]=None,
               timeframe: None|tuple[pd.Timestamp, pd.Timestamp]=None
               ) -> plt.Figure:
    '''
    Generates a time series of either temperature, temperature and IR, IR,
    or RH %. For the temperature columns there is the option to include the 'b'
    sensors or not. There are also other inputs for restricting the y axis
    and time frame of the plot. By default it will generate a time series of
    temperature with the 'b' sensors.

    Inputs:
        dataframe (pd.DataFrame|gpd.GeoDataFrame): The (Geo)DataFrame with all
        the columns to be used for plotting.
        temp (bool): If RTDs should be plotted. Default True.
        ir (bool): If IR should be plotted. Defualt False.
        rh (bool): If RH should be plotted. Default False.
        b (bool): If the 'b' RTD sensors should be plotted. Default True. Will
        be plotted as dashed lines of the same color as their 'a'.
        ymaxmin (None|tuple[int|float, int|float]): The maximum and minimum
        y-axis values for the plot. Default None.
        timeframe (None|tuple[pd.Timestamp, pd.Timestamp]): Filter start and
        end time for the plot.

    Returns:
        plt.Figure: Time series plot with the chosen parameters.

    '''
    plt.figure(figsize=(40, 10))
    colordict = {
        6: (mcolors.CSS4_COLORS['navy']),
        5: (mcolors.CSS4_COLORS['royalblue']),
        4: (mcolors.CSS4_COLORS['dodgerblue']),
        3: (mcolors.CSS4_COLORS['tomato']),
        2: (mcolors.CSS4_COLORS['red']),
        1: (mcolors.CSS4_COLORS['maroon']),
    }
    i = 1
    if temp:
        for column in dataframe.columns:
            if '(°F)' in column and 'ft' in column:
                if 'b' not in column:
                    plt.plot(dataframe.index, dataframe[column], label=column,
                            color=colordict.get(i, (0, 0, 0)))
                    i += 1
                elif b:
                    plt.plot(dataframe.index, dataframe[column], label=column,
                            color=colordict.get(i, (0, 0, 0)),
                            linestyle='dashed')
        plt.ylabel('Temperature (°F)', fontsize=30)
    if ir:
        plt.plot(dataframe.index, dataframe['IR (°F)'], label='IR (°F)',
                 color='black')
        plt.ylabel('Temperature (°F)', fontsize=30)
    if rh:
        plt.ylabel('Relative Humidity (RH %)', fontsize=30)

    #plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xlabel('Time', fontsize=30)
    if yminmax is not None:
        plt.ylim(yminmax[0], yminmax[1])
    if timeframe is not None:
        plt.xlim(timeframe[0], timeframe[1])
    plt.tick_params(axis='both', which='major', labelsize=20)
    title = input('What would you like the time series title to be?: ')
    plt.title(title, fontsize=30)
    plt.legend(fontsize=30)
    plt.tight_layout()
    plt.grid(True)
    #plt.savefig()
    plt.show()
    return plt
