# -*- coding: utf-8 -*-

"""
This file contains GUI - Window and Dialogs.

pyCVD is free software: you can redistribute it and/or modify
it under the terms of the....License
"""

from PyQt5 import QtWidgets
from PyQt5 import uic
import os
import sys

class GasControlMainWindow(QtWidgets.QMainWindow):
    """ Create the Mainwindow based on the corresponding *.ui file. """

    def __init__(self):
        """
        Constructor
        @return: no return value
        """
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        # ui_file = os.path.join(this_dir, 'ui_gascontrol.ui')
        ui_file = os.path.join(this_dir, 'ui_gascontrol_small.ui')

        # Load it
        super(GasControlMainWindow, self).__init__()
        uic.loadUi(ui_file, self)
        self.connectActions()
        self.show()

    def connectActions(self):
        """
        Method connecting all Actions(including buttons firing and etc.) with class or instance methods
        @return: no return value
        """
        self.actionExit.triggered.connect(self.close)


class GasControlSettingDialog(QtWidgets.QDialog):
    """ Create the SettingsDialog window, based on the corresponding *.ui file.
    Gas coefficient tables for MassFlowControllers see http://mfc.engr.arizona.edu/documents/MFC%20Correction.pdf
    """

    def __init__(self):
        """
        Constructor
        @return: no return value
        """
        self.numberOfGases = 2  # initial value of gases
        self.comboBox1Index = 0  # initial value of combobox index (of gases)

        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_gc_settings.ui')
        super(GasControlSettingDialog, self).__init__()
        uic.loadUi(ui_file, self)

        self.update_settings()
        self.connectActions()

        # self.show()


    def connectActions(self):
        """
        Method connecting all Actions(including buttons firing and etc.) with class or instance methods
        @return: no return value
        """
        self.accepted.connect(self.update_settings)
        self.rejected.connect(self.keep_former_settings)


    def update_settings(self):
        """
        Update/set instance variable according to Settings gui. Fires after pressing OK button (see connectActions)
        @return: no return value
        """
        self.numberOfGases = int(self.ComBoxnumberOfGases.currentText())
        self.comboBox1Index = int(self.ComBoxnumberOfGases.currentIndex())
        # logging.debug("Hi from Settings dialog!, self.ComBoxnumberOfGases.currentText() - ".format(int(self.ComBoxnumberOfGases.currentText())))

    def keep_former_settings(self):
        """
        Reload/set Settings GUI forms according to instance variable. Fires after pressing Cancel button (see connectActions)
        @return: no return value
        """
        self.ComBoxnumberOfGases.setCurrentIndex(self.comboBox1Index)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    mw = GasControlMainWindow()
    sd = GasControlSettingDialog()
    sys.exit(app.exec_())