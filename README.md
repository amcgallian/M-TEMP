# M-Temp Data Processing and Analysis Program

## Overview

The **M-Temp Data Processing Module** is a Python script designed to handle and process M-Temp data efficiently. This module provides a suite of functions for loading, cleaning, converting, and visualizing temperature, IR/RH, and GPS data. It is intended to be interacted with at the command line through the `main.py` script.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Using The Script](#using-the-script)
  - [Using The Excel Sheet](#using-the-excel-sheet)
- [Directory Structure](#directory-structure)
- [Functions](#functions)
  - [Loading Data](#loading-data)
    - [`load_excelsheet()`](#load_excelsheet)
    - [`define_output_folder()`](#define_output_folder)
    - [`load_temp_daq()`](#load_temp_daq)
    - [`load_ir_daq()`](#load_ir_daq)
    - [`load_gps()`](#load_gps)
  - [Data Conversion](#data-conversion)
    - [`convertCtoF()`](#convertctoF)
    - [`convertVtoIR()`](#convertvtoir)
    - [`convertVtoRH()`](#convertvtorh)
  - [Spatial Data Handling](#spatial-data-handling)
    - [`spatially_enable_data()`](#spatially_enable_data)
  - [Visualization](#visualization)
    - [`timeseries()`](#timeseries)
    - [`scatter_plot()`](#scatter_plot)
    - [`make_heatmap()`](#make_heatmap)
    - [`vertical_heatmap()`](#vertical_heatmap)
- [Cart Configuration](#cart-configuration)
- [Ideas for Future Development](#ideas-for-future-development)
- [Author](#author)
- [License](#license)

## Features

- **Data Loading**: Efficiently load and clean temperature, IR/RH, and GPS data from Excel and CSV files.
- **Data Conversion**: Convert temperature from Celsius to Fahrenheit, raw IR voltage to temperature, and raw RH voltage to relative humidity percentages.
- **Spatial Data Handling**: Merge sensor data with GPS data to create geospatial datasets.
- **Visualization**: Generate time series plots, scatter plots, and heatmaps for comprehensive data analysis.
- **Configuration Management**: Easily manage different sensor configurations for multiple carts.

## Installation

Ensure you have Python 3.7 or higher installed. You can install the required dependencies found with the included requirements.txt file by using `pip`:

```{bash}
pip install -r requirements.txt
```

## Usage

### Using The Script

From the command line you can invoke `main.py` to begin the script to process M-Temp data.

```bash
python main.py
```

You then will be presented with an interface within the program where you will simply input an integer that refers to the test you would like to work with. You then will have other prompts to do specific operations with the data from that test.

More to come soon on how to interact and use.

Here’s a revised version of the section that improves clarity and presentation:

### Using The Excel Sheet

To ensure the script functions correctly, the included Excel sheet must be up-to-date and accurately filled out for each test. The script depends on the information in each column being accurate so that the only interaction you need to have is through inputting the test number. The Excel sheet consists of 11 columns, each with specific requirements:

| Column Name               | Requirements                                                         |
|---------------------------|----------------------------------------------------------------------|
| **Test Number**           | Must be an integer.                                                 |
| **Test Folder**           | Should be written as plain text    |
| **Temperature Data**      | Should be written as plain text    |
| **IR/RH Data**            | Should be written as plain text    |
| **GPS Data**              | Should be written as plain text    |
| **Test Date**             | Valid date format, stay consistent.                                                 |
| **Testing Route**         | Description of the testing route.                                  |
| **Cart**                  | Name or description of the cart used.                              |
| **Set Up**                | Description of the wiring setup process.                                  |
| **Temperature Configuration** | Should be written in plain text    |
| **IR/RH Configuration**   | Should be written in plain text    |

**Note:** All columns must be filled out properly. If there is no data or information available for a column, please input `None`.

## Directory Structure

The raw data and outputs are organized in a structured directory layout to facilitate easy access and management. The scipt also hinges on this structure being used.

```mermaid
graph LR;
    A[main_project_folder] -->|contains| B[main.py]
    A -->|contains| C[mtemp.py]
    A -->|contains| D[test_list.xlsx]
    A -->|contains| E[test_folders]
    E -->|contains| F[test_n]
    F -->|contains| G[temp_data.csv]
    F -->|contains| H[ir_rh_data.csv]
    F -->|contains| I[gps_data.csv]
    F -->|contains| J[outputs]
    J -->|contains| K[output_plot1.png]
    J -->|contains| L[output_results.png]
    J -->|contains| M[...]
    E -->|contains| N[test_n+1]
    E -->|contains| O[...]
```

### Explanation of Key Files and Folders

- **main.py**: The primary script that utilizes the `mtemp` module for data processing.
- **mtemp.py**: The M-Temp Data Processing Module containing all necessary functions.
- **test_list.xlsx**: Excel file containing references to all tests, where their data is stored, and their configurations.
- **/test_folders/**: Directory containing individual test data folders.
  - **/test_n/**: Folder for a specific test containing raw data and outputs.
    - **temp_data.csv**: Temperature DAQ data.
    - **ir_rh_data.csv**: IR/RH DAQ data.
    - **gps_data.csv**: GPS data.
    - **/outputs/**: Directory for generated plots and results.

## Functions

### Loading Data

Here are the revised descriptions for the functions based on your updated code:

#### `load_excelsheet()`

Automatically loads the Excel reference sheet and converts it into a dictionary for easy access to file paths, configurations, and test-related information. The dictionary uses test numbers as keys and their associated data, including folder paths, temperature data, IR/RH data, GPS data, and more, as a list values. This function should be run at program start to ensure all data-loading functions can access the necessary file paths.

- **Parameters**:
  - None
- **Returns**:
  A dictionary with test numbers as keys and associated lists of relevant information as values, such as file paths and configurations.

#### `define_output_folder()`

Automatically finds or creates the output folder for the specified test number. The function uses the test number to locate the associated test folder and ensures an 'outputs' subdirectory is created if it doesn't already exist.

- **Parameters**:
  - `test_dict`: Dictionary containing test information loaded from the Excel sheet.
  - `test_number`: The test number for which the output folder path is needed.
- **Returns**:
  The path to the output folder for the specified test number.

#### `load_temp_daq()`

Loads, cleans, and returns the temperature DAQ data as a pandas DataFrame based on the given test number. It uses the test folder and temperature data path stored in the Excel reference sheet. The function formats timestamps, renames columns according to configuration, and selects relevant temperature columns for analysis.

- **Parameters**:
  - `test_num`: The test number associated with the desired temperature data.
  - `tests_dict`: Dictionary containing test information loaded from the Excel sheet.
- **Returns**:
  A pandas DataFrame containing the cleaned temperature data, with the appropriate columns renamed and formatted for analysis.

#### `load_ir_daq()`

Loads and cleans IR/RH DAQ data based on the test number.

- **Parameters**:
  - `test_num`: The test number associated with the desired IR/RH data.
- **Returns**: A pandas DataFrame containing IR/RH data.

#### `load_gps()`

Loads and cleans GPS data based on the test number.

- **Parameters**:
  - `test_num`: The test number associated with the desired GPS data.
- **Returns**: A pandas DataFrame containing GPS data.

### Data Conversion

#### `convertCtoF()`

Converts a temperature column from Celsius to Fahrenheit.

- **Parameters**:
  - `ccolumn`: Pandas Series containing temperature data in Celsius.
- **Returns**: Pandas Series with temperature data in Fahrenheit.

#### `convertVtoIR()`

Calculates temperature in Fahrenheit from raw IR voltage data.

- **Parameters**:
  - `vcolumn`: Pandas Series containing raw IR voltage data.
- **Returns**: Pandas Series with temperature data in Fahrenheit.

#### `convertVtoRH()`

Calculates Relative Humidity (%) from raw RH voltage and temperature data.

- **Parameters**:
  - `rhvcolumn`: Pandas Series containing raw RH voltage data.
  - `tempcolumn`: Pandas Series containing temperature data in Celsius.
- **Returns**: Pandas Series with calculated Relative Humidity percentages.

### Spatial Data Handling

#### `spatially_enable_data()`

Merges sensor data with GPS data to create a GeoDataFrame with spatial information.

- **Parameters**:
  - `sensordf`: DataFrame containing sensor data.
  - `gpsdf`: DataFrame containing GPS data.
- **Returns**: GeoPandas GeoDataFrame with spatially enabled sensor data.

### Visualization

#### `timeseries()`

Generates a time series plot for temperature, IR, and/or RH data.

- **Parameters**:
  - `dataframe`: DataFrame or GeoDataFrame containing the data to plot.
  - `temp`: Include temperature data. Default True.
  - `ir`: Include IR data. Default False.
  - `rh`: Include RH data. Default False.
  - `b`: Include 'b' sensors. Default True.
  - `ymax`: Maximum y-axis limit as a float or integer. Default None.
  - `ymin`: Minimum y-axis limit as a float or integer. Default None.
  - `starttime`: Start time for the plot as a Pandas Timestamp. Default None.
  - `endtime`: End time for the plot as a Pandas Timestamp. Default None.
- **Returns**: Matplotlib Figure object with the time series plot.

#### `scatter_plot()`

Generates a scatter plot between two data columns.

- **Parameters**:
  - `column1`: First data column.
  - `column2`: Second data column.
- **Returns**: Matplotlib Figure object with the scatter plot.

#### `make_heatmap()`

Generates a heatmap from geospatial data.

- **Parameters**:
  - `gdf`: GeoDataFrame containing the spatial data.
  - `cell_size`: Size, in meters, of each cell in the heatmap as an integer. Default 10.
  - `interpolate`: Whether to interpolate the heatmap. Default False.
- **Returns**: Matplotlib Figure object with the heatmap.

#### `vertical_heatmap()`

Generates a vertical heatmap from the data.

- **Parameters**:
  - `df`: DataFrame or GeoDataFrame containing the data.
  - `ir`: Include IR data. Default False.
  - `to_height`: Height parameter, in feet, for the heatmap as a float or integer. Default 10.8.
- **Returns**: Matplotlib Figure object with the vertical heatmap.

## Cart Configuration

The module includes predefined configurations for different sensor carts. These configurations map sensor channels to their respective physical positions and measurement units.

```python
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
```

## Ideas for Future Development

- **Make Function to Smooth Out IR Data**: Implement a function to smooth out
IR data in some way since it is so erratic.
- **Subset DataFrame Generation**: Implement a function to generate a subset of the DataFrame based on user-specified columns.
- **Enhanced Visualization**: Add more visualization options and enhance current options.
- **Data Validation**: Incorporate data validation checks to ensure data integrity before processing.

## Author

**M-TEMP Team**

_Last Updated: October 15, 2024_

## License

[MIT License](LICENSE)

---