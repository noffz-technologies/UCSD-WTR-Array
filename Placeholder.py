import nidaqmx
import pyvisa

# General function (logging_enable, error_enable, test_number, date, etc.)

# Initialize sequence (notify user to validate power supply procedure)
#   Power supply
    # Enable power
    # Validate power on rails is appropriate

# -------------------------------------------------------------------------------
# Instrument control parameters read from config.ini ()
#   Synths
    # Center frequency
    # Power

#   Downconverters
    # Values from table to set filters
    # Use the IF Name and RF tags to set values

#   VSGs
    # Cal signal file
    # Center frequency
    # Power
    # Symbol rate

#   Scopes
    # Center Frequency
    # Bandwidth
    # Sample rate
    # Collection length
    # Collection time

    # *Sync precision time

# Data Collection
    # Start
    # Store data + metadata from instruments

# -------------------------------------------------------------------------------
# Cleanup
    # Disable power