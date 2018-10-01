Installation guide for pyCVD
============================
Example (01.10.2018):
- new Yepo notebook with installed Windows 10 and Python 3.6 (Anaconda bundle)
- non official Arduino-Nano board (2017)

1. Install Arduino IDE on computer
2. Plug In board and let Windows to install driver (additional COM port should appear in OS)
3. In Arduino IDE (this case Arduino 1.8.7 (Windows Store 1.8.15.0)):
	- 3a. select proper Board, Processor, Port in Tools menu, e.g. Tools>Board>Processor:..>ATmega328P (Old Bootloader)
	- 3b. open sketch File>Examples>Firmata>StandardFirmata and load on board
4. clone pyCVD on ["github/..."](https://github.com/IRebri/pyCVD.git) - program in Python to control gas mixture flows. In this case folder we clone it in such way that we have C:/pyCVD/gui/gascontrol
5. pyCVD constructed on ["pymata_aio"](https://github.com/MrYsLab/pymata-aio). If you do not have this package you should install it, e.g. in command line (cmd.exe) write "pip install pymata_aio"
6. We will use the "shorcut" in order to run pyCVD:
	- 6a. Move shorcut "plasmaCVD"  from C:/pyCVD/gui/gascontrol/plasmaCVD to any convinient place, e.g. we move it to the Desktop.
	- 6b. Right-click on shortcut>Properties. Make shure that Target properly constracted (it say's "to run cmd.exe", then open folder "C:/pyCVD/gui/gascontrol", and run by "python gascontrol.py")
7. Run the program by clicking on shortcut

P.S.
- In case of troubles, change "C" to "K" in the shortcut target "...\cmd.exe /C..." in order to keep cmd open and read the exceptions.
- you may change shortcut icon by icons from "C:/pyCVD/gui/artsrc/Icons.."

