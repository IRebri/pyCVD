# -*- coding: utf-8 -*-

"""
This file contains Thread wrapper to gain analog data from sensors - Mass Flow Controller and Vacuum Pressure sensor.

pyCVD is free software: you can redistribute it and/or modify
it under the terms of the....License
"""

from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants
import logging
# from gui.gascontrol.pyCVDconstants import Consts
from pyCVDconstants import Consts

class MonitoringModule:
    # Create the signal
    # TODO implement Pressure sensor

    def __init__(self, board):
        """
        Constructor
        @param board: pyMata object
        @return: no return value
        """

        self.board = board
        logging.debug('Init monitoring module')
        self.gas1MFCoutputVal = 0.0
        self.gas2MFCoutputVal = 0.0
        self.gasPressureVal = 0.0

    def getAnalogData(self):

        """
        Getter to get analog data (gas flow data from MFControllers and pressure) from board
        @return: tuple of data (int, int, float) = (gasFlow1, gasFlow2, Pressure) in Volts
        """

        data = ()

        self.gas1MFCoutputVal = self.board.analog_read(Consts.AR_NANO_PINS['gas1 real flow, analog_read pin']) / 1024 * 5
        # logging.debug("{}, pin {}".format(self.gas1MFCoutputVal,BoardPins.NANOPINS['gas1 real flow, analog_read pin']))
        data += (self.gas1MFCoutputVal),

        self.gas2MFCoutputVal = self.board.analog_read(Consts.AR_NANO_PINS['gas2 real flow, analog_read pin']) / 1024 * 5
        # logging.debug("{}, pin {}".format(self.gas2MFCoutputVal, BoardPins.NANOPINS['gas2 real flow, analog_read pin']))
        data += (self.gas2MFCoutputVal),


        self.gasPressureVal = self.board.analog_read(Consts.AR_NANO_PINS['pressure value, analog_read pin']) / 1024 * 5
        # logging.debug("{}, pin {}".format(self.gasPressureVal, BoardPins.NANOPINS['pressure value, analog_read pin']))
        data +=(self.gasPressureVal),

        return data


        # self.count += 1
        # self.gas1MFCoutputVal += self.count
        # self.gas2MFCoutputVal += self.count
        # self.gasPressureVal += self.count


if __name__ == "__main__":
    board = PyMata3(arduino_wait = 5)
    board.set_pin_mode(Consts.AR_NANO_PINS['gas1 real flow, analog_read pin'], Constants.ANALOG)
    board.set_pin_mode(Consts.AR_NANO_PINS['gas2 real flow, analog_read pin'], Constants.ANALOG)
    board.set_pin_mode(Consts.AR_NANO_PINS['pressure value, analog_read pin'], Constants.ANALOG)
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(thread)d:%(levelname)s:%(message)s")
    playInstance = MonitoringModule(board)
    while True:
        logging.debug(playInstance.getAnalogData())
        board.sleep(1)
