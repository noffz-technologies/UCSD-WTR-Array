import nidaqmx
import pyvisa

# User should specify a center frequency value in config.ini between 500 and 18000 where every 500 units corresponds in a table to center frequency and power of two BNC845M and a string input for DIOController. There will be 35 rows in this table.
# General function (logging_enable, error_enable, test_number, date, etc.)

# Initialize sequence (notify user to validate power supply procedure)
#   NGP800PowerSupply (one instance)
    # Enable power
    # Prompt the user as a warning if the voltage and current do not match predefined values

#   Instrument pyvisa initialization
    # Open connection to all instruments, specify ip address for each in config.ini
    # identify instruments to verify connection

# -------------------------------------------------------------------------------
# Instrument control parameters read from config.ini ()
#   BNC845M (two instances)
    # Center frequency and power from table

#   DIOController (one instance)
    # string input from table

#   SMW200A (one instance)
    # Center frequency and power level from config.ini

#   TektronixMSO68B (two instances) run in a loop every x seconds from config.ini. Every iteration will use new channels, sample rate, and record length from config.ini
    # Set channels
    # Set Sample rate
    # Set Record length
    # Force trigger

# -------------------------------------------------------------------------------
# Cleanup
    # Close instances to instruments except power supply
    # Disable power
    # Close connection to power supply