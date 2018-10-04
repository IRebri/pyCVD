# -*- coding: utf-8 -*-

"""
This is nain currently 'unpleasant' file with builtin
logic (for the first time). It initiate different instances and use them.

pyCVD is free software: you can redistribute it and/or modify
it under the terms of the....License
"""

#TODO make it more elegant

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
import sys
from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants
import logging
import time

# from gui.gascontrol.monitoring_analog_data_module import MonitoringModule
from monitoring_analog_data_module import MonitoringModule

from window_dialogs import GasControlMainWindow, GasControlSettingDialog
# from gui.gascontrol.window_dialogs import GasControlMainWindow, GasControlSettingDialog

# from gui.gascontrol.pyCVDconstants import Consts
from pyCVDconstants import Consts



class GasControlGUI:

    def __init__(self):
        self._mw = GasControlMainWindow()
        self._sd = GasControlSettingDialog()
        self.initEquipmentStates()
        self.initAutoPressureModule()
        self.pinsBoardInit()
        self.connectCrossActions()
        self.updateData()           # is this really needed? Check and remove (just in case)
        self.initMonitorModule()
        self.pressure_tick_counter = 0 # first plugin for decresing presure range current 9,7 - 9.2kPa (10s - SPump is On)... by time ticks


    def initEquipmentStates(self):
        self.isONBPump = False  # physical initial states of equipments - Big pump OFF
        self.isONSPump = False  # Small pump OFF
        self.isONBOutletValve = False  # gas outlet valve for big pump is OFF
        self.isONSOutletValve = False  # gas outlet valve for big pump is OFF
        self.isONInletValve = False  # gas inlet valve
        self.isOpenSPumpExhaustValve = True  # Small pump exhaust (vent) valve

        self.updateGasState(0,0,0)


    def updateGasState(self, val1, val2, val3):                      # fires during init and from monitorModuleTick
        self.gas1MFCoutputVal = val1
        self.gas2MFCoutputVal = val2
        self.gasPressureVal = val3
        self._mw.gas1MFCoutput.setText(str(self.gas1MFCoutputVal))
        self._mw.gas2MFCoutput.setText(str(self.gas2MFCoutputVal))
        self._mw.lineEditPressureActual.setText(str(self.gasPressureVal))
        logging.debug("Hi from GasControlGUI updateGasState(val,val,val)! gas1 = {}, gas2 = {}, Pressure = {}".format(val1, val2, val3))

    def initAutoPressureModule(self):
        self.autoPressureState = False  # initially working mode is manual
        self.TIMER_INTERVAL = 1000 # time in msec #was 2000
        self.autoPressureTimer = QtCore.QTimer()
        self.autoPressureTimer.timeout.connect(self.autoPressureTick)
        self.autoPressureTimer.setInterval(self.TIMER_INTERVAL)

    def pinsBoardInit(self):

        # Uncoment: In case of problems specify port explicitly
        # self.BOARD_COMPORT = "COM4"
        # self.board = PyMata3(com_port=self.BOARD_COMPORT)
        self.board = PyMata3(arduino_wait = 5)

        # TODO uncomment to configure i2c communications
        self.board.i2c_config()

        self.board.set_pin_mode(Consts.AR_NANO_PINS['board led'], Constants.OUTPUT)
        self.board.set_pin_mode(Consts.AR_NANO_PINS['big pump On/Off'], Constants.OUTPUT)
        self.board.set_pin_mode(Consts.AR_NANO_PINS['small pump on/Off'], Constants.OUTPUT)
        self.board.set_pin_mode(Consts.AR_NANO_PINS['outlet valve to big pump'], Constants.OUTPUT)
        self.board.set_pin_mode(Consts.AR_NANO_PINS['outlet valve to small pump'], Constants.OUTPUT)
        self.board.set_pin_mode(Consts.AR_NANO_PINS['inlet valve'], Constants.OUTPUT)
        self.board.set_pin_mode(Consts.AR_NANO_PINS['exhaust valve for small pump'], Constants.OUTPUT)
        self.board.set_pin_mode(Consts.AR_NANO_PINS['trap valve, extra outlet valve to small pump'], Constants.OUTPUT)
        self.board.set_pin_mode(Consts.AR_NANO_PINS['gas1 real flow, analog_read pin'], Constants.ANALOG)
        self.board.set_pin_mode(Consts.AR_NANO_PINS['gas2 real flow, analog_read pin'], Constants.ANALOG)
        self.board.set_pin_mode(Consts.AR_NANO_PINS['pressure value, analog_read pin'], Constants.ANALOG)
        self.board.set_pin_mode(Consts.AR_NANO_PINS['gas1 real flow setter, pwm pin'], Constants.PWM)
        self.board.set_pin_mode(Consts.AR_NANO_PINS['gas2 real flow setter, pwm pin'], Constants.PWM)
        self.initRelayPins()

    def initRelayPins(self):                      # fires during init and before close
        self.board.digital_write(Consts.AR_NANO_PINS['big pump On/Off'], 1) # Relay OFF when pin is HIGH (ON when pin is LOW)
        self.board.digital_write(Consts.AR_NANO_PINS['small pump on/Off'], 1)
        self.board.digital_write(Consts.AR_NANO_PINS['outlet valve to big pump'], 1)
        self.board.digital_write(Consts.AR_NANO_PINS['outlet valve to small pump'], 1)
        self.board.digital_write(Consts.AR_NANO_PINS['inlet valve'], 1)
        self.board.digital_write(Consts.AR_NANO_PINS['exhaust valve for small pump'], 1) # Relay OFF = exhaust OPEN
        self.board.digital_write(Consts.AR_NANO_PINS['trap valve, extra outlet valve to small pump'], 1)

    def initMonitorModule(self):
        self.monitorModule = MonitoringModule(self.board)
        self.MONITOR_TIMER_INTERVAL = 333  # time in msec
        self.monitorTimer = QtCore.QTimer()
        self.monitorTimer.timeout.connect(self.monitorModuleTick)
        self.monitorTimer.setInterval(self.MONITOR_TIMER_INTERVAL)
        self.monitorTimer.start()



        #################################################################
        #                           Actions                             #
        #################################################################
    def connectCrossActions(self):
        self._mw.actionSettings.triggered.connect(self._sd.show)
        self._mw.btnBPump.pressed.connect(self.btnBPumpClicked)
        self._mw.btnSPump.pressed.connect(self.btnSPumpClicked)
        self._mw.btnBigGasOutletValve.pressed.connect(self.btnBOutletValveClicked)
        self._mw.btnSmallGasOutletValve.pressed.connect(self.btnSOutletValveClicked)
        self._mw.btnGasInletValve.pressed.connect(self.btnInletValveClicked)
        self._mw.btnSmallPumpExhaustValve.pressed.connect(self.btnSPumpExhaustValveClicked)
        self._sd.accepted.connect(self.updateData)
        self._sd.rejected.connect(self.keep_formerData)

        # self.autoPressureTimer.timeout.connect(self.autoPressureTick)  #moved to initAutoPressureModule()
        # self.monitorTimer.timeout.connect(self.monitorModuleTick)      #moved to initMonitorModule()

        self._mw.btnSetGasFlow.pressed.connect(self.btnSetGasFlowClicked)
        self._mw.btnAutoKeepPressureConst.pressed.connect(self.btnAutoKeepPressureConstClicked)
        self._mw.actionExit.triggered.connect(self.beforeClose)
        app.aboutToQuit.connect(self.beforeClose)  # hard coded from even app TODO to find m/m,m .  ore elegant way


        #################################################################
        #                     Buttons implementations                   #
        #################################################################
    # TODO implement similar functions for other buttons (Relays)
    def btnSPumpExhaustValveClicked(self):
        if self.isOpenSPumpExhaustValve:
            self.isOpenSPumpExhaustValve = False
            self._mw.statusBar().showMessage("Small pump exhaust valve is set to state OFF")
            self._mw.btnSmallGasOutletValve.setEnabled(True)
            self._mw.btnSPump.setEnabled(True)
            logging.info("SmallPumpExhaustValve OFF")
            self.board.digital_write(Consts.AR_NANO_PINS['exhaust valve for small pump'], 0) # Relay ON when pin is LOW, Relay ON = exhaust CLOSED
            self.board.digital_write(Consts.AR_NANO_PINS['trap valve, extra outlet valve to small pump'], 0) # trap valve (ghost valve) opened after exhaust CLOSED

        else:
            if ((not self.isONSOutletValve) and (not self.isONSPump)):
                self.isOpenSPumpExhaustValve = True
                self._mw.statusBar().showMessage("Small pump exhaust valve is set to state ON")
                self._mw.btnSmallGasOutletValve.setEnabled(False)
                self._mw.btnSPump.setEnabled(False)
                logging.info("SmallPumpExhaustValve ON")
                self.board.digital_write(Consts.AR_NANO_PINS['trap valve, extra outlet valve to small pump'],
                                         1)  # trap valve (ghost valve) closed with exhaust OPENED
                self.board.digital_write(Consts.AR_NANO_PINS['exhaust valve for small pump'], 1) # Relay OFF when pin is HIGH, Relay OFF = exhaust OPENED

            else:
                self._mw.btnSmallPumpExhaustValve.setChecked(True)  # inverse strange behaviour of pyQt... may be it implements GIU one more time after user's method
                self._mw.statusBar().showMessage("Small pump exhaust valve might be opened if Small Pump is OFF and SOutlet is closed")

    def btnInletValveClicked(self):
        if self.isONInletValve:
            self.isONInletValve = False
            self._mw.statusBar().showMessage("Inlet valve is set to state OFF")
            self._mw.btnAutoKeepPressureConst.setEnabled(False)   # the only reason to set autoPressure enabled/disabled
            logging.info("InletValve OFF")
            self.board.digital_write(Consts.AR_NANO_PINS['inlet valve'], 1)
        else:
            self.isONInletValve = True
            self._mw.btnAutoKeepPressureConst.setEnabled(True)   # the only reason to set autoPressure enabled/disabled
            self._mw.statusBar().showMessage("Inlet valve is set to state ON")
            logging.info("InletValve ON")
            self.board.digital_write(Consts.AR_NANO_PINS['inlet valve'], 0)

    def btnSOutletValveClicked(self):
        if self.isONSOutletValve:
            self.isONSOutletValve = False
            self._mw.statusBar().showMessage("Chamber's outlet valve connected to small pump is set to state OFF")
            logging.info("SOutletValve OFF")
            self.board.digital_write(Consts.AR_NANO_PINS['outlet valve to small pump'], 1)
        else:
            if (self.isONSPump):
                self.isONSOutletValve = True
                self._mw.statusBar().showMessage("Chamber's outlet valve connected to small pump is set to state ON")
                logging.info("SOutletValve ON")
                self.board.digital_write(Consts.AR_NANO_PINS['outlet valve to small pump'], 0)
            else:
                self._mw.btnSmallGasOutletValve.setChecked(True) # inverse strange behaviour of pyQt
                self._mw.statusBar().showMessage("Small outlet valve might be opened if Small Pump is ON")
                logging.debug("self.isONSOutletValve -------------status------------------- {}".format(str(self.isONSOutletValve)))

    def btnBOutletValveClicked(self):
        if self.isONBOutletValve:
            self.isONBOutletValve = False
            self._mw.statusBar().showMessage("Chamber's outlet valve connected to big pump is set to state OFF")
            logging.info("BOutletValve OFF")
            self.board.digital_write(Consts.AR_NANO_PINS['outlet valve to big pump'], 1)
        else:
            if (self.isONBPump):
               self.isONBOutletValve = True
               self._mw.statusBar().showMessage("Chamber's outlet valve connected to big pump is set to state ON")
               logging.info("BOutletValve ON")
               self.board.digital_write(Consts.AR_NANO_PINS['outlet valve to big pump'], 0)
            else:
                self._mw.btnBigGasOutletValve.setChecked(True)  # inverse strange behaviour of pyQt
                self._mw.statusBar().showMessage("Big outlet valve might be opened if Big Pump is ON")

    def btnBPumpClicked(self):
        if self.isONBPump and (not self.isONBOutletValve):
            self.isONBPump = False
            self._mw.statusBar().showMessage("Big pump is set to state OFF")
            logging.info("BPump OFF")
            self.board.digital_write(Consts.AR_NANO_PINS['big pump On/Off'], 1)
        elif self.isONBPump and self.isONBOutletValve:
            self._mw.statusBar().showMessage("Big pump might be swithed off only if big outlet valve is OFF")
            self._mw.btnBPump.setChecked(False)  # inverse strange behaviour of pyQt
        else:
            self.isONBPump = True
            self._mw.statusBar().showMessage("Big pump is set to state ON")
            logging.info("BPump ON")
            self.board.digital_write(Consts.AR_NANO_PINS['big pump On/Off'], 0)

    def btnSPumpClicked(self):
        if self.isONSPump and (not self.isONSOutletValve):
            self.isONSPump = False
            self._mw.statusBar().showMessage("Small pump is set to state OFF")
            logging.info("SPump OFF")
            self.board.digital_write(Consts.AR_NANO_PINS['small pump on/Off'], 1)
        elif self.isONSPump and self.isONSOutletValve:
            self._mw.statusBar().showMessage("Small pump might be swithed off only if small outlet valve is OFF")
            self._mw.btnSPump.setChecked(False)  # inverse strange behaviour of pyQt
        else:
            self.isONSPump = True
            self._mw.statusBar().showMessage("Small pump is set to state ON")
            logging.info("SPump ON")
            self.board.digital_write(Consts.AR_NANO_PINS['small pump on/Off'], 0)


    # TODO implement I2C write for 2 MFC
    def btnSetGasFlowClicked(self):
        """
                Setter Voltage 0 to 5V
                @param pin: PWM pin
                @param val: Voltage value
                @return: no return value
        """
        # logging.debug("btnSetGasFlowClicked Not implemented yet! see Desai p215 for I2C")      # see Desai p215
        # self._mw.statusBar().showMessage("'Set gas flow' button clicked. I2C communication started")
        self._mw.statusBar().showMessage("'Set gas flow' button clicked. PWM signal through RCfilter sent to MFCs: gas1 = "+str(self._mw.spinBoxGas1.value())
                                         +" sccm; gas2 = " + str(self._mw.spinBoxGas2.value()) +" sccm")
        self.board.analog_write(Consts.AR_NANO_PINS['gas1 real flow setter, pwm pin'],
                                round(self._mw.spinBoxGas1.value()*Consts.GAS1['sccm to volts coefficient'] * 255 / 5))  # write range (8 bits) 0-255 in Volts
        self.board.sleep(0.05)
        self.board.analog_write(Consts.AR_NANO_PINS['gas2 real flow setter, pwm pin'],
                                round(self._mw.spinBoxGas2.value() * Consts.GAS2['sccm to volts coefficient'] * 255 / 5))  # write range (8 bits) 0-255 in Volts
        self.board.sleep(0.05)

        logging.debug("Set in volts {} and {} ".format((self._mw.spinBoxGas1.value()*Consts.GAS1['sccm to volts coefficient']),
                      (self._mw.spinBoxGas2.value() * Consts.GAS2['sccm to volts coefficient'])))      # see Desai p215





    #################################################################
    #                   Pressure control module                     #
    #################################################################

    def btnAutoKeepPressureConstClicked(self):
        logging.debug("btnAutoKeepPressureConstClicked")
        if self.autoPressureState:
            self.autoPressureState = False
            self._mw.statusBar().showMessage("'Keep pressure constant' button clicked. Auto pressure mode is set to state OFF")
            self.autoPressureTimer.stop()
            self.autoPressureTimer.setInterval(self.TIMER_INTERVAL)
            self.autoPressureExtraButtonsEnabled(True)
        else:
            if self.isONBOutletValve:
                self._mw.btnBigGasOutletValve.click()
            if self.isOpenSPumpExhaustValve:
                self._mw.btnSmallPumpExhaustValve.click()
            if self.isONSOutletValve:
                self._mw.btnSmallGasOutletValve.click()
            if (not self.isONSPump):
                self._mw.btnSPump.click()
            self.autoPressureState = True
            self._mw.statusBar().showMessage("'Keep pressure constant' button clicked. Updated some states of modules involved in gas flow. Auto pressure mode is ON")
            #TODO switch ON all needed equipment from any initial state
            self.autoPressureExtraButtonsEnabled(False) # for the first time Disabled almost all meaningful buttons
            logging.debug("Before timer start")
            self.autoPressureTimer.start()
            self.gasPressureSet = float(self._mw.lineEditPressureSet.text())
            logging.debug("After timer start")

    def autoPressureExtraButtonsEnabled(self, isEnable = True):
        """ Disabled (enabled) extra buttons during autoPressure"""
        self._mw.btnGasInletValve.setEnabled(isEnable)
        self._mw.lineEditPressureSet.setEnabled(isEnable)
        self._mw.btnBigGasOutletValve.setEnabled(isEnable)

        self._mw.btnSmallGasOutletValve.setEnabled(isEnable)
        self._mw.btnSmallPumpExhaustValve.setEnabled(isEnable)
        self._mw.btnSPump.setEnabled(isEnable)

    def autoPressureTick(self):
        logging.debug('PressureTick!')
        self.pressure_tick_counter += 1
        #TODO realize pressure control logic (PID +-0.5kPa)
        # if we buy pressure controller (use PID algorithms)
        #  http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/
        #  https://playground.arduino.cc/Code/PIDLibrary
        #  http://codinglab.blogspot.ru/2016/04/online-pdi-trainer.html

        # logging.debug('PressureTick! {} {} {}'.format(type(self.gasPressureVal), type(self.gasPressureSet), type(self.isONSOutletValve)))


        # Pump condition
        if (float(self.gasPressureVal) > (self.gasPressureSet + 0.1)) and (not self.isONSOutletValve): #was +0.2
            self.pressure_tick_counter = -1000
            self._mw.btnSmallGasOutletValve.setEnabled(True)
            logging.debug('PressureTick! {}'.format('in first'))
            self._mw.btnSmallGasOutletValve.click()
            self._mw.btnSmallGasOutletValve.setEnabled(False)

#       stop pump condition
        #  if (float(self.gasPressureVal) < (self.gasPressureSet - 0.3)) and (self.isONSOutletValve):
        if (float(self.gasPressureVal) < (self.gasPressureSet + 0.1)) and (self.isONSOutletValve) and (self.pressure_tick_counter > (-998)):
            self.pressure_tick_counter = 0
            self._mw.btnSmallGasOutletValve.setEnabled(True)
            self._mw.btnSmallGasOutletValve.click()
            logging.debug('PressureTick! {}'.format('in second'))
            self._mw.btnSmallGasOutletValve.setEnabled(False)

        if self.pressure_tick_counter > 10000:  # not to overflow
            self.pressure_tick_counter = 0


            #################################################################
            #                   Pressure control module                     #
            #################################################################

    def monitorModuleTick(self):
        logging.debug(self.monitorModule.getAnalogData())
        logging.debug("Hello from MonitorModuleTick")
        monitorData = self.monitorModule.getAnalogData()    #(gasFlow1, gasFlow2, Pressure) in Volts
        self.updateGasState(int(monitorData[0]/Consts.GAS1['sccm to volts coefficient']),int(monitorData[1]/Consts.GAS2['sccm to volts coefficient']), "{:.2f}".format(float(monitorData[2])/Consts.PRESSURE['kPa to volts coefficient']))


            #################################################################
            #                Respond on Setting Dialog                      #
            #################################################################

    def updateData(self):
        """ Updates data according to Settings dialog"""
        self._mw.backGroundImage.setPixmap(QtGui.QPixmap("../../artsrc/backgrounds/CVD_"+str(self._sd.numberOfGases)+"ballons.png"))
        self._mw.statusBar().showMessage("Data were update according Settings Dialog")
        # logging.debug("gascontrol got accept info from _sd (setting dialog) or during __init__.  Gascontrol executes corresponding updateData method. It gets number of gases = {}".format(str(self._sd.numberOfGases)))
        
    def keep_formerData(self):
        pass
        # logging.debug("gascontrol got reject information from _sd (setting dialog) and implemented in keep_formerData method")

    def beforeClose(self):
        logging.debug("User has clicked the red x on the main window or activated exit Action")
        self.initRelayPins()
        self.board.shutdown()



if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(thread)d:%(levelname)s:%(message)s")
    #  logging.basicConfig(level=logging.DEBUG, filename="{}device.log".format(time.strftime("%Y%m%d%Hh%Mm%Ss")),
    #                     format="%(asctime)s:%(thread)d:%(levelname)s:%(message)s")
    app = QtWidgets.QApplication(sys.argv)
    ex = GasControlGUI()
    sys.exit(app.exec_())

    # TODO might be play around with Python state machine (fysom or transitions)
    # see more https://www.talyarkoni.org/blog/2014/10/29/yet-another-python-state-machine-and-why-you-might-care/
    # people more likely used this (according to "likes") https://github.com/pytransitions/transitions than this (used in Qudi) https://github.com/mriehl/fysom