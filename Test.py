import nidaqmx
import pyvisa

# rm = pyvisa.ResourceManager()

# my_instrument = rm.open_resource('TCPIP0::192.168.141.136::inst0::INSTR')

# print(my_instrument.query('*IDN?'))

# from nidaqmx.constants import LineGrouping

# with nidaqmx.Task() as task:

#     task.di_channels.add_di_chan(

#         "USB-6509/port0/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)

#     task.read(number_of_samples_per_channel=2)

rm = pyvisa.ResourceManager()

my_instrument = rm.open_resource('TCPIP0::192.168.141.136::inst0::INSTR')

print(my_instrument.query('*LRN?'))