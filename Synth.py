import pyvisa


class BNC845M:
    def __init__(self, resource_name):
        """
        Initialize the BNC 845-M instrument.

        Args:
            resource_name (str): VISA resource name (e.g., 'TCPIP0::192.168.141.71::inst0::INSTR')
        """
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(resource_name)
        self.instrument.timeout = 5000  # Set a reasonable timeout (in milliseconds)

    def identify(self):
        """Query and print the instrument identification."""
        idn = self.instrument.query("*IDN?")
        print(f"Instrument identification: {idn.strip()}")

    def set_frequency(self, frequency_hz):
        """
        Set the output frequency of the BNC 845-M.

        Args:
            frequency_hz (float): Frequency in Hz
        """
        self.instrument.write(f":FREQ:CW {frequency_hz:.6f} Hz")
        print(f"Frequency set to {frequency_hz:.6f} Hz")

    def start_output(self):
        """Start the output signal."""
        self.instrument.write(":OUTP ON")
        print("Output started")

    def stop_output(self):
        """Stop the output signal."""
        self.instrument.write(":OUTP OFF")
        print("Output stopped")

    def validate_output(self):
        """Query and print the current output settings."""
        freq = float(self.instrument.query(":FREQ:CW?"))
        output_status = self.instrument.query(":OUTP?")
        print(f"Current frequency: {freq:.6f} Hz")
        print(f"Output status: {output_status.strip()}")

    def close(self):
        """Close the instrument connection."""
        self.instrument.close()


# Example usage:
if __name__ == "__main__":
    bnc = BNC845M(resource_name="TCPIP0::192.168.141.71::inst0::INSTR")
    bnc.identify()  # Print instrument identification
    bnc.set_frequency(frequency_hz=1e9)  # Set frequency to 1 GHz
    bnc.start_output()  # Start the output
    # Do something with the output...
    bnc.validate_output()  # Check current output settings
    input("Press Enter to stop the output...")
    bnc.stop_output()  # Stop the output
    bnc.close()  # Close the connection
