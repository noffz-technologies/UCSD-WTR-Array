import time
import configparser
from BNC845M import BNC845M
from DIOController import DIOController
from NGP800PowerSupply import NGP800PowerSupply
from SMW200A import SMW200A
from TektronixMSO68B import TektronixMSO68B
import logging
import ast

# Set up logging configuration
logging.basicConfig(filename='logs/instrument.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def set_instrument_parameters(dwell_center_freq):
    # Define default values
    lo1, lo2, rfif = None, None, None

    # Define conditions and outputs for each frequency range
    if 500 <= dwell_center_freq <= 1000:
        lo1, lo2, rfif = 4600, 5000, "RF1IF1"
    elif 1000 < dwell_center_freq <= 1500:
        lo1, lo2, rfif = 5100, 5000, "RF1IF1"
    elif 1500 < dwell_center_freq <= 2000:
        lo1, lo2, rfif = 5600, 5000, "RF1IF1"
    elif 2000 < dwell_center_freq <= 2500:
        lo1, lo2, rfif = 6100, 5000, "RF1IF1"
    elif 2500 < dwell_center_freq <= 3000:
        lo1, lo2, rfif = 9500, 7900, "RF2IF3"
    elif 3000 < dwell_center_freq <= 3500:
        lo1, lo2, rfif = 10000, 7900, "RF2IF3"
    elif 3500 < dwell_center_freq <= 4000:
        lo1, lo2, rfif = 10500, 7900, "RF2IF3"
    elif 4000 < dwell_center_freq <= 4500:
        lo1, lo2, rfif = 11000, 7900, "RF2IF3"
    elif 4500 < dwell_center_freq <= 5000:
        lo1, lo2, rfif = 11500, 7900, "RF2IF3"
    elif 5000 < dwell_center_freq <= 5500:
        lo1, lo2, rfif = 9000, 4900, "RF2IF3"
    elif 5500 < dwell_center_freq <= 6000:
        lo1, lo2, rfif = 9500, 4900, "RF3IF1"
    elif 6000 < dwell_center_freq <= 6500:
        lo1, lo2, rfif = 10000, 4900, "RF3IF1"
    elif 6500 < dwell_center_freq <= 7000:
        lo1, lo2, rfif = 10500, 4900, "RF3IF1"
    elif 7000 < dwell_center_freq <= 7500:
        lo1, lo2, rfif = 11000, 4900, "RF3IF1"
    elif 7500 < dwell_center_freq <= 8000:
        lo1, lo2, rfif = 11500, 4900, "RF3IF1"
    elif 8000 < dwell_center_freq <= 8500:
        lo1, lo2, rfif = 12500, 5400, "RF4IF2"
    elif 8500 < dwell_center_freq <= 9000:
        lo1, lo2, rfif = 13000, 5400, "RF4IF2"
    elif 9000 < dwell_center_freq <= 9500:
        lo1, lo2, rfif = 13500, 5400, "RF4IF2"
    elif 9500 < dwell_center_freq <= 10000:
        lo1, lo2, rfif = 14000, 5400, "RF4IF2"
    elif 10000 < dwell_center_freq <= 10500:
        lo1, lo2, rfif = 14500, 5400, "RF4IF2"
    elif 10500 < dwell_center_freq <= 11000:
        lo1, lo2, rfif = 15000, 5400, "RF4IF2"
    elif 11000 < dwell_center_freq <= 11500:
        lo1, lo2, rfif = 15500, 5400, "RF4IF2"
    elif 11500 < dwell_center_freq <= 12000:
        lo1, lo2, rfif = 16000, 5400, "RF4IF2"
    elif 12000 < dwell_center_freq <= 12500:
        lo1, lo2, rfif = 8500, 4900, "RF5IF1"
    elif 12500 < dwell_center_freq <= 13000:
        lo1, lo2, rfif = 9000, 4900, "RF5IF1"
    elif 13000 < dwell_center_freq <= 13500:
        lo1, lo2, rfif = 9500, 4900, "RF5IF1"
    elif 13500 < dwell_center_freq <= 14000:
        lo1, lo2, rfif = 10000, 4900, "RF5IF1"
    elif 14000 < dwell_center_freq <= 14500:
        lo1, lo2, rfif = 9800, 5600, "RF5IF2"
    elif 14500 < dwell_center_freq <= 15000:
        lo1, lo2, rfif = 10300, 5600, "RF5IF2"
    elif 15000 < dwell_center_freq <= 15500:
        lo1, lo2, rfif = 8500, 7900, "RF5IF3"
    elif 15500 < dwell_center_freq <= 16000:
        lo1, lo2, rfif = 9000, 7900, "RF5IF3"
    elif 16000 < dwell_center_freq <= 16500:
        lo1, lo2, rfif = 9500, 7900, "RF5IF3"
    elif 16500 < dwell_center_freq <= 17000:
        lo1, lo2, rfif = 10000, 7900, "RF5IF3"
    elif 17000 < dwell_center_freq <= 17500:
        lo1, lo2, rfif = 9800, 8600, "RF5IF4"
    elif 17500 < dwell_center_freq <= 18000:
        lo1, lo2, rfif = 10300, 8600, "RF5IF4"
    else:
        raise ValueError("Invalid center frequency value")

    return lo1, lo2, rfif


def main():
    # Initialize all potential instrument objects to None.
    # This allows us to safely check if they were initialized later.
    ngp800, smw200a, bnc1, bnc2, dio, tektronix1, tektronix2 = None, None, None, None, None, None, None

    try:
        config = configparser.ConfigParser()
        config.read('config.ini')

        # --- General Config ---
        dwell_spacing = config.getint('General', 'dwell_spacing', fallback=60)

        # --- Initialize Instruments Conditionally ---
        print("Initializing instruments...")

        # NGP800PowerSupply
        if config.has_section('NGP800PowerSupply'):
            try:
                addr = config.get('NGP800PowerSupply', 'resource_address')
                ngp800 = NGP800PowerSupply(f"TCPIP0::{addr}::inst0::INSTR")
                for i in range(1, 4):  # Configure channels 1, 2, 3
                    v = config.getfloat('NGP800PowerSupply', f'Ch{i}_voltage')
                    c = config.getfloat('NGP800PowerSupply', f'Ch{i}_current')
                    ngp800.configure_channel(i, v, c)
                ngp800.start_output()
                logging.info("[OK] NGP800PowerSupply initialized and configured.")
                print("NGP800 Power Supply successfully initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize NGP800PowerSupply: {e}")
                print("Failed to initialize NGP800 Power Supply.")
                ngp800 = None
        else:
            logging.warning("[SKIP] NGP800PowerSupply section not found in config.")
            print("Skipping NGP800 Power Supply: section not found in config.")

        # SMW200A
        if config.has_section('SMW200A'):
            try:
                addr = config.get('SMW200A', 'resource_address')
                smw200a = SMW200A(f"TCPIP0::{addr}::inst0::INSTR")
                logging.info(f"[OK] SMW200A initialized: {smw200a.identify()}")
                print("SMW200A Signal Generator successfully initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize SMW200A: {e}")
                print("Failed to initialize SMW200A Signal Generator")
                smw200a = None
        else:
            logging.warning("[SKIP] SMW200A section not found in config.")
            print("Skipping SMW200A Signal Generator: section not found in config.")

        # BNC845M_1
        if config.has_section('BNC845M_1'):
            try:
                addr = config.get('BNC845M_1', 'resource_address')
                pwr = config.getint('BNC845M_1', 'power_level')
                bnc1 = BNC845M(f"TCPIP0::{addr}::inst0::INSTR")
                bnc1.set_power_level(power_level=pwr)
                logging.info(f"[OK] BNC845M_1 initialized: {bnc1.identify()}")
                print("BNC845M_1 Local Oscillator successfully initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize BNC845M_1: {e}")
                print("Failed to initialize BNC845M_1 Local Oscillator")
                bnc1 = None
        else:
            logging.warning("[SKIP] BNC845M_1 section not found in config.")
            print("Skipping BNC845M_1 Local Oscillator: section not found in config.")

        # BNC845M_2
        if config.has_section('BNC845M_2'):
            try:
                addr = config.get('BNC845M_2', 'resource_address')
                pwr = config.getint('BNC845M_2', 'power_level')
                bnc2 = BNC845M(f"TCPIP0::{addr}::inst0::INSTR")
                bnc2.set_power_level(power_level=pwr)
                logging.info(f"[OK] BNC845M_2 initialized: {bnc2.identify()}")
                print("BNC845M_2 Local Oscillator successfully initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize BNC845M_2: {e}")
                print("Failed to initialize BNC845M_2 Local Oscillator")
                bnc2 = None
        else:
            logging.warning("[SKIP] BNC845M_2 section not found in config.")
            print("Skipping BNC845M_2 Local Oscillator: section not found in config.")

        # DIOController
        if config.has_section('DIOController'):
            input("Switch on junction box switches from left to right. Press Enter to proceed...")
            try:
                name = config.get('DIOController', 'resource_name')
                dio = DIOController(name)
                logging.info(f"[OK] DIOController initialized for {name}.")
                print(f"DIOController successfully initialized for {name}.")
            except Exception as e:
                logging.error(f"Failed to initialize DIOController: {e}")
                print(f"Failed to initialize DIOController: {e}")
                dio = None
        else:
            logging.warning("[SKIP] DIOController section not found in config.")
            print("Skipping DIOController: section not found in config.")

        # TektronixMSO68B_1
        if config.has_section('TektronixMSO68B_1'):
            try:
                addr = config.get('TektronixMSO68B_1', 'resource_address')
                path = config.get('TektronixMSO68B_1', 'settings_path')
                tektronix1 = TektronixMSO68B(f"TCPIP0::{addr}::inst0::INSTR")
                tektronix1.recall_setup(path)
                logging.info(f"[OK] TektronixMSO68B_1 initialized: {tektronix1.identify()}")
                print("TektronixMSO68B_1 Oscilloscope successfully initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize TektronixMSO68B_1: {e}")
                print(f"Failed to initialize TektronixMSO68B_1: {e}")
                tektronix1 = None
        else:
            logging.warning("[SKIP] TektronixMSO68B_1 section not found in config.")
            print("Skipping TektronixMSO68B_1: section not found in config.")

        # TektronixMSO68B_2
        if config.has_section('TektronixMSO68B_2'):
            try:
                addr = config.get('TektronixMSO68B_2', 'resource_address')
                path = config.get('TektronixMSO68B_2', 'settings_path')
                tektronix2 = TektronixMSO68B(f"TCPIP0::{addr}::inst0::INSTR")
                tektronix2.recall_setup(path)
                logging.info(f"[OK] TektronixMSO68B_2 initialized: {tektronix2.identify()}")
                print("TektronixMSO68B_2 Oscilloscope successfully initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize TektronixMSO68B_2: {e}")
                print(f"Failed to initialize TektronixMSO68B_2: {e}")
                tektronix2 = None
        else:
            logging.warning("[SKIP] TektronixMSO68B_2 section not found in config.")
            print("Skipping TektronixMSO68B_2: section not found in config.")

        # --- Main loop for dwells ---

        # Determine which instruments were expected (i.e., present in the config)
        expected_instruments = {
            'SMW200A': smw200a if config.has_section('SMW200A') else 'SKIP',
            'BNC845M_1': bnc1 if config.has_section('BNC845M_1') else 'SKIP',
            'BNC845M_2': bnc2 if config.has_section('BNC845M_2') else 'SKIP',
            'DIOController': dio if config.has_section('DIOController') else 'SKIP',
            'TektronixMSO68B_1': tektronix1 if config.has_section('TektronixMSO68B_1') else 'SKIP',
            'TektronixMSO68B_2': tektronix2 if config.has_section('TektronixMSO68B_2') else 'SKIP',
        }

        # Check for any expected instruments that failed to initialize
        uninitialized = [name for name, obj in expected_instruments.items() if obj is None]

        if uninitialized:
            logging.critical(f"Missing critical instruments: {', '.join(uninitialized)}. Aborting test.")
            print(f"ERROR: Missing critical instruments: {', '.join(uninitialized)}. Aborting test.")
            return  # Exit the main() function before entering the dwell loop

        dwell_sections = [s for s in config.sections() if s.startswith('Dwell_')]
        for dwell_name in dwell_sections:
            try:
                dwell_config = config[dwell_name]
                repeat_count = dwell_config.getint('repeat_count')
                dwell_center_freq = dwell_config.getint('dwell_center_frequency')

                logging.info(f"--- Starting {dwell_name} (x{repeat_count} repeats) ---")

                lo1, lo2, rfif = set_instrument_parameters(dwell_center_freq)

                if bnc1 and bnc2:
                    bnc1.set_frequency(lo1 * 1e6)
                    bnc1.start_output()
                    bnc2.set_frequency(lo2 * 1e6)
                    bnc2.start_output()
                    logging.info(f"BNCs set to LO1={lo1}MHz, LO2={lo2}MHz.")
                    print(f"BNCs set to LO1={lo1}MHz, LO2={lo2}MHz.")

                if dio:
                    dio.set_all_ports_rf_if_values(rfif)
                    dio.update_digital_output()
                    logging.info(f"DIO set for {rfif}.")
                    print(f"DIO set for {rfif}.")

                if smw200a:
                    cal_freq = dwell_config.getint('cal_center_frequency')
                    cal_pwr = dwell_config.getint('cal_power')
                    smw200a.set_frequency(cal_freq * 1e6)
                    smw200a.set_power_level(cal_pwr)
                    smw200a.start_signal()
                    logging.info(f"SMW200A set to {cal_freq}MHz at {cal_pwr}dBm.")
                    print(f"SMW200A set to {cal_freq}MHz at {cal_pwr}dBm.")

                for i in range(repeat_count):
                    logging.info(f"Starting repeat {i + 1}/{repeat_count}...")
                    print(f"Starting {dwell_name} repeat {i + 1}/{repeat_count}...")

                    if tektronix1:
                        ch1 = ast.literal_eval(dwell_config.get('set_channels_1'))
                        sr1 = dwell_config.getint('sample_rate_1')
                        rl1 = dwell_config.getint('record_length_1')
                        tektronix1.set_channels(ch1, "ON")
                        tektronix1.set_sample_rate(sr1)
                        tektronix1.set_record_length(rl1)
                        tektronix1.clipcheck(ch1)
                        tektronix1.force_trigger()
                        logging.info("Tektronix1 triggered.")
                        logging.debug(f"Tektronix1 Events: {tektronix1.query('ALLEV?').strip()}")
                        print(f"Tektronix1 Events: {tektronix1.query('ALLEV?').strip()}")

                    if tektronix2:
                        ch2 = ast.literal_eval(dwell_config.get('set_channels_2'))
                        sr2 = dwell_config.getint('sample_rate_2')
                        rl2 = dwell_config.getint('record_length_2')
                        tektronix2.set_channels(ch2, "ON")
                        tektronix2.set_sample_rate(sr2)
                        tektronix2.set_record_length(rl2)
                        tektronix2.clipcheck(ch2)
                        tektronix2.force_trigger()
                        logging.info("Tektronix2 triggered.")
                        logging.debug(f"Tektronix2 Events: {tektronix2.query('ALLEV?').strip()}")
                        print(f"Tektronix2 Events: {tektronix1.query('ALLEV?').strip()}")

                    time.sleep(dwell_spacing)
            except Exception as e:
                logging.error(f"An error occurred during {dwell_name}: {e}")
                print(f"An error occurred during {dwell_name}: {e}")

    except Exception as e:
        logging.critical(f"A critical error occurred in main execution: {e}")
        print(f"A critical error occurred in main execution: {e}")
    finally:
        # --- Safely shut down and clean up all initialized instruments ---
        logging.info("--- Shutting Down ---")
        input("Switch off junction box switches from right to left. Press Enter to finish...")
        print("Beginning shutdown of instruments...")
        if smw200a is not None: smw200a.stop_signal(); smw200a.close()
        if bnc1 is not None: bnc1.stop_output(); bnc1.close()
        if bnc2 is not None: bnc2.stop_output(); bnc2.close()
        if dio is not None: dio.set_all_ports_rf_if_values("ALLOFF"); dio.update_digital_output(); dio.close()
        if tektronix1 is not None: tektronix1.close()
        if tektronix2 is not None: tektronix2.close()
        if ngp800 is not None: ngp800.stop_output(); ngp800.close()
        logging.info("Cleanup complete. Program finished.")
        print("All instruments shut down. Program complete.")


if __name__ == "__main__":
    main()
