# Simple File transfer example for Riddick scopes 4/5/6 series, assuming file is located in CWD
# Tested on files as large as 3.2GB, FW1.44

import pyvisa as visa


def get_file_size(file_list_str, filename):  # returns number of bytes from requested filename
    file_list = file_list_str.split(',')
    for entry in file_list:
        parts = entry.split(';')
        if parts[0] == '"' + filename:
            return int(parts[2])
    print("File not found in CWD")
    return -1


# VISA setup
visa_descriptor = 'TCPIP::192.168.141.136::INSTR'
rm = visa.ResourceManager()
scope = rm.open_resource(visa_descriptor)
scope.write_termination = None
scope.read_termination = '\n'
scope.timeout = 15000  # ms
scope.encoding = 'latin_1'  # native encoding for scope

print(scope.query('*IDN?'))  # verifying communication

# Enter filename
filename = 'Tek000_000_ch4.mat'  # large 3.2GB test file, located in current working directory

r = scope.query("FILESystem:LDIR?")  # retrieving table of files from CWD along with num of bytes for each file

num_bytes = get_file_size(r, filename)

# Read file data from instrument

# scope.write('FILESystem:READFile "C:/Users/Tek_Local_Admin/Documents{}"'.format(filename))    # Windows example
scope.write('FILESystem:READFile "C:/{}"'.format(filename))
fileData = scope.read_bytes(num_bytes)

# Save image data to local disk
file = open(filename, "wb")
file.write(fileData)
file.close()
scope.close()
rm.close()
