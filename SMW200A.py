import pyvisa
import time


class SMW200A:
    def __init__(self, address):
        self.rm = pyvisa.ResourceManager()
        self.instr = self.rm.open_resource(address)

    def identify(self):
        idn = self.instr.query("*IDN?")
        print(f"Instrument identification: {idn.strip()}")

    def set_frequency(self, freq):
        self.instr.write(f"SOURce:FREQuency:FIXed {freq}Hz")
        print(f"Set frequency to {freq} Hz")

    def set_power_level(self, level):
        self.instr.write(f"SOURce:POWer:LEVel:IMMediate:AMPLitude {level}dBm")
        print(f"Set power level to {level} dBm")

    def start_signal(self):
        self.instr.write("OUTPut:STATe ON")
        print("Signal output started")

    def stop_signal(self):
        self.instr.write("OUTPut:STATe OFF")
        print("Signal output stopped")

    def close(self):
        self.instr.close()


if __name__ == "__main__":
    instrument_address = "TCPIP0::192.168.141.222::inst0::INSTR"  # Replace this with your instrument's IP address
    vsg = SMW200A(instrument_address)
    vsg.identify()  # Print instrument identification

    # Example usage
    frequency = 1000000000  # Frequency in Hz
    power_level = -10  # Power level in dBm

    vsg.set_frequency(frequency)
    vsg.set_power_level(power_level)
    vsg.start_signal()

    # Wait for user input to stop signal
    input("Press Enter to stop the output...")

    vsg.stop_signal()

    # Close connection
    vsg.close()
