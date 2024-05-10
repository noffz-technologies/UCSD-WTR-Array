import numpy as np
import nidaqmx

# Define a lookup table mapping RF and IF combinations to binary values for digital output lines.
lookup_table = {
    'ALLOFF': (0, 0, 0, 0, 0),
    'ALLON': (1, 1, 1, 1, 1),
    'RF1IF1': (1, 0, 0, 0, 0),
    'RF1IF2': (1, 0, 0, 1, 0),
    'RF1IF3': (1, 0, 0, 0, 1),
    'RF1IF4': (1, 0, 0, 1, 1),
    'RF2IF1': (0, 1, 0, 0, 0),
    'RF2IF2': (0, 1, 0, 1, 0),
    'RF2IF3': (0, 1, 0, 0, 1),
    'RF2IF4': (0, 1, 0, 1, 1),
    'RF3IF1': (1, 1, 0, 0, 0),
    'RF3IF2': (1, 1, 0, 1, 0),
    'RF3IF3': (1, 1, 0, 0, 1),
    'RF3IF4': (1, 1, 0, 1, 1),
    'RF4IF1': (0, 0, 1, 0, 0),
    'RF4IF2': (0, 0, 1, 1, 0),
    'RF4IF3': (0, 0, 1, 0, 1),
    'RF4IF4': (0, 0, 1, 1, 1),
    'RF5IF1': (1, 0, 1, 0, 0),
    'RF5IF2': (1, 0, 1, 1, 0),
    'RF5IF3': (1, 0, 1, 0, 1),
    'RF5IF4': (1, 0, 1, 1, 1)
}


class DIOController:
    def __init__(self, resource_name):
        # Initialize a task for communication with the NI DAQ hardware.
        self.task = nidaqmx.Task()
        self.num_ports = 8  # Total number of ports on the DAQ device.
        self.num_lines_per_port = 5  # Number of digital output lines per port.
        self.num_total_lines = self.num_ports * self.num_lines_per_port  # Total number of digital output lines.
        self.lines = np.zeros(self.num_total_lines, dtype=bool)  # Initialize an array to store line values.

        # Add digital output channels to the task for each line.
        for DIOport in range(self.num_ports):
            for DIOline in range(self.num_lines_per_port):
                self.task.do_channels.add_do_chan(f'{resource_name}/port{DIOport}/line{DIOline}',
                                                  line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE)

    def set_line_value(self, port, line, value):
        # Calculate the index of the line in the lines array.
        line_index = port * self.num_lines_per_port + line
        # Set the value of the line.
        self.lines[line_index] = value

    def set_rf_if_values(self, rf_if_combination):
        # Retrieve the binary values corresponding to the given RF and IF combination from the lookup table.
        if rf_if_combination not in lookup_table:
            raise ValueError(f"Invalid RF and IF combination: {rf_if_combination}")
        rf_if_values = lookup_table[rf_if_combination]
        # Set the line values for all ports based on the RF and IF values.
        for port in range(self.num_ports):
            for line, value in enumerate(rf_if_values):
                self.set_line_value(port, line, value)

    def set_all_ports_rf_if_values(self, rf_if_combination):
        # Set the RF and IF values for all ports using the set_rf_if_values method.
        for port in range(self.num_ports):
            self.set_rf_if_values(rf_if_combination)

    def update_digital_output(self):
        # Write the line values to the digital output.
        self.task.write(self.lines, auto_start=True)

    def read_written_values(self):
        # Read the written values from the digital output.
        read_data = self.task.read(number_of_samples_per_channel=1)
        return read_data

    def close(self):
        # Close the task.
        self.task.close()


# Example usage:
if __name__ == "__main__":
    # Create an instance of DAQController.
    daq = DIOController("USB-6509")
    try:
        # Set RF and IF combination for all ports.
        daq.set_all_ports_rf_if_values('ALLOFF')
        # Update the digital output.
        daq.update_digital_output()

        # Read back the written values.
        written_values = daq.read_written_values()
        print("Written Values:")
        # Iterate over ports and lines to print the written values.
        for port in range(daq.num_ports):
            for line in range(daq.num_lines_per_port):
                index = port * daq.num_lines_per_port + line
                value = written_values[index]
                print(f"Port {port}, Line {line}: {value}")

    finally:
        # Close the DAQ controller.
        daq.close()