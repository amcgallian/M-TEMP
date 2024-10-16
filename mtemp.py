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


def define_output_folder(test_dict: dict[int, list[str|int]], test_number: int
                         ) -> str:
    '''
    This function should run on program start and automatically find the
    associated output folder for the given test number.

    Inputs:
        test_info (dict[int, list[str|int]]): Dictionary containing test
        information
        test_number (int): The test number to identify the specific output
        folder.

    Returns:
        str: The path to the output folder for the specified test number.
    '''
    test_folder = test_dict[test_number][0]
    output_folder_path = os.path.join(test_folder, 'outputs')

    # Create the output folder if it does not exist
    os.makedirs(output_folder_path, exist_ok=True)

    return output_folder_path


def load_temp_daq(test_num: int,
                  tests_dict: dict[int, list[str|int]]) -> pd.DataFrame:
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
    test_folder = tests_dict[test_num][0]
    temp_data_file = tests_dict[test_num][1]
    temp_data_path = os.path.join('Test_Folders', test_folder, temp_data_file)
    temp_data = pd.read_csv(temp_data_path, skiprows=6)
    if 'AI0 (°C)' in temp_data.columns:
        temp_data.rename(columns=configs[tests_dict[test_num][8]], inplace=True)
        if '0.6 ft (°C)' not in temp_data.columns:
            temp_data.rename(columns={'0.0 ft (°C)': '0.6 ft (°C)'}, inplace=True)
    elif '0.0 ft (°C)' in temp_data.columns:
        temp_data.rename(columns={'0.0 ft (°C)': '0.6 ft (°C)'}, inplace=True)
    temp_data['Time'] = pd.to_datetime(temp_data['Date/Time'])
    temp_data['Time'] = temp_data['Time'].dt.strftime('%H:%M:%S')
    temp_data = temp_data.set_index(pd.DatetimeIndex(temp_data['Time']))
    temp_data.index = temp_data.index.time
    temp_data = temp_data.drop(['Sample', 'Date/Time', 'Time'], axis=1)
    if '3.6 ft b (°C)' in temp_data.columns:
        temp_data = temp_data[['0.6 ft (°C)', '1.8 ft (°C)', '3.6 ft (°C)',
                               '3.6 ft b (°C)', '5.4 ft (°C)', '5.4 ft b (°C)',
                               '7.2 ft (°C)', '9.0 ft (°C)']]
    else:
        temp_data = temp_data[['0.6 ft (°C)', '1.8 ft (°C)', '3.6 ft (°C)',
                               '5.4 ft (°C)', '7.2 ft (°C)', '9.0 ft (°C)']]
    return temp_data


def load_ir_daq(test_num: int,
                tests_dict: dict[int, list[str|int]]) -> pd.DataFrame:
    '''
    Cleans IR/RH DAQ data and turns it into a DataFrame. Uses the excel
    sheet to find the filepath based on the Test Folder and IR/RH Data
    column.

    Inputs:
        test_num (int): The test number associated with the desired raw IR/RH
        data in the excel sheet.
        tests_dict (dict[int, list[str|int]]): Dictionary containing test
        information.

    Returns:
        pd.core.frame.DataFrame: DataFrame of temperature DAQ.
    '''
    test_folder = tests_dict[test_num][0]
    irrh_data_file = tests_dict[test_num][2]
    irrh_data_path = os.path.join('Test_Folders', test_folder, irrh_data_file)
    irrh_data = pd.read_csv(irrh_data_path, skiprows=6)
    if 'AI0 (V)' in irrh_data.columns:
        irrh_data.rename(columns=configs[tests_dict[test_num][9]], inplace=True)
    irrh_data['Time'] = pd.to_datetime(irrh_data['Date/Time'])
    irrh_data['Time'] = irrh_data['Time'].dt.strftime('%H:%M:%S')
    irrh_data = irrh_data.set_index(pd.DatetimeIndex(irrh_data['Time']))
    irrh_data.index = irrh_data.index.time
    irrh_data = irrh_data.drop(['Sample', 'Date/Time', 'Time'], axis=1)

    return irrh_data


def load_gps(test_num: int,
                tests_dict: dict[int, list[str|int]]) -> pd.DataFrame:
    '''
    Cleans GPS data and turns it into a dataframe. Uses excel sheet to find
    filepath based on temperature data filename column.

    Inputs:
        test_num (int): The test number associated with the desired GPS data in
        the excel sheet.
        tests_dict (dict[int, list[str|int]]): Dictionary containing test
        information.

    Returns:
        pd.core.frame.DataFrame: Dataframe of GPS Data
    '''
    test_folder = tests_dict[test_num][0]
    gps_data_file = tests_dict[test_num][3]
    gps_data_path = os.path.join('Test_Folders', test_folder, gps_data_file)
    gps_data = pd.read_csv(gps_data_path)
    gps_data['Time'] = pd.to_datetime(gps_data['Timestamp'])
    gps_data['Time'] = gps_data['Time'].dt.strftime('%H:%M:%S')
    gps_data = gps_data.set_index(pd.DatetimeIndex(gps_data['Time']))
    gps_data.index = gps_data.index.time
    gps_data = gps_data.drop(['Timestamp', 'Time'], axis=1)
    return gps_data


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
            cdfcol[col + ' (°F)'] = cdfcol[col] * (9/5) + 32
    return cdfcol


def convertVtoIR(virdfcol: pd.DataFrame|gpd.GeoDataFrame
                 ) -> pd.DataFrame|gpd.GeoDataFrame:
    '''
    Calculates the temperature in °F for the raw IR data from V in a new column.
    Uses manufacturers equation.

    Inputs:
        virdfcol (pd.DataFrame|gpd.GeoDataFrame): (Geo)DataFrame with columns
        of raw IR data in V to be converted to °F.

    Returns:
        pd.DataFrame|gpd.GeoDataFrame: (Geo)DataFrame given back with new
        column of the temperature data converted to °F from Raw IR V.
    '''
    for col in virdfcol.columns:
        if 'IR (V)' in col:
            virdfcol[col[0:2] + ' (°F)'] = ((((virdfcol[col] - 0.620)
                                              * 105.263) * (9/5)) + 32)
    return virdfcol


def convertVtoRH(rhdfcol: pd.DataFrame|gpd.GeoDataFrame
                 ) -> pd.DataFrame|gpd.GeoDataFrame:
    '''
    Calculates the RH% from the raw RH V and temperature in C and puts it in a
    new column. Uses manufacturers equation.

    Inputs:
        rhvcolumn (pd.DataFrame|gpd.GeoDataFrame): (Geo)DataFrame with of raw V
        for RH and associated temperature at the same height to be used in
        calculation of RH%.

    Returns:
        pd.DataFrame|gpd.GeoDataFrame: (Geo)DataFrame with new column of
        calculated RH%.
    '''
    for col in rhdfcol.columns:
        if 'Raw RH' in col:
            ir_v = col
            rtd_temp = 0
            for daqcol in rhdfcol.columns:
                if ir_v[3:] in daqcol:
                    rtd_temp = daqcol
            rhdfcol[col[3:] + 'RH (%)'] = (((rhdfcol[col]/5)-0.16)/0.0062
                                        )/(1.0546 - (0.00216 * ((
                                            rhdfcol[rtd_temp] - 32) * (5/9))))
    return rhdfcol


def spatially_enable_data(sensordf: pd.DataFrame,
                          gpsdf: pd.DataFrame,
                          irrhdf: None|pd.DataFrame=None) -> gpd.GeoDataFrame:
    '''
    Merges Temperature sensor dataframe with gps dataframe to create a GeoDataFrame with
    specified CRS. Will also merge IR if desired.

    Inputs:
        sensordf (pd.DataFrame): DataFrame containing all relevant sensor data
        to be merged.
        gpsdf (pd.DataFrame): DataFrame containing all relevant gps data to be
        merged.
        irrhdf (pd.DataFrame): DataFrame containing all relevant IR/RH data to
        be merged. Is not included by default.

    Returns:
        gpd.core.series.GeoDataFrame: New spatially enabled GeoDataFrame of
        sensor data.
    '''
    if irrhdf is not None:
        merged_sensor_df = pd.merge(sensordf, irrhdf, left_index=True,
                                    right_index=True, how='inner')
        merged_df = pd.merge(merged_sensor_df, gpsdf, left_index=True,
                            right_index=True, how='inner')
    else:
        merged_df = pd.merge(sensordf, gpsdf, left_index=True,
                             right_index=True, how='inner')
    geometry = [Point(xy) for xy in zip(merged_df['Longitude'],
                                        merged_df['Latitude'])]
    gdf = gpd.GeoDataFrame(merged_df, geometry=geometry, crs="EPSG:4326")
    gdf = gdf.to_crs(epsg=3857)
    return gdf


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


def dot_map(gdf: gpd.GeoDataFrame) -> plt.Figure:
    '''
    Generates a map with each data point on it, usually used as a test to show
    path and to make sure everything merged correctly and was spatially enabled.

    Inputs:
        gdf (gpd.GeoDataFrame):
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