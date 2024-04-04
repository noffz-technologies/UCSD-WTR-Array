"""
    Socket curve plot script
    Tested on MDO3000/4000C and 2/3/4/5(B)/6(B) series platform scopes
    Socket instrument communication program for curve? waveform query
    Only a single channel source allowed per curve query in this example
    Socket communication is more difficult to debug and lacks the robustness of VISA/VXI-11.

    Disclaimer:
    Some modifications may be required to run without error.
    This program is a proof of concept and provided "As-is".
    Its contents may be altered to suit different applications.

    Tested using Python v3.10
    Author: Steve Guerrero
"""
import socket
import sys
import numpy as np      # numpy version v1.23.1
import matplotlib.pyplot as plt        # (optional) used for plots, version 3.5.2

""" Methods for instrument object, socket connection, and data transfer """


class SocketInstr(object):
    def __init__(self, host, port, timeout=10):     # Initialization of socket object

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # AF_INET = IPV4, SOCK_STREAM = TCP
        try:
            self.socket.connect((host, port))   # Attempt connection to instrument (IPV4 address, socket port)
            self.socket.setblocking(False)      # non-blocking is best for asynchronous communication
            self.socket.settimeout(timeout)     # default timeout set to 10 seconds
        except socket.error as msg:             # error checking
            print("Error: could not create socket")
            print("Description: " + str(msg))
            sys.exit()

    def disconnect(self):   # socket closing function

        self.socket.shutdown(socket.SHUT_RDWR)  # informs server (instrument) prior to closure
        self.socket.close()

    def read(self):         # Socket data receive method, decodes to ASCII string

        try:
            resp = self.socket.recv(1024)       # default 1KiB
            while resp[-1:] != b'\n':           # check for EOL linefeed char
                resp += self.socket.recv(1024)  # receive and append more data
            resp = resp.decode('latin_1').strip()   # convert Bytes to string
        except socket.error as msg:
            print("Error: unable to recv()")
            print("Description: " + str(msg))
            sys.exit()
        return resp  # return response from instrument

    def write(self, scpi):  # Socket Write SCPI to instrument method, encodes string to bytes

        scpi = '{}\n'.format(scpi).encode('latin_1')    # convert string to Bytes prior to send
        try:
            self.socket.sendall(scpi)   # send Bytes
        except socket.error as msg:
            print("Error: send() failed")
            print("Description: " + str(msg))
            sys.exit()

    def query(self, scpi):  # Socket Query SCPI from instrument, references both write and read functions

        self.write(scpi)
        resp = self.read()
        return resp         # return response from instrument

    def read_bytes(self, n_bytes):  # reads raw data, requires byte length as argument

        raw_data = bytearray(n_bytes)  # Initialize byte array of N-length
        mv = memoryview(raw_data)     # object 'raw_data' spliced for much faster manipulation. 'mv' points to 'raw_data' object in memory
        try:
            while n_bytes:     # While data remains
                c = self.socket.recv_into(mv, n_bytes)   # recv n_bytes into mv, c = num bytes recvd
                mv = mv[c:]     # appends n_bytes received to mv object
                n_bytes -= c    # removes number of bytes read from mv
        except socket.error as msg:
            print("Error: unable to recv()")
            print("Description: " + str(msg))
            sys.exit()
        return raw_data

    def clear(self):        # behaves like pyvisa device.clear(), used for debugging
        self.write('!d')    # device clear flag for supported instruments


""" Instrument specific functions """


def read_bin_wave(instr):   # Binary block header parsing and waveform reading function, references read_bytes(), struct.unpack may work best for multi-source Curve?

    # first we need to read and parse binary block header by format represented by example: (#72500000[250M Bytes of binary data]\n)
    bin_header = instr.read_bytes(15)           # first 15 Bytes should contain all binary block header information in any case, tested to 1 Gpts
    byte_len = int(bin_header.decode('latin_1').strip()[1], base=16)        # number of characters representing number of bytes
    num_bytes = int(bin_header.decode('latin_1').strip()[2:byte_len + 2])   # num_bytes of waveform data to read after header
    rem = bin_header[byte_len + 2:]             # remaining bytes from header to be included in returned waveform data

    wave_data = rem + instr.read_bytes(num_bytes - len(rem) + 1)    # '+1' accounts for linefeed character
    return wave_data[:-1]   # return waveform data without linefeed character


"""     Main Application    """
if __name__ == "__main__":

    # user preferences
    plots = True        # set False to disable plots, program is slow to plot 100M+ sample waveforms
    save2file = False   # Set True to enable raw waveform data save to file
    chan_sel = 1        # channel/source to acquire waveform data, only 1 source allowed per curve query

    scope = SocketInstr('192.168.1.31', 4000, timeout=10)  # Default port = 4000

    scope.write('*cls')         # clears event status register
    ID = scope.query('*idn?')   # query scope ID
    print("Connected to:", ID)

    # curve configuration, queries entire record
    scope.write('data:encdg SRIBINARY')                 # signed integer, may need to modify program for other encoding schemes
    scope.write('data:source CH{:d}'.format(chan_sel))  # only a single source is allowed per curve query
    scope.write('data:start 1')
    acq_record = int(scope.query('horizontal:recordlength?'))
    scope.write('data:stop {}'.format(acq_record))
    scope.write('wfmoutpre:byt_n 2')            # 2 Bytes per sample, needs to reflect numpy data type below
    r = scope.query('*opc?')    # sync

    scope.write('curve?')   # initiates waveform data dump
    bin_wave = read_bin_wave(scope)  # reads binary waveform data

    if save2file is True:   # dumps raw waveform data to file in directory where script was ran
        file = open('wave_data.bin', "wb")
        file.write(bin_wave)
        file.close()

    # retrieve scaling factors for scaled wave plot
    if plots is True:
        pre_trig_record = int(scope.query('wfmoutpre:pt_off?'))
        t_scale = float(scope.query('wfmoutpre:xincr?'))
        t_sub = float(scope.query('wfmoutpre:xzero?'))  # sub-sample trigger correction
        v_scale = float(scope.query('wfmoutpre:ymult?'))  # volts / level
        v_off = float(scope.query('wfmoutpre:yzero?'))  # reference voltage
        v_pos = float(scope.query('wfmoutpre:yoff?'))  # reference position (level)

    r = scope.query('*opc?')    # sync

    # error checking
    print('Event Status Register:', scope.query('*esr?'))
    print("All event codes/messages:", scope.query('allev?'))   # displays event codes and messages, also clears EVMsg? queue

    scope.clear()   # clear buffer, used for debugging.

    # close socket
    scope.disconnect()

    if plots is True:
        # create scaled vectors

        bin_wave = np.frombuffer(bin_wave, dtype='h')  # converts raw byte array to np array for easier handling
        # 'h' signed 2-Byte int, 'b' signed 1-Byte int. C-type data type formats: https://docs.python.org/3/library/struct.html#format-characters

        # horizontal (time)
        total_time = t_scale * acq_record
        t_start = (-pre_trig_record * t_scale) + t_sub
        t_stop = t_start + total_time
        scaled_time = np.linspace(t_start, t_stop, num=acq_record, endpoint=False)

        # vertical (voltage)
        unscaled_wave = np.array(bin_wave, dtype='double')  # data type conversion
        scaled_wave = (unscaled_wave - v_pos) * v_scale + v_off

        # plotting
        plt.plot(scaled_time, scaled_wave)
        plt.title('Channel {:d}'.format(chan_sel))  # plot label
        plt.xlabel('Time (seconds)')  # x label
        plt.ylabel('Amplitude (volts)')  # y label
        print("look for plot window...")
        plt.show()
