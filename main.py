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
    general_config = {}
    general_config['dwell_spacing'] = config.getint('General', 'dwell_spacing')

    # SMW200A parameters
    smw200a_config = {}
    smw200a_config['resource_address'] = config.get('SMW200A', 'resource_address')
    smw200a_config['power_level'] = config.getint('SMW200A', 'power_level')

    # NGP800PowerSupply parameters
    ngp800_config = {}
    ngp800_config['resource_name'] = config.get('NGP800PowerSupply', 'resource_name')
    ngp800_config['channels'] = {
        'Ch1': {'voltage': config.getfloat('NGP800PowerSupply', 'Ch1_voltage'),
                'current': config.getfloat('NGP800PowerSupply', 'Ch1_current')},
        'Ch2': {'voltage': config.getfloat('NGP800PowerSupply', 'Ch2_voltage'),
                'current': config.getfloat('NGP800PowerSupply', 'Ch2_current')},
        'Ch3': {'voltage': config.getfloat('NGP800PowerSupply', 'Ch3_voltage'),
                'current': config.getfloat('NGP800PowerSupply', 'Ch3_current')}
    }

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
    center_freq = 1200  # Set a center frequency between 500 and 18000

    # Define conditions and outputs for each frequency range
    if 500 <= center_freq <= 1000:
        LO1, LO2, RFIF = 4600, 5000, "RF1IF1"
    elif 1000 < center_freq <= 1500:
        LO1, LO2, RFIF = 5100, 5500, "RF1IF2"
    elif 1500 < center_freq <= 2000:
        LO1, LO2, RFIF = 5600, 6000, "RF2IF1"
    elif 2000 < center_freq <= 2500:
        LO1, LO2, RFIF = 6100, 6500, "RF2IF2"
    elif 2500 < center_freq <= 3000:
        LO1, LO2, RFIF = 6600, 7000, "RF3IF1"
    elif 3000 < center_freq <= 3500:
        LO1, LO2, RFIF = 7100, 7500, "RF3IF2"
    elif 3500 < center_freq <= 4000:
        LO1, LO2, RFIF = 7600, 8000, "RF4IF1"
    elif 4000 < center_freq <= 4500:
        LO1, LO2, RFIF = 8100, 8500, "RF4IF2"
    elif 4500 < center_freq <= 5000:
        LO1, LO2, RFIF = 8600, 9000, "RF5IF1"
    elif 5000 < center_freq <= 5500:
        LO1, LO2, RFIF = 9100, 9500, "RF5IF2"
    elif 5500 < center_freq <= 6000:
        LO1, LO2, RFIF = 9600, 10000, "RF6IF1"
    elif 6000 < center_freq <= 6500:
        LO1, LO2, RFIF = 10100, 10500, "RF6IF2"
    elif 6500 < center_freq <= 7000:
        LO1, LO2, RFIF = 10600, 11000, "RF7IF1"
    elif 7000 < center_freq <= 7500:
        LO1, LO2, RFIF = 11100, 11500, "RF7IF2"
    elif 7500 < center_freq <= 8000:
        LO1, LO2, RFIF = 11600, 12000, "RF8IF1"
    elif 8000 < center_freq <= 8500:
        LO1, LO2, RFIF = 12100, 12500, "RF8IF2"
    elif 8500 < center_freq <= 9000:
        LO1, LO2, RFIF = 12600, 13000, "RF9IF1"
    elif 9000 < center_freq <= 9500:
        LO1, LO2, RFIF = 13100, 13500, "RF9IF2"
    elif 9500 < center_freq <= 10000:
        LO1, LO2, RFIF = 13600, 14000, "RF10IF1"
    elif 10000 < center_freq <= 10500:
        LO1, LO2, RFIF = 14100, 14500, "RF10IF2"

    return LO1, LO2, RFIF


def initialize_instruments(ngp800_config, smw200a_config, bnc845m_config, dio_config, tektronix_config):
    # Initialize NGP800PowerSupply
    ngp800 = NGP800PowerSupply(ngp800_config['resource_name'])

    # Initialize SMW200A
    smw200a = SMW200A(f"TCPIP0::{smw200a_config['resource_address']}::inst0::INSTR")

    # Initialize BNC845M_1 and BNC845M_2
    bnc845m_1 = BNC845M(f"TCPIP0::{bnc845m_config['BNC845M_1']['resource_address']}::inst0::INSTR")
    bnc845m_2 = BNC845M(f"TCPIP0::{bnc845m_config['BNC845M_2']['resource_address']}::inst0::INSTR")

    # Initialize DIOController
    dio = DIOController(dio_config['resource_name'])

    # Initialize TektronixMSO68B_1 and TektronixMSO68B_2
    tektronix_1 = TektronixMSO68B(f"TCPIP0::{tektronix_config['TektronixMSO68B_1']['resource_address']}::inst0::INSTR")
    tektronix_2 = TektronixMSO68B(f"TCPIP0::{tektronix_config['TektronixMSO68B_2']['resource_address']}::inst0::INSTR")

    return ngp800, smw200a, bnc845m_1, bnc845m_2, dio, tektronix_1, tektronix_2


def control_instruments(ngp800, smw200a, bnc845m_1, bnc845m_2, dio, tektronix_1, tektronix_2, dwells_config):
    # Control NGP800PowerSupply
    ngp800.configure_channel(1, ngp800_config['channels']['Ch1']['voltage'],
                             ngp800_config['channels']['Ch1']['current'])
    ngp800.configure_channel(2, ngp800_config['channels']['Ch2']['voltage'],
                             ngp800_config['channels']['Ch2']['current'])
    ngp800.configure_channel(3, ngp800_config['channels']['Ch3']['voltage'],
                             ngp800_config['channels']['Ch3']['current'])

    # Control SMW200A
    smw200a.set_power_level(smw200a_config['power_level'])

    # Control BNC845M_1 and BNC845M_2
    bnc845m_1.set_frequency(bnc845m_config['BNC845M_1']['frequency'])
    bnc845m_1.set_power_level(bnc845m_config['BNC845M_1']['power_level'])
    bnc845m_2.set_frequency(bnc845m_config['BNC845M_2']['frequency'])
    bnc845m_2.set_power_level(bnc845m_config['BNC845M_2']['power_level'])

    # Control DIOController
    dio.set_rf_if_values(dio_config['rf_if_combination'])
    dio.update_digital_output()

    # Control TektronixMSO68B_1 and TektronixMSO68B_2
    for dwell, settings in dwells_config.items():
        # Set channels, sample rate, and record length for TektronixMSO68B_1
        tektronix_1.set_channels(settings['set_channels_1'], state="ON")
        tektronix_1.set_sample_rate(settings['sample_rate_1'])
        tektronix_1.set_record_length(settings['record_length_1'])
        tektronix_1.force_trigger()

        # Set channels, sample rate, and record length for TektronixMSO68B_2
        tektronix_2.set_channels(settings['set_channels_2'], state="ON")
        tektronix_2.set_sample_rate(settings['sample_rate_2'])
        tektronix_2.set_record_length(settings['record_length_2'])
        tektronix_2.force_trigger()

        # Wait for dwell spacing
        time.sleep(general_config['dwell_spacing'])

    # Additional control logic as needed

def cleanup(ngp800, smw200a, bnc845m_1, bnc845m_2, dio, tektronix_1, tektronix_2):
    # Close connections to instruments
    ngp800.close()
    smw200a.close()
    bnc845m_1.close()
    bnc845m_2.close()
    dio.close()
    tektronix_1.close()
    tektronix_2.close()

    # Disable power supply
    # Logic to disable power supply channels if needed

    # Close connection to power supply
    # Logic to close connection to power supply if needed

def start_bnc(bnc):
    bnc.start_output()

def stop_bnc(bnc):
    bnc.stop_output()

def start_smw200a(smw200a):
    smw200a.start_signal()

def stop_smw200a(smw200a):
    smw200a.stop_signal()


def main():
    # Read configuration
    general_config, smw200a_config, ngp800_config, bnc845m_config, dio_config, tektronix_config, dwells_config = read_config()

    # Initialize NGP800PowerSupply
    ngp800 = NGP800PowerSupply(ngp800_config['resource_name'])
    ngp800.start_output()  # Enable power

    # Initialize SMW200A
    smw200a = SMW200A(smw200a_config['resource_address'])

    # Initialize BNC845M
    bnc1 = BNC845M(bnc845m_config['BNC845M_1']['resource_address'])
    bnc2 = BNC845M(bnc845m_config['BNC845M_2']['resource_address'])

    # Initialize DIOController
    dio = DIOController(dio_config['resource_name'])

    # Initialize TektronixMSO68B
    tektronix1 = TektronixMSO68B(tektronix_config['TektronixMSO68B_1']['resource_address'])
    tektronix2 = TektronixMSO68B(tektronix_config['TektronixMSO68B_2']['resource_address'])

    # Main loop for dwells
    for dwell_name, dwell_config in dwells_config.items():
        center_freq = dwell_config['center_frequency']
        set_channels_1 = dwell_config['set_channels_1']
        sample_rate_1 = dwell_config['sample_rate_1']
        record_length_1 = dwell_config['record_length_1']
        set_channels_2 = dwell_config['set_channels_2']
        sample_rate_2 = dwell_config['sample_rate_2']
        record_length_2 = dwell_config['record_length_2']

        # Set parameters for BNC845M and DIOController
        LO1, LO2, RFIF = set_instrument_parameters(center_freq)
        bnc1.set_frequency(LO1)
        bnc2.set_frequency(LO2)
        dio.set_rf_if_values(RFIF)

        # Set parameters for SMW200A
        smw200a.set_frequency(center_freq * 1e6)  # Convert MHz to Hz
        smw200a.set_power_level(smw200a_config['power_level'])

        # Set parameters for TektronixMSO68B
        tektronix1.set_channels(set_channels_1, "ON")
        tektronix1.set_sample_rate(sample_rate_1)
        tektronix1.set_record_length(record_length_1)
        tektronix1.force_trigger()

        tektronix2.set_channels(set_channels_2, "ON")
        tektronix2.set_sample_rate(sample_rate_2)
        tektronix2.set_record_length(record_length_2)
        tektronix2.force_trigger()

        # Wait for dwell spacing
        time.sleep(general_config['dwell_spacing'])

    # Cleanup
    ngp800.stop_output()  # Disable power
    ngp800.close()
    smw200a.close()
    bnc1.close()
    bnc2.close()
    dio.close()
    tektronix1.close()
    tektronix2.close()


if __name__ == "__main__":
    main()