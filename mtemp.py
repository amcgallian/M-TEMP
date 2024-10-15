'''
Module for all the functions needed when processing M-Temp data. This is to be
used within the main.py processing code.

Last Updated: 10/15/2024
Author: Andrew McGallian

Ideas for further functions:
    - Something that generates a subset dataframe based on added columns
'''

# Imports
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.transform import from_origin
from scipy.interpolate import griddata
import contextily as ctx
import os as os

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

    "Cart 1 IR": {'AI0 (V)':'IR Raw'},

    "Cart 2 Temp": {'AI2 (°C)': '1.8 ft (°C)',
                'AI1 (°C)': '0.6 ft (°C)',
                'AI3 (°C)': '3.6 ft (°C)',
                'AI4 (°C)': '3.6 ft b (°C)',
                'AI0 (°C)': '5.4 ft (°C)',
                'AI5 (°C)': '5.4 ft b (°C)',
                'AI6 (°C)': '7.2 ft (°C)' ,
                'AI7 (°C)': '9.0 ft (°C)'
                },

    "Cart 2 IR": {'AI0 (V)':'IR Raw',
                  'AI1 (V)':'RH 0.0ft',
                  'AI3 (V)':'RH 1.8ft',
                  'AI2 (V)':'RH 7.2ft',
                  'AI4 (V)':'RH 9.0ft'}

}

# Functions

def load_excelsheet(filepath: str) -> dict[int: list[str|int]]:
    '''
    Loads the excel reference sheet and turns it into a dictionary. For example
    user can set a variable tests = load_excelsheet('path/to/file') and then
    will have tests become a dictionary where they could look up, say, the
    filepath to the test by doing tests[###test number###][1]. This function
    should be used first before loading any data since those functions will
    depend on that dictionary scheme for accessing file paths. Popup should
    come where it prompts you to choose the sheet. This function should run on
    program start.

    Currently the scheme should be as such:
        - They key will be the test number (int) i.e. 1
        - The "value" will be a list with the associated excel sheet columns
        being:
            [folders, temperature data, ir/rh data, gps data, date,
            testing route, cart, set up, config]

    This also means the scheme where the raw data is stored should look like:

    /main_project_folder
    │
    ├──main.py
    │
    ├── /test_folders
    │   ├──/test_n
    │   │   ├── temp_data.csv
    │   │   ├── ir_rh_data.csv
    │   │   ├── gps_data.csv
    │   │   └── /outputs
    │   │       ├── output_plot1.png
    │   │       ├── output_results.png
    │   │       └── ...
    │   ├──/test_n+1
    │   └── ...
    │
    ├── mtemp.py
    │
    ├── test_list.xlsx
    │
    └── README.md

    Inputs:
        filepath (str): file with file path.

    Returns:
        dict[int, list[str|int]]: Dictionary with a list of relevant
        information such as filepath, configuration, and more for each test
        name availible in the excel spreadsheet.
    '''
    return None


def define_output_folder(folderpath: str) -> str:
    '''
    Popup should come where it prompts you to choose the folder plots will
    be saved to when generated. Makes it easier than typing it in. This
    function should run on program start.

    Inputs:
        folderpath (str): folder with path to folder

    Returns:
        str: folderpath chosen by user
    '''
    return folderpath


def load_temp_daq(test_num: int) -> pd.DataFrame:
    '''
    Cleans temperature DAQ data and turns it into a dataframe. Uses excel sheet
    to find filepath based on temperature data filename column.

    Inputs:
        test_num (int): The test number associated with the desired temperature
        data in the excel sheet.

    Returns:
        pd.core.frame.DataFrame: Dataframe of temperature DAQ.
    '''
    return None


def load_ir_daq(test_num: int) -> pd.DataFrame:
    '''
    Cleans IR/RH DAQ data and turns it into a dataframe. Uses excel sheet to
    find filepath based on temperature data filename column.

    Inputs:
        test_num (int): The test number associated with the desired IR or RH
        data in the excel sheet.

    Returns:
        pd.core.frame.DataFrame: Dataframe of IR/RH DAQ.
    '''
    return None


def load_gps(test_num: int) -> pd.DataFrame:
    '''
    Cleans GPS data and turns it into a dataframe. Uses excel sheet to find
    filepath based on temperature data filename column.

    Inputs:
        test_num (int): The test number associated with the desired GPS data in
        the excel sheet.

    Returns:
        pd.core.frame.DataFrame: Dataframe of GPS Data
    '''
    return None


def convertCtoF(ccolumn: pd.Series) -> pd.Series:
    '''
    Creates a new column that is the conversion of another temperature column
    in C to F.

    Inputs:
        ccolumn (pd.core.series.Series): Column of temperature data in C to be
        converted to F.

    Returns:
        pd.core.series.Series: New column of the temperature data converted
        to F from C.
    '''
    return None


def convertVtoIR(vcolumn: pd.Series) -> pd.Series:
    '''
    Calculates the temperature in F for the raw IR data from V in a new column.

    Inputs:
        vcolumn (pd.core.series.Series): Column of raw IR data in V to be
        converted to F.

    Returns:
        pd.core.series.Series: New column of the temperature data converted
        to F from Raw IR V.
    '''
    return None


def convertVtoRH(rhvcolumn: pd.Series,
                 tempcolumn: pd.Series) -> pd.Series:
    '''
    Calculates the RH% from the raw RH V and temperature in C and puts it in a
    new column.

    Inputs:
        rhvcolumn (pd.core.series.Series): Column of raw RH V to be used in the
        calculation of RH%
        tempcolumn (pd.core.series.Series): Column of temperature data in C to
        be used in the calculation of RH%

    Returns:
        pd.core.series.Series: New column of calculated RH%
    '''
    return None


def spatially_enable_data(sensordf: pd.DataFrame,
                          gpsdf: pd.DataFrame) -> gpd.GeoDataFrame:
    '''
    Merges sensor dataframe with gps dataframe to create a GeoDataFrame with
    specified CRS.

    Inputs:
        sensordf (pd.core.series.Dataframe): Dataframe containing all relevant
        sensor data to be merged.
        gpsdf (pd.core.series.Dataframe): Dataframe containing all relevant
        gps data to be merged.

    Returns:
        gpd.core.series.GeoDataFrame: New spatially enabled GeoDataFrame of
        sensor data.
    '''
    return None


def timeseries(dataframe: pd.DataFrame|gpd.GeoDataFrame,
               temp: bool=True,
               ir: bool=False,
               rh: bool=False,
               b: bool=True,
               ymax: None|int|float=None,
               ymin: None|int|float=None,
               starttime: None|pd.Timestamp=None,
               endtime: None|pd.Timestamp=None) -> plt.Figure:
    '''
    Generates a time series of either temperature, temperature and IR, IR,
    or RH %. For the temperature columns there is the option to include the 'b'
    sensors or not. There are also other inputs for restricting the y axis
    and time frame of the plot. By default it will generate a time series of
    temperature with the 'b' sensors.

    Inputs:
        dataframe (pd.DataFrame|gpd.GeoDataFrame):
        temp (bool):
        ir (bool):
        rh (bool):
        b (bool):
        ymax (None|int|float):
        ymin (None|int|float):
        starttime (None|pd.Timestamp):
        endtime (None|pd.Timestamp):

    Returns:
        plt.Figure: Time series plot with the chosen parameters.

    '''
    return None


def scatter_plot(column1: pd.Series|gpd.GeoSeries,
                 column2: pd.Series|gpd.GeoSeries) -> plt.Figure:
    '''
    Generates a

    Inputs:

    Returns:

    '''
    return None


def make_heatmap(gdf: gpd.GeoDataFrame,
                 cell_size: int=10,
                 interpolate: bool=False,
                 ) -> plt.Figure:
    '''
    Generates a

    Inputs:

    Returns:

    '''
    return None


def vertical_heatmap(df: pd.DataFrame|gpd.GeoDataFrame,
                     ir: bool=False,
                     to_height: int|float=10.8
                     ) -> plt.Figure:
    '''
    Generates

    Inputs:

    Returns:

    '''
    return None