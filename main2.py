# Imports
import mtemp

### Uncomment out which format to use ###
# Excel Sheet
'''
test_num = 0 # THIS WOULD BE THE ONLY INPUT WITH AN EXCEL SHEET
tests = mtemp.load_excelsheet()
folder, file = mtemp.load_test()
'''

# Explicit Path
folder = 'path/to/folder'
file = 'path/to/file'

headers = mtemp.get_headers(folder, file)
daqdf = mtemp.load_temp_daq(folder, file, headers)
mtemp.timeseries(daqdf) #THIS HAS A BUNCH MORE PARAMETERS, REFER TO MODULE
