#region imports
import numpy as np
import PyQt5.QtWidgets as qtw
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from pathlib import Path
import sys
import os

# Import the UI form created by Qt Designer (converted via pyuic5)
from pump import Ui_Form
from Pump_MVC import Pump_Controller
#endregion

#region class definitions
class PumpCurve_GUI_Class(Ui_Form, qtw.QWidget):
    """
    This class defines the GUI for the Pump Curve application.
    It inherits from both the auto-generated Ui_Form and the QWidget class.
    Handles layout setup, signal-slot connections, and interaction with the MVC controller.
    """
    def __init__(self):
        """
        Constructor that sets up the GUI, initializes plot canvas, and connects signals.
        """
        super().__init__()
        self.setupUi(self)  # Setup widgets defined in Qt Designer
        self.AssignSignals()  # Connect button signals to their respective functions
        self.FilePath = os.getcwd()  # Default file path is current working directory
        self.FileName = ""  # Placeholder for full file name

        # Matplotlib figure and canvas setup
        self.canvas = FigureCanvasQTAgg(Figure(figsize=(5, 3), tight_layout=True, frameon=True))
        self.ax = self.canvas.figure.add_subplot()  # Add a plot to the canvas

        # Embed canvas into the layout defined in the UI
        self.GL_Output.addWidget(self.canvas, 5, 0, 1, 4)

        # Initialize pump controller (MVC structure)
        self.myPump = Pump_Controller()
        self.setViewWidgets()  # Link view widgets to the controller

        # Show GUI on screen
        self.show()

    def AssignSignals(self):
        """
        Connect GUI button signals to their corresponding slot methods.
        """
        self.PB_Exit.clicked.connect(self.Exit)
        self.CMD_Open.clicked.connect(self.ReadAndCalculate)

    def setViewWidgets(self):
        """
        Pass necessary widgets from the GUI to the pump controller.
        These widgets are used for output display and plotting.
        """
        w = [self.LE_PumpName, self.LE_FlowUnits, self.LE_HeadUnits,
             self.LE_HeadCoefs, self.LE_EffCoefs, self.ax, self.canvas]
        self.myPump.setViewWidgets(w)

    def ReadAndCalculate(self):
        """
        Opens a file dialog, reads the selected pump data file,
        and triggers the controller to import and process the data.

        :return: True if file read and calculation were successful, otherwise False.
        """
        if self.OpenFile():
            with open(self.FileName, 'r') as f1:
                data = f1.readlines()
            self.myPump.ImportFromFile(data)
            return True
        else:
            return False

    def OpenFile(self):
        """
        Opens a QFileDialog for selecting a pump data file.
        Updates internal file path and display widget with the selected file name.

        :return: True if a file was selected, False otherwise.
        """
        fname = qtw.QFileDialog.getOpenFileName(self, "Open Pump Data File", self.FilePath,
                                                "Text Files (*.txt);;All Files (*)")
        file_selected = len(fname[0]) > 0
        if file_selected:
            self.FileName = fname[0]  # full file path
            self.FilePath = str(Path(fname[0]).parents[0]) + '/'  # update directory
            self.TE_Filename.setText(self.FileName)  # show file name in GUI
        return file_selected

    def Exit(self):
        """
        Slot method to exit the application when Exit button is clicked.
        """
        qapp.exit()
#endregion

#region function definitions
def main():
    """
    Launch the pump curve GUI application. Entry point when running the script directly.
    """
    PumpCurve_GUI = PumpCurve_GUI_Class()
    qapp.exec_()
#endregion

#region function calls
if __name__ == "__main__":
    qapp = qtw.QApplication(sys.argv)  # create Qt application object
    main()  # run the main GUI application
#endregion
