# Imports
import mtemp2

### Uncomment out which format to use ###
# Excel Sheet

test_num = 1 # THIS WOULD BE THE ONLY INPUT WITH AN EXCEL SHEET
tests = mtemp2.load_excelsheet()
folder, file = mtemp2.load_test(test_num, tests)


# Explicit Path
'''
folder = 'path/to/folder'
file = 'path/to/file'
'''

def main():
    headers = mtemp2.get_headers(folder, file)
    daqdf = mtemp2.load_temp_daq(folder, file, headers)
    mtemp2.timeseries(daqdf) #THIS HAS A BUNCH MORE PARAMETERS, REFER TO MODULE

if __name__ == "__main__":
    main()
