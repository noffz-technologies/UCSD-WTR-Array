import pyvisa
import time


class PowerSupplyController:
    def __init__(self, address):
        self.rm = pyvisa.ResourceManager()
        self.address = address
        self.instrument = self.rm.open_resource(self.address)

    def set_voltage(self, voltage, channel=1):
        self.instrument.write(f"VOLT {voltage},(@{channel})")

    def set_power(self, power, channel=1):
        self.instrument.write(f"POW {power},(@{channel})")

    def enable_channel(self, channel=1):
        self.instrument.write(f"OUTP:STAT ON,(@{channel})")

    def disable_channel(self, channel=1):
        self.instrument.write(f"OUTP:STAT OFF,(@{channel})")

    def check_output(self, voltage_expected, power_expected, channel=1):
        voltage_actual = float(self.instrument.query(f"MEAS:VOLT? (@{channel})"))
        power_actual = float(self.instrument.query(f"MEAS:POW? (@{channel})"))

        if abs(voltage_actual - voltage_expected) > 0.1:
            print(
                f"Warning: Actual voltage ({voltage_actual}V) does not match expected voltage ({voltage_expected}V) for channel {channel}")

        if abs(power_actual - power_expected) > 0.1:
            print(
                f"Warning: Actual power ({power_actual}W) does not match expected power ({power_expected}W) for channel {channel}")


# Example usage
if __name__ == "__main__":
    # Replace 'TCPIP0::192.168.1.100::inst0::INSTR' with the actual address of your power supply
    power_supply = PowerSupplyController('TCPIP0::192.168.1.100::inst0::INSTR')

    power_supply.set_voltage(5)  # Set voltage to 5V
    power_supply.set_power(10)  # Set power to 10W
    power_supply.enable_channel()  # Enable the channel

    time.sleep(2)  # Wait for the power supply to stabilize

    power_supply.check_output(5, 10)  # Check if output matches expected values

    power_supply.disable_channel()  # Disable the channel
