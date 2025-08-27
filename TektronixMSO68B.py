from datetime import time
import pyvisa


class TektronixMSO68B:
    def __init__(self, visa_address):
        self.visa_address = visa_address
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(visa_address, timeout=15000)  # Adjust timeout as needed
        self.instrument.write_termination = None
        self.instrument.read_termination = '\n'
        self.instrument.encoding = 'latin_1'

    def set_sample_rate(self, sample_rate):
        self.instrument.write(f':HORizontal:MODE:SAMPLERate {sample_rate}')
        self.instrument.query("*OPC?") #make sure operations are complete before continuing
        # Read back the sample rate setting
        response = self.instrument.query(':HORizontal:MODE:SAMPLERate?')
        return response.strip()

    def set_record_length(self, record_length):
        self.instrument.write(f':HORizontal:RECOrdlength {record_length}')
        self.instrument.query("*OPC?") #make sure operations are complete before continuing
        # Read back the record length setting
        response = self.instrument.query(':HORizontal:RECOrdlength?')
        return response.strip()

    def set_channels(self, channels, state):
        valid_channels = set(range(1, 9))
        invalid_channels = [ch for ch in channels if ch not in valid_channels]

        if invalid_channels:
            raise ValueError(f"Invalid channel numbers: {invalid_channels}. Must be 1 to 8.")

        if state not in ["ON", "OFF"]:
            raise ValueError("Invalid state. Must be 'ON' or 'OFF'.")

        # Determine unlisted channels and set them to OFF
        unlisted_channels = valid_channels - set(channels)
        for channel in unlisted_channels:
            command = f"DISplay:GLObal:CH{channel}:STATE OFF"
            self.instrument.write(command)

        # Set specified channels to the desired state
        for channel in channels:
            command = f"DISplay:GLObal:CH{channel}:STATE {state}"
            self.instrument.write(command)

        self.instrument.query("*OPC?") #make sure operations are complete before continuing


    def identify(self):
        return self.instrument.query('*IDN?').strip()

    def close(self):
        self.instrument.close()

    def recall_setup(self, setup_path):
        self.instrument.write(f':RECAll:SETUp "{setup_path}"')
        self.instrument.query("*OPC?")

    def force_trigger(self):
        self.instrument.write("FPANEL:PRESS FORCETRIG")

    def write(self, string):
        self.instrument.write(string)

    def query(self, string):
        return(self.instrument.query(string))

    def clipcheck(self, channels):

        for channel in channels:  # cycle through all active channels

            while int(self.instrument.query(f'ch{channel}:clipping?')):  # if clipping for selected channel is true
                scale = float(self.instrument.query(f'ch{channel}:scale?'))  # check current scale for selected channel
                new_scale = scale * 1.20  # increase vertical scale by 25%
                print(f"Clipping detected, scale changed to {new_scale}")
                for channel in channels:
                    self.instrument.write(f'ch{channel}:scale {new_scale}')  # set new vertical scale
                    self.instrument.query('*opc?')  # sync to make sure scale is changed before next query
                time.sleep()


if __name__ == "__main__":
    visa_address = "TCPIP0::192.168.141.134::inst0::INSTR"  # Replace this with your instrument's VISA address
    mso = TektronixMSO68B(visa_address)
    mso.write("*CLS")  # clear errors in the queue

    # Get information about the device
    instrument_info = mso.identify()
    print(f"Instrument Information: {instrument_info}")
    # mso.recall_setup("C:/SpecAnTest.set")
    channels_to_set_on = [1, 2]

    # Set Channels
    try:
        mso.set_channels(channels=channels_to_set_on, state="ON")
        print(f"Channels {channels_to_set_on} set to ON.")

        # Channels not in the list will be automatically set to OFF
        print(f"Unlisted channels set to OFF.")
    except Exception as e:
        print(f"Error: {str(e)}")

    # Set sample rate to 12.5 MS/s
    sample_rate = mso.set_sample_rate(12500000)
    print(f"Sample Rate set to: {sample_rate} samples/s")

    # Set record length to 1000 points
    record_length = mso.set_record_length(10000000)
    print(f"Record Length set to: {record_length} points")

    # Force trigger
    mso.clipcheck(channels_to_set_on)
    mso.force_trigger()
    print("Trigger forced.")
    mso.query("*ESR?")  # Event status register value
    print(mso.query("ALLEV?"))  # All events, more descriptive for errors detected
    # Close the connection to the instrument
    mso.close()
