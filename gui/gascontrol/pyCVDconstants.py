class Consts:

    AR_NANO_PINS = {
        'board led': 13,
        # 'big pump On/Off' : 13,
        # 'small pump on/Off' : 13,
        # 'outlet valve to big pump': 13,
        # 'outlet valve to small pump': 13,
        # 'inlet valve': 13,
        # 'exhaust valve for small pump' : 13

        'big pump On/Off': 2,
        'outlet valve to big pump': 3,
        'small pump on/Off': 4,
        'outlet valve to small pump': 5,
        'trap valve, extra outlet valve to small pump': 6,  # tightly connected to exhaust valve
        'exhaust valve for small pump': 7,
        'inlet valve': 8,
        'gas1 real flow, analog_read pin': 1,  # A1 = 15 - no need specify A, pyMata makes it automatically when board.analog_read
        'gas2 real flow, analog_read pin': 2,  # A2 = 16 - no need specify A, pyMata makes it automatically when board.analog_read
        'pressure value, analog_read pin': 3,  # A0 = 14 - no need specify A, pyMata makes it automatically when board.analog_read
        'gas1 real flow setter, pwm pin' : 10,
        'gas2 real flow setter, pwm pin': 11

    # A0 = 14 - no need specify A, pyMata makes it automatically when board.analog_read
        # 'SDA, i2c data line': 4, # For hardware purpose - A4 - no need specify, pyMata makes it automatically
        # 'SCL, i2c clock line' : 5 # For hardware purpose - A5 - no need specify, pyMata makes it automatically
    }

    AR_UNO_PINS = {
        'board led': 13,
    }

    GAS1 = {
        'lph to volts coefficient': 0.5625,  # e.g. 1 liter per hour == 0.5625 volts
        'sccm to volts coefficient': 0.03375 # e.g. 1 sm^3 per minute == 0.03375 volts
    }

    GAS2 = {
        'lph to volts coefficient': 3.1,     # e.g. 1 liter per hour == 3.1 volts
        'sccm to volts coefficient': 0.186  # e.g. 1 sm^3 per minute == 0.186 volts
    }

    PRESSURE = {
        'kPa to volts coefficient': 0.21524796447076242,  # e.g. 1 kPa == 4.362*0.04934616333580064 volts (4.362 not 4 because of hardware features)
        '0-101,325 kPa to volts coefficient': 0.04934616333580064,  # e.g. 1 kPa == 0.04934616333580064 volts
        'torr to volts coefficient': 0.006578947368421052  # e.g. 1 torr == 0.006578947368421052 volts
    }