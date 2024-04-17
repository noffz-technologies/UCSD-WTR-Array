import time
import configparser
from BNC845M import BNC845M
from DIOController import DIOController
from NGP800PowerSupply import NGP800PowerSupply
from SMW200A import SMW200A
from TektronixMSO68B import TektronixMSO68B


def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # General parameters
    general_config = {'dwell_spacing': config.getint('General', 'dwell_spacing')}

    # SMW200A parameters
    smw200a_config = {'resource_address': config.get('SMW200A', 'resource_address'),
                      'power_level': config.getint('SMW200A', 'power_level')}

    # NGP800PowerSupply parameters
    ngp800_config = {'resource_address': config.get('NGP800PowerSupply', 'resource_address'), 'channels': {
        'Ch1': {'voltage': config.getfloat('NGP800PowerSupply', 'Ch1_voltage'),
                'current': config.getfloat('NGP800PowerSupply', 'Ch1_current')},
        'Ch2': {'voltage': config.getfloat('NGP800PowerSupply', 'Ch2_voltage'),
                'current': config.getfloat('NGP800PowerSupply', 'Ch2_current')},
        'Ch3': {'voltage': config.getfloat('NGP800PowerSupply', 'Ch3_voltage'),
                'current': config.getfloat('NGP800PowerSupply', 'Ch3_current')}
    }}

    # BNC845M parameters
    bnc845m_config = {}
    bnc845m_config['BNC845M_1'] = {
        'resource_address': config.get('BNC845M_1', 'resource_address'),
        'power_level': config.getint('BNC845M_1', 'power_level')
    }
    bnc845m_config['BNC845M_2'] = {
        'resource_address': config.get('BNC845M_2', 'resource_address'),
        'power_level': config.getint('BNC845M_2', 'power_level')
    }

    # DIOController parameters
    dio_config = {}
    dio_config['resource_name'] = config.get('DIOController', 'resource_name')

    # TektronixMSO68B parameters
    tektronix_config = {}
    tektronix_config['TektronixMSO68B_1'] = {
        'resource_address': config.get('TektronixMSO68B_1', 'resource_address')
    }
    tektronix_config['TektronixMSO68B_2'] = {
        'resource_address': config.get('TektronixMSO68B_2', 'resource_address')
    }

    # Dwell configurations
    dwells_config = {}
    for section in config.sections():
        if section.startswith('Dwell_'):
            dwell = {}
            dwell['center_frequency'] = config.getint(section, 'center_frequency')
            dwell['set_channels_1'] = eval(config.get(section, 'set_channels_1'))
            dwell['sample_rate_1'] = config.getint(section, 'sample_rate_1')
            dwell['record_length_1'] = config.getint(section, 'record_length_1')
            dwell['set_channels_2'] = eval(config.get(section, 'set_channels_2'))
            dwell['sample_rate_2'] = config.getint(section, 'sample_rate_2')
            dwell['record_length_2'] = config.getint(section, 'record_length_2')
            dwells_config[section] = dwell

    return general_config, smw200a_config, ngp800_config, bnc845m_config, dio_config, tektronix_config, dwells_config


def set_instrument_parameters(center_freq):
    # Define default values
    LO1, LO2, RFIF = None, None, None

    # Define conditions and outputs for each frequency range
    if 500 <= center_freq <= 1000:
        LO1, LO2, RFIF = 4600, 5000, "RF1IF1"
    elif 1000 < center_freq <= 1500:
        LO1, LO2, RFIF = 5100, 5000, "RF1IF1"
    elif 1500 < center_freq <= 2000:
        LO1, LO2, RFIF = 5600, 5000, "RF1IF1"
    elif 2000 < center_freq <= 2500:
        LO1, LO2, RFIF = 6100, 5000, "RF1IF1"
    elif 2500 < center_freq <= 3000:
        LO1, LO2, RFIF = 9500, 7900, "RF2IF3"
    elif 3000 < center_freq <= 3500:
        LO1, LO2, RFIF = 10000, 7900, "RF2IF3"
    elif 3500 < center_freq <= 4000:
        LO1, LO2, RFIF = 10500, 7900, "RF2IF3"
    elif 4000 < center_freq <= 4500:
        LO1, LO2, RFIF = 11000, 7900, "RF2IF3"
    elif 4500 < center_freq <= 5000:
        LO1, LO2, RFIF = 11500, 7900, "RF2IF3"
    elif 5000 < center_freq <= 5500:
        LO1, LO2, RFIF = 9000, 4900, "RF2IF3"
    elif 5500 < center_freq <= 6000:
        LO1, LO2, RFIF = 9500, 4900, "RF3IF1"
    elif 6000 < center_freq <= 6500:
        LO1, LO2, RFIF = 10000, 4900, "RF3IF1"
    elif 6500 < center_freq <= 7000:
        LO1, LO2, RFIF = 10500, 4900, "RF3IF1"
    elif 7000 < center_freq <= 7500:
        LO1, LO2, RFIF = 11000, 4900, "RF3IF1"
    elif 7500 < center_freq <= 8000:
        LO1, LO2, RFIF = 11500, 4900, "RF3IF1"
    elif 8000 < center_freq <= 8500:
        LO1, LO2, RFIF = 12500, 5400, "RF4IF2"
    elif 8500 < center_freq <= 9000:
        LO1, LO2, RFIF = 13000, 5400, "RF4IF2"
    elif 9000 < center_freq <= 9500:
        LO1, LO2, RFIF = 13500, 5400, "RF4IF2"
    elif 9500 < center_freq <= 10000:
        LO1, LO2, RFIF = 14000, 5400, "RF4IF2"
    elif 10000 < center_freq <= 10500:
        LO1, LO2, RFIF = 14500, 5400, "RF4IF2"
    elif 10500 < center_freq <= 11000:
        LO1, LO2, RFIF = 15000, 5400, "RF4IF2"
    elif 11000 < center_freq <= 11500:
        LO1, LO2, RFIF = 15500, 5400, "RF4IF2"
    elif 11500 < center_freq <= 12000:
        LO1, LO2, RFIF = 16000, 5400, "RF4IF2"
    elif 12000 < center_freq <= 12500:
        LO1, LO2, RFIF = 8500, 4900, "RF5IF1"
    elif 12500 < center_freq <= 13000:
        LO1, LO2, RFIF = 9000, 4900, "RF5IF1"
    elif 13000 < center_freq <= 13500:
        LO1, LO2, RFIF = 9500, 4900, "RF5IF1"
    elif 13500 < center_freq <= 14000:
        LO1, LO2, RFIF = 10000, 4900, "RF5IF1"
    elif 14000 < center_freq <= 14500:
        LO1, LO2, RFIF = 9800, 5600, "RF5IF2"
    elif 14500 < center_freq <= 15000:
        LO1, LO2, RFIF = 10300, 5600, "RF5IF2"
    elif 15000 < center_freq <= 15500:
        LO1, LO2, RFIF = 8500, 7900, "RF5IF3"
    elif 15500 < center_freq <= 16000:
        LO1, LO2, RFIF = 9000, 7900, "RF5IF3"
    elif 16000 < center_freq <= 16500:
        LO1, LO2, RFIF = 9500, 7900, "RF5IF3"
    elif 16500 < center_freq <= 17000:
        LO1, LO2, RFIF = 10000, 7900, "RF5IF3"
    elif 17000 < center_freq <= 17500:
        LO1, LO2, RFIF = 9800, 8600, "RF5IF4"
    elif 17500 < center_freq <= 18000:
        LO1, LO2, RFIF = 10300, 8600, "RF5IF4"
    else:
        raise ValueError("Invalid center frequency value")

    return LO1, LO2, RFIF


def main():
    # Read configuration
    general_config, smw200a_config, ngp800_config, bnc845m_config, dio_config, tektronix_config, dwells_config = read_config()

    # # Initialize NGP800PowerSupply
    # ngp800 = NGP800PowerSupply(f"TCPIP0::{ngp800_config['resource_address']}::inst0::INSTR")
    #
    # ngp800.configure_channel(1, ngp800_config['channels']['Ch1']['voltage'],
    #                          ngp800_config['channels']['Ch1']['current'])
    # ngp800.configure_channel(2, ngp800_config['channels']['Ch2']['voltage'],
    #                          ngp800_config['channels']['Ch2']['current'])
    # ngp800.configure_channel(3, ngp800_config['channels']['Ch3']['voltage'],
    #                          ngp800_config['channels']['Ch3']['current'])
    # ngp800.start_output()  # Enable power

    # Initialize SMW200A
    smw200a = SMW200A(f"TCPIP0::{smw200a_config['resource_address']}::inst0::INSTR")
    smw200a.identify()  # Print instrument identification

    # Initialize BNC845M
    bnc1 = BNC845M(f"TCPIP0::{bnc845m_config['BNC845M_1']['resource_address']}::inst0::INSTR")
    bnc1.identify()
    bnc1.set_power_level(power_level=bnc845m_config['BNC845M_1']['power_level'])
    # bnc2 = BNC845M(f"TCPIP0::{bnc845m_config['BNC845M_2']['resource_address']}::inst0::INSTR")
    # bnc2.identify()
    # bnc2.set_power_level(power_level=bnc845m_config['BNC845M_2']['power_level'])

    # Initialize DIOController
    dio = DIOController(dio_config['resource_name'])

    # Initialize TektronixMSO68B
    tektronix1 = TektronixMSO68B(f"TCPIP0::{tektronix_config['TektronixMSO68B_1']['resource_address']}::inst0::INSTR")
    tektronix1.identify()
    # tektronix2 = TektronixMSO68B(f"TCPIP0::{tektronix_config['TektronixMSO68B_2']['resource_address']}::inst0::INSTR")
    # tektronix2.identify()

    # Main loop for dwells
    for dwell_name, dwell_config in dwells_config.items():
        center_freq = dwell_config['center_frequency']
        set_channels_1 = dwell_config['set_channels_1']
        print(set_channels_1)
        sample_rate_1 = dwell_config['sample_rate_1']
        record_length_1 = dwell_config['record_length_1']
        set_channels_2 = dwell_config['set_channels_2']
        print(set_channels_2)
        sample_rate_2 = dwell_config['sample_rate_2']
        record_length_2 = dwell_config['record_length_2']

        # Set parameters for BNC845M
        LO1, LO2, RFIF = set_instrument_parameters(center_freq)
        bnc1.set_frequency(LO1)
        bnc1.start_output()
        # bnc2.set_frequency(LO2)
        # bnc2.start_output()

        # Set digital values
        dio.set_all_ports_rf_if_values(RFIF)    # Set RF and IF combination for all ports.
        dio.update_digital_output()     # Update the digital output.
        written_values = dio.read_written_values()        # Read back the written values.
        print("Written Values:")
        # Iterate over ports and lines to print the written values.
        for port in range(dio.num_ports):
            for line in range(dio.num_lines_per_port):
                index = port * dio.num_lines_per_port + line
                value = written_values[index]
                print(f"Port {port}, Line {line}: {value}")

        # Set parameters for SMW200A
        smw200a.set_frequency(center_freq * 1e6)  # Convert MHz to Hz
        smw200a.set_power_level(smw200a_config['power_level'])

        # Set parameters for TektronixMSO68B
        tektronix1.set_channels(set_channels_1, "ON")
        tektronix1.set_sample_rate(sample_rate_1)
        tektronix1.set_record_length(record_length_1)
        tektronix1.force_trigger()

        # tektronix2.set_channels(set_channels_2, "ON")
        # tektronix2.set_sample_rate(sample_rate_2)
        # tektronix2.set_record_length(record_length_2)
        # tektronix2.force_trigger()

        # Wait for dwell spacing
        time.sleep(general_config['dwell_spacing'])

    # Shut down
    smw200a.stop_signal()
    bnc1.stop_output()
    # bnc2.stop_output()
    dio.set_all_ports_rf_if_values("ALLOFF")
    dio.update_digital_output()

    # Cleanup
    smw200a.close()
    bnc1.close()
    # bnc2.close()
    dio.close()
    tektronix1.close()
    # tektronix2.close()
    # ngp800.stop_output()  # Disable power
    # ngp800.close()


if __name__ == "__main__":
    main()
