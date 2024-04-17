import pyvisa


class NGP800PowerSupply:
    def __init__(self, resource_name):
        """
        Initialize the Rohde & Schwarz NGP800 power supply.

        Args:
            resource_name (str): VISA resource name (e.g., 'TCPIP0::192.168.1.100::inst0::INSTR')
        """
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(resource_name)
        self.instrument.timeout = 5000  # Set a reasonable timeout (in milliseconds)

    def identify(self):
        """Query and print the instrument identification."""
        idn = self.instrument.query("*IDN?")
        print(f"Instrument identification: {idn.strip()}")

    def configure_channel(self, channel, voltage, current):
        """
        Configure the specified channel with the given voltage and current.

        Args:
            channel (int): Channel number (1, 2, or 3)
            voltage (float): Voltage in volts
            current (float): Current in amps
        """
        self.instrument.write(f"INST:SEL CH{channel}")
        self.instrument.write(f"VOLT {voltage:.6f}")
        self.instrument.write(f"CURR {current:.6f}")

    def start_output(self):
        """Start the output of all channels."""
        self.instrument.write(":OUTP ON")
        print("Output started for all channels")

    def stop_output(self):
        """Stop the output of all channels."""
        self.instrument.write(":OUTP OFF")
        print("Output stopped for all channels")

    def close(self):
        """Close the instrument connection."""
        self.instrument.close()


# Example usage:
if __name__ == "__main__":
    ngp800 = NGP800PowerSupply(resource_name="TCPIP0::192.168.1.100::inst0::INSTR")
    ngp800.identify() # Print resource to validate connection
    ngp800.configure_channel(channel=1, voltage=6, current=1)  # Configure channel 1
    ngp800.configure_channel(channel=2, voltage=6, current=1)  # Configure channel 2
    ngp800.configure_channel(channel=3, voltage=12, current=3)  # Configure channel 3
    ngp800.start_output()  # Start the output for all channels
    # Do something with the output...
    ngp800.stop_output()  # Stop the output for all channels
    ngp800.close()  # Close the connection
