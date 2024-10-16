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
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
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
    output_folder_path = os.path.join('Test_folders', test_folder, 'outputs')

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
            cdfcol[col[:-4] + '(°F)'] = cdfcol[col] * (9/5) + 32
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
        if 'IR Raw (V)' in col:
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
                if ir_v[7:] in daqcol and 'b' not in daqcol:
                    rtd_temp = daqcol
            rhdfcol[col[7:] + 'RH (%)'] = (((rhdfcol[col]/5)-0.16)/0.0062
                                        )/(1.0546 - (0.00216 * ((
                                            rhdfcol[rtd_temp] - 32) * (5/9))))
    return rhdfcol


def merge_sensors(sensordf: pd.DataFrame,
                  irrhdf: pd.DataFrame) -> pd.DataFrame:
    '''
    Merges the temperature and IR/RH dataframes using their relevant DataFrames

    Inputs:
        sensordf (pd.DataFrame): Temperature Dataframe
        irrhdf (pd.DataFrame): IR/RH DataFrame

    Returns:
        pd.DataFrame The new merged dataframe
    '''
    merged_sensor_df = pd.merge(sensordf, irrhdf, left_index=True,
                                right_index=True, how='inner')
    return merged_sensor_df


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
        merged_sensor_df = merge_sensors(sensordf, irrhdf)
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


def timeseries(output_folder: str,
               dataframe: pd.DataFrame|gpd.GeoDataFrame,
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
        output_folder (str): Where the plot will be saved to, this should be
        automatic and based on define_output_folder()
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
    plt.title(input('What would you like the time series title to be?: '),
              fontsize=30)
    plt.legend(fontsize=30)
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(output_folder)
    plt.show()
    return plt


def dot_map(gdf: gpd.GeoDataFrame, output_folder: str) -> plt.Figure:
    '''
    Generates a map with each data point on it, usually used as a test to show
    path and to make sure everything merged correctly and was spatially enabled.
    Will automatically use the '5.4 ft (°F)' column to plot. This function it
    more for ensuring correct GPS merging and plotting.

    Inputs:
        gdf (gpd.GeoDataFrame): GeoDataFrame with all relevant sensor and gps
        data.
        output_folder (str): Where the plot will be saved to, this should be
        automatic and based on define_output_folder()

    Returns:
        plt.Figure: The plot of GPS data on the map with the '5.4 ft (°F)'
        level as the color of each dot.
    '''
    fig, ax = plt.subplots(figsize=(40, 10))
    gdf.plot(ax=ax, marker='o', column='5.4 ft (°F)',
             cmap='Reds', markersize=40, legend=True)
    ctx.add_basemap(ax, crs=gdf.crs.to_string(),
                    source=ctx.providers.OpenStreetMap.Mapnik)
    plt.axis('off')
    plt.title(input('What would you like the plot title to be?: '))
    plt.savefig(output_folder)
    plt.show()
    return plt


def scatter_plot(column1: pd.Series|gpd.GeoSeries,
                 column2: pd.Series|gpd.GeoSeries,
                 output_folder: str,
                 column3: None|pd.Series|gpd.GeoSeries=None,
                 cmap: str='viridis'
                 ) -> plt.Figure:
    '''
    Generates a scatter plot of two chosen columns from a (Geo)DataFrame.

    Inputs:
        column1 (pd.Series|gpd.GeoSeries): Column 1 to be plotted.
        column2 (pd.Series|gpd.GeoSeries): Column 2 to be plotted.
        output_folder (str): Where the plot will be saved to, this should be
        automatic and based on define_output_folder()
        column3 (None|pd.Series|gpd.GeoSeries): Column 3 to be plotted as a
        color ramp on the plotted points of Column 1 and 2. Default None.
        cmap (str): Colormap to use for coloring points based on column3.
                    Default is 'viridis'.

    Returns:
        plt.Figure: The scatter plot of the columns plotted.

    '''
    plt.figure()
    if column3 is not None:
        plt.scatter(column1, column2, c=column3, cmap=cmap)
        plt.colorbar(label=column3.name)
    else:
        plt.scatter(column1, column2, color='green')
    plt.xlabel(column1.name)
    plt.ylabel(column2.name)
    plt.title(f'{column1.name} vs. {column2.name} Correlation Plot')
    plt.legend()
    plt.savefig(output_folder)
    plt.show()
    return plt


def make_heatmap(gdf: gpd.GeoDataFrame,
                 output_folder: str,
                 units: str='F',
                 cell_size: int=10,
                 interpolate: bool=False,
                 ) -> plt.Figure:
    '''
    Generates a heatmap of the chosen columns, based on given units, using the
    (eoDataFrame. Will automatically save outputs to output folder.

    Inputs:
        gdf (gpd.GeoDataFrame): GeoDataFrame with the relevant data to be used
        for plotting.
        output_folder (str): Should be based off of define_output_folder,
        should be automatic.
        units (str): Will default to °F as the units. Other acceptable inputs
        are C for °C and RH for RH%. This is case sensitive.
        cell_size (int): The cell size for the grid to be plotted. In meters.
        Default is 10. Not reccomended to go less than 5 if not interpolating
        due to phone GPS accuracy limits.
        interpolate (bool): Decides if the plot should be interpolated. Default
        is False, may not be alwasys useful for transects, better for grids.
        Uses linear interpolation.

    Returns:
        plt.Figure: The heatmap of each height for the unit type.

    '''
    units = 'ft (°F)'
    if units != 'F':
        if units == 'C':
            units = '(°C)'
        if units == 'RH':
            units = 'RH (%)'
    global_min = float('inf')
    global_max = float('-inf')

    for vertcolumn in gdf.columns:
        if units in vertcolumn:
            xmin, ymin, xmax, ymax = gdf.total_bounds
            cols = int(np.ceil((xmax - xmin) / cell_size))
            rows = int(np.ceil((ymax - ymin) / cell_size))
            grid = np.full((rows, cols), np.nan)
            for row in range(rows):
                for col in range(cols):
                    x0 = xmin + col * cell_size
                    x1 = x0 + cell_size
                    y0 = ymin + row * cell_size
                    y1 = y0 + cell_size
                    points_in_cell = gdf.cx[x0:x1, y0:y1]
                    if not points_in_cell.empty:
                        mean_temp = points_in_cell[vertcolumn].mean()
                        grid[row, col] = mean_temp
                        global_min = min(global_min, np.nanmin(grid))
                        global_max = max(global_max, np.nanmax(grid))
    if interpolate:
        for col in gdf.columns:
            if units in col:
                xmin, ymin, xmax, ymax = gdf.total_bounds
                cols = int(np.ceil((xmax - xmin) / cell_size))
                rows = int(np.ceil((ymax - ymin) / cell_size))
                grid_x, grid_y = np.meshgrid(
                    np.linspace(xmin, xmax, cols),
                    np.linspace(ymin, ymax, rows)
                )
                coords = np.array([(x, y) for x, y in zip(gdf.geometry.x,
                                                          gdf.geometry.y)])
                temps = gdf[col].values
                grid_temps = griddata(coords, temps, (grid_x, grid_y),
                                      method='linear')
                transform = from_origin(xmin, ymax, cell_size, cell_size)
                def flip_grid_vertically(grid):
                    return np.flipud(grid)
                grid_flipped = flip_grid_vertically(grid_temps)
                raster_meta = {
                    'driver': 'GTiff',
                    'height': rows,
                    'width': cols,
                    'count': 1,
                    'dtype': rasterio.float32,
                    'crs': 'EPSG:3857',
                    'transform': transform,
                }
                raster_output_path = os.path.join(output_folder,
                                                  f'{col}_heatmap_inter.tif')
                image_output_path = os.path.join(output_folder,
                                                 f'{col}_heatmap_inter.png')
                with rasterio.open(raster_output_path, 'w',
                                   **raster_meta) as dst:
                    dst.write(grid_flipped, 1)
                with rasterio.open(raster_output_path) as src:
                    data = src.read(1)
                    bounds = src.bounds
                fig, ax = plt.subplots(figsize=(10, 10))
                img = ax.imshow(data, cmap='Reds', extent=(bounds.left,
                                                           bounds.right,
                                                           bounds.bottom,
                                                           bounds.top),
                                                           aspect='equal',
                                                           vmin=global_min,
                                                           vmax=global_max)
                plt.colorbar(img, label=units)
                plt.axis('off')
                plt.title(f'{col}')
                plt.savefig(image_output_path)
                plt.show()
    else:
        for vertcolumn in gdf.columns:
            if units in vertcolumn:
                xmin, ymin, xmax, ymax = gdf.total_bounds
                cols = int(np.ceil((xmax - xmin) / cell_size))
                rows = int(np.ceil((ymax - ymin) / cell_size))
                grid = np.full((rows, cols), np.nan)
                for row in range(rows):
                    for col in range(cols):
                        x0 = xmin + col * cell_size
                        x1 = x0 + cell_size
                        y0 = ymin + row * cell_size
                        y1 = y0 + cell_size
                        points_in_cell = gdf.cx[x0:x1, y0:y1]
                        if not points_in_cell.empty:
                            grid[row, col] = points_in_cell[vertcolumn].mean()
                transform = from_origin(xmin, ymax, cell_size, cell_size)
                def flip_grid_vertically(grid):
                    return np.flipud(grid)
                grid_flipped = flip_grid_vertically(grid)
                raster_meta = {
                    'driver': 'GTiff',
                    'height': rows,
                    'width': cols,
                    'count': 1,
                    'dtype': rasterio.float32,
                    'crs': 'EPSG:3857',
                    'transform': transform,
                }
                raster_output_path = os.path.join(output_folder,
                                                  f'{vertcolumn}_heatmap.tif')
                image_output_path = os.path.join(output_folder,
                                                 f'{vertcolumn}_heatmap.png')
                with rasterio.open(raster_output_path, 'w',
                                   **raster_meta) as dst:
                    dst.write(grid_flipped, 1)
                with rasterio.open(raster_output_path) as src:
                    data = src.read(1)
                    bounds = src.bounds
                fig, ax = plt.subplots(figsize=(20, 10))
                img = ax.imshow(data, cmap='Reds', extent=(bounds.left,
                                                           bounds.right,
                                                           bounds.bottom,
                                                           bounds.top),
                                                           aspect='equal',
                                                           vmin=global_min,
                                                           vmax=global_max)
                plt.colorbar(img, label=units)
                plt.axis('off')
                plt.title(f'{vertcolumn}')
                plt.savefig(image_output_path)
                plt.show()
    return plt


def vertical_heatmap(df: pd.DataFrame|gpd.GeoDataFrame,
                     output_folder: str,
                     temp: bool=True,
                     ir: bool=False,
                     rh: bool=False,
                     to_height: int|float=10.8
                     ) -> plt.Figure:
    '''
    Generates a vertial heatmap of the chosen data from the (Geo)DataFrame.

    Inputs:
        df (pd.DataFrame|gpd.GeoDataFrame): The (Geo)DataFrame with all the
        relevant sensor data to be plotted.
        output_folder (str): The output folder that the plot will be saved to,
        should be found automatically through define_output_folder().
        temp (bool): If temperature columns should be plotted. Default True.
        ir (bool): If IR should be plotted. Default False.
        rh (bool): IF RH should be plotted. Default False.
        to_height (int|float): The height of the top sensor plus the interval
        between all sensors.

    Returns:
        plt.Figure: The plot of the vertical heatmap.

    '''
    if temp:
        units = 'ft (°F)'
    if rh:
        units = 'RH (%)'
    image_output_path = os.path.join(output_folder, 'vertheatmap.png')
    heights = np.arange(1.8, to_height, 1.8)
    grid_labels = [f'{h} ft' for h in heights]
    grid_data = []
    grid_data.append(df['0.6 ft (°F)'])
    if ir:
        grid_data.append(df['IR (°F)'])
    for height in heights:
        height_data = df[f'{height} {units}'].tolist()
        grid_data.append(height_data)
    fig, ax = plt.subplots(figsize=(40, 10))
    heatmap = ax.imshow(grid_data, cmap='Reds', aspect='auto',
                        interpolation='nearest')
    ax.set_title(input('What would you like the title to be?: '), fontsize=30)
    ax.set_xlabel('Time')
    ax.set_ylabel('Height (ft)', fontsize=30)
    ax.set_yticks(np.arange(len(heights)))
    ax.set_yticklabels(grid_labels)
    plt.tick_params(axis='both', which='major', labelsize=20)
    ax.invert_yaxis()
    cbar = plt.colorbar(heatmap, ax=ax, orientation='vertical')
    cbar.ax.tick_params(labelsize=20)
    cbar.set_label(units, size=30)
    plt.tight_layout()
    plt.savefig(output_folder)
    plt.show()
    return plt