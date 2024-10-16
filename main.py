"""
M-TEMP DATA PROCESSING PROGRAM

Last Updated: 10/16/2024
Author: Andrew McGallian

Main file for processing M-TEMP data. The main loop for the program
runs here and utilizes the mtemp module's functions. Refer to the
README for further guidance on operating the program.
"""

# IMPORTS
import os
import sys
import pyfiglet
import logging
import pandas as pd
import mtemp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class MTempProcessor:
    """Class to handle M-TEMP data processing and user interactions."""

    def __init__(self):
        # Initialize data variables
        self.tests = mtemp.load_excelsheet()
        self.test_num = None
        self.tempdf = None
        self.gpsdf = None
        self.irrhdf = None
        self.df = None
        self.gdf = None
        self.output = None

    def display_ascii_title(self):
        """Displays the ASCII art title."""
        ascii_title = pyfiglet.figlet_format("M-TEMP")
        print(ascii_title)

    def clear_screen(self):
        """Clears the terminal screen."""
        os.system("clear" if os.name == "posix" else "cls")

    def draw_separator(self):
        """Prints a separator line."""
        print("Xx-------------------------------------xX")

    def main_menu(self):
        """Displays the main menu and handles user interaction."""
        while True:
            self.clear_screen()
            self.display_ascii_title()
            self.draw_separator()
            print("\nMain Menu:")

            if self.test_num is None:
                print("1. Select Test Number")
            else:
                logging.info(f"Selected Test Number: {self.test_num} - {self.tests[self.test_num][1]}")
                if self.tempdf is None:
                    print("2. Load Temperature Data")
                if self.gpsdf is None:
                    print("3. Load GPS Data")
                if self.irrhdf is None:
                    print("4. Load IR/RH Data")

            if (self.gpsdf is not None and
                (self.tempdf is not None or self.irrhdf is not None) and
                self.gdf is None):
                print("5. Merge and Spatially Enable Data")
            elif (self.tempdf is not None and self.irrhdf is not None and
                  self.df is None and self.gdf is None):
                print("5. Merge Temp and IR into DataFrame")

            if self.gdf is not None:
                print("A. Plot Time Series")
                print("B. Plot Vertical Heatmap")
                print("C. Plot Scatter Plot")
                print("D. Plot Dot Map")
                print("E. Plot Heatmap")
            elif self.df is not None:
                print("A. Plot Time Series")
                print("B. Plot Vertical Heatmap")
                print("C. Plot Scatter Plot")

            print("9. Display Data")
            print("Q. Quit")

            user_choice = input("Please select an option: ").strip().lower()

            # Mapping user choices to methods
            options = {
                "1": self.select_test_number,
                "2": self.load_temperature_data,
                "3": self.load_gps_data,
                "4": self.load_irrh_data,
                "5_merge_spatial": self.merge_and_spatially_enable_data,
                "5_merge_temp_ir": self.merge_temp_ir,
                "a": self.plot_time_series,
                "b": self.plot_vertical_heatmap,
                "c": self.plot_scatter_plot,
                "d": self.plot_dot_map,
                "e": self.plot_heatmap,
                "9": self.display_data,
                "q": self.quit_program
            }

            # Handle options based on user choice and state
            if user_choice == "1" and self.test_num is None:
                options["1"]()
                self.output = mtemp.define_output_folder(self.tests, self.test_num)
            elif user_choice == "2" and self.test_num:
                options["2"]()
            elif user_choice == "3" and self.test_num:
                options["3"]()
            elif user_choice == "4" and self.test_num:
                options["4"]()
            elif user_choice == "5":
                if (self.gpsdf is not None and
                    (self.tempdf is not None or self.irrhdf is not None) and
                    self.gdf is None):
                    options["5_merge_spatial"]()
                elif (self.tempdf is not None and self.irrhdf is not None and
                      self.df is None and self.gdf is None):
                    options["5_merge_temp_ir"]()
                else:
                    self.invalid_option()
            elif user_choice in ["a", "b", "c", "d", "e"]:
                if (self.gdf is not None or self.df is not None):
                    options[user_choice]()
                else:
                    self.invalid_option()
            elif user_choice == "9":
                options["9"]()
                input(">Press Enter to Continue")
            elif user_choice == "q":
                options["q"]()
            else:
                self.invalid_option()

    def invalid_option(self):
        """Handles invalid menu options."""
        logging.warning("Invalid option. Please try again.")
        input(">Press Enter")

    def select_test_number(self):
        """Handles selecting the test number."""
        try:
            test_num_input = input("Enter test number: ").strip()
            self.test_num = int(test_num_input)
            if self.test_num not in self.tests:
                logging.error(f"Test number {self.test_num} does not exist.")
                self.test_num = None
            else:
                logging.info(f"Test number {self.test_num} selected.")
        except ValueError:
            logging.error("Invalid input. Please enter a valid integer test number.")
            self.test_num = None
        input(">Press Enter")

    def load_temperature_data(self):
        """Loads temperature data."""
        try:
            logging.info("Loading temperature data...")
            self.tempdf = mtemp.load_temp_daq(self.test_num, self.tests)
            logging.info("Temperature data loaded successfully.")
            logging.info("Converting data from Celsius to Fahrenheit...")
            self.tempdf = mtemp.convertCtoF(self.tempdf)
            logging.info("Data converted to Fahrenheit.")
        except Exception as e:
            logging.error(f"Failed to load or convert temperature data: {e}")
            self.tempdf = None
        input(">Press Enter")

    def load_gps_data(self):
        """Loads GPS data."""
        try:
            logging.info("Loading GPS data...")
            self.gpsdf = mtemp.load_gps(self.test_num, self.tests)
            logging.info("GPS data loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load GPS data: {e}")
            self.gpsdf = None
        input(">Press Enter")

    def load_irrh_data(self):
        """Loads IR/RH data."""
        try:
            logging.info("Loading IR/RH data...")
            self.irrhdf = mtemp.load_ir_daq(self.test_num, self.tests)
            logging.info("IR/RH data loaded successfully.")
            logging.info("Converting voltage to IR...")
            self.irrhdf = mtemp.convertVtoIR(self.irrhdf)
            logging.info("Data converted to IR.")
            if self.tests[self.test_num][6] == 2:
                logging.info("Converting voltage to RH...")
                self.irrhdf = mtemp.convertVtoRH(self.irrhdf)
                logging.info("Data converted to RH.")
        except Exception as e:
            logging.error(f"Failed to load or convert IR/RH data: {e}")
            self.irrhdf = None
        input(">Press Enter")

    def merge_and_spatially_enable_data(self):
        """Merges and spatially enables GPS and other data."""
        try:
            logging.info("Merging and spatially enabling data...")
            self.gdf = mtemp.spatially_enable_data(self.tempdf, self.gpsdf, self.irrhdf)
            logging.info("Data merged and spatially enabled successfully.")
        except Exception as e:
            logging.error(f"Failed to merge and spatially enable data: {e}")
            self.gdf = None
        input(">Press Enter")

    def merge_temp_ir(self):
        """Merges temperature and IR data into a DataFrame."""
        try:
            logging.info("Merging temperature and IR data...")
            self.df = mtemp.merge_sensors(self.tempdf, self.irrhdf)
            logging.info("Temperature and IR data merged successfully.")
        except Exception as e:
            logging.error(f"Failed to merge temperature and IR data: {e}")
            self.df = None
        input(">Press Enter")

    def plot_time_series(self):
        """Plots the merged data in a time series."""
        try:
            logging.info("Preparing to plot time series...")
            plot_options = self.get_plot_options()
            dataframe = self.gdf if self.gdf is not None else self.df
            if dataframe is None:
                logging.error("No DataFrame available for plotting.")
                input(">Press Enter")
                return
            mtemp.timeseries(
                output_folder=self.output,
                dataframe=dataframe,
                temp=plot_options['temp'],
                ir=plot_options['ir'],
                rh=plot_options['rh'],
                b=plot_options['b'],
                yminmax=plot_options['yminmax'],
                timeframe=plot_options['timeframe']
            )
            logging.info("Plot generated successfully.")
        except Exception as e:
            logging.error(f"An error occurred while plotting time series: {e}")
        input(">Press Enter")

    def plot_vertical_heatmap(self):
        """Plots a vertical heatmap."""
        try:
            logging.info("Plotting vertical heatmap...")
            # Implement the actual plotting logic using mtemp module
            # Example: mtemp.vertical_heatmap(self.output, self.df or self.gdf)
            logging.warning("Vertical heatmap plotting is not yet implemented.")
        except Exception as e:
            logging.error(f"An error occurred while plotting vertical heatmap: {e}")
        input(">Press Enter")

    def plot_scatter_plot(self):
        """Plots a scatter plot."""
        try:
            logging.info("Plotting scatter plot...")
            # Implement the actual plotting logic using mtemp module
            # Example: mtemp.scatter_plot(self.output, self.df or self.gdf)
            logging.warning("Scatter plot plotting is not yet implemented.")
        except Exception as e:
            logging.error(f"An error occurred while plotting scatter plot: {e}")
        input(">Press Enter")

    def plot_dot_map(self):
        """Plots a dot map."""
        try:
            logging.info("Plotting dot map...")
            # Implement the actual plotting logic using mtemp module
            # Example: mtemp.dot_map(self.output, self.gdf)
            logging.warning("Dot map plotting is not yet implemented.")
        except Exception as e:
            logging.error(f"An error occurred while plotting dot map: {e}")
        input(">Press Enter")

    def plot_heatmap(self):
        """Plots a heatmap."""
        try:
            logging.info("Plotting heatmap...")
            # Implement the actual plotting logic using mtemp module
            # Example: mtemp.heatmap(self.output, self.gdf)
            logging.warning("Heatmap plotting is not yet implemented.")
        except Exception as e:
            logging.error(f"An error occurred while plotting heatmap: {e}")
        input(">Press Enter")

    def display_data(self):
        """Displays all data in use."""
        data_frames = [
            ("GeoDataFrame", self.gdf),
            ("Sensor DataFrame", self.df),
            ("RTD DataFrame", self.tempdf),
            ("IR/RH DataFrame", self.irrhdf),
            ("GPS DataFrame", self.gpsdf)
        ]
        for name, df in data_frames:
            if df is not None:
                print(f"\n{name}")
                print("-" * len(name))
                print(df.head())
                print(f"\n{name} columns:")
                print(df.columns.tolist())
                print("------------------------------")
        logging.info("Data display complete.")

    def quit_program(self):
        """Exits the program."""
        logging.info("Exiting the M-TEMP system. Goodbye!")
        sys.exit(0)

    def get_plot_options(self):
        """Gathers user inputs for plotting options."""
        options = {
            'temp': True,
            'ir': False,
            'rh': False,
            'b': True,
            'yminmax': None,
            'timeframe': None
        }
        try:
            temp_input = input("Do you want RTDs? (y/n): ").strip().lower()
            options['temp'] = temp_input == 'y'

            ir_input = input("Do you want IR? (y/n): ").strip().lower()
            options['ir'] = ir_input == 'y'

            rh_input = input("Do you want RH? (y/n): ").strip().lower()
            options['rh'] = rh_input == 'y'

            b_input = input("Do you want 'b' RTDs? (y/n): ").strip().lower()
            options['b'] = b_input == 'y'

            yminmax_input = input("Do you want to set y-axis min and max? (y/n): ").strip().lower()
            if yminmax_input == 'y':
                ymin = float(input("Y min: ").strip())
                ymax = float(input("Y max: ").strip())
                options['yminmax'] = (ymin, ymax)

            timeframe_input = input("Do you have a timeframe? (y/n): ").strip().lower()
            if timeframe_input == 'y':
                timestart_str = input("Enter start time as HH:MM:SS: ").strip()
                timeend_str = input("Enter end time as HH:MM:SS: ").strip()
                # Assuming the index is datetime and contains the date
                start_datetime = pd.to_datetime(timestart_str, format="%H:%M:%S", errors='coerce')
                end_datetime = pd.to_datetime(timeend_str, format="%H:%M:%S", errors='coerce')
                if pd.isna(start_datetime) or pd.isna(end_datetime):
                    logging.error("Invalid time format. Timeframe will not be applied.")
                else:
                    options['timeframe'] = (start_datetime, end_datetime)
        except ValueError as e:
            logging.error(f"Invalid input: {e}")
        return options

def main():
    """Main entry point of the program."""
    processor = MTempProcessor()
    processor.clear_screen()
    processor.display_ascii_title()
    logging.info("Welcome to the M-TEMP system.")
    logging.info("Excel sheet loaded automatically.")
    input(">Press Enter to Start")
    processor.main_menu()

if __name__ == "__main__":
    main()
