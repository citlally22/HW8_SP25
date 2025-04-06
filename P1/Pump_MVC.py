# region imports
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import PyQt5.QtWidgets as qtw

# importing from previous work on least squares fit
from LeastSquares import LeastSquaresFit_Class
# endregion

# region class definitions
class Pump_Model():
    """
    Data container class for the pump model.
    Stores pump name, units, raw data, and results from least squares polynomial fits.
    """
    def __init__(self):
        """Pump_Model constructor initializing all fields to default values."""
        # Basic pump information
        self.PumpName = ""
        self.FlowUnits = ""
        self.HeadUnits = ""

        # Raw data arrays
        self.FlowData = np.array([])
        self.HeadData = np.array([])
        self.EffData = np.array([])

        # Coefficient arrays for curve fits
        self.HeadCoefficients = np.array([])
        self.EfficiencyCoefficients = np.array([])

        # Least squares polynomial fit objects
        self.LSFitHead = LeastSquaresFit_Class()
        self.LSFitEff = LeastSquaresFit_Class()


class Pump_Controller():
    """
    Controls the logic between the model and the view.
    Responsible for importing data, computing polynomial fits, and updating the view.
    """
    def __init__(self):
        """Initialize model and view objects."""
        self.Model = Pump_Model()
        self.View = Pump_View()

    # region functions to modify data of the model
    def ImportFromFile(self, data):
        """
        Reads and parses pump data from a list of strings.
        Initializes units and sends numerical data to be processed.

        :param data: List of lines from the pump data file
        """
        self.Model.PumpName = data[0].strip()
        # data[1] is the units line (usually unused)
        L = data[2].split()
        self.Model.FlowUnits = L[0]
        self.Model.HeadUnits = L[1]

        # Process and fit the remaining numerical data
        self.SetData(data[3:])
        self.updateView()

    def SetData(self, data):
        """
        Parses flow, head, and efficiency values from the data.
        Populates model arrays and performs least squares curve fitting.

        :param data: List of strings, each with three space-separated float values
        """
        # Clear existing data
        self.Model.FlowData = np.array([])
        self.Model.HeadData = np.array([])
        self.Model.EffData = np.array([])

        # Parse each line and store values
        for L in data:
            Cells = L.strip().split()
            self.Model.FlowData = np.append(self.Model.FlowData, float(Cells[0]))
            self.Model.HeadData = np.append(self.Model.HeadData, float(Cells[1]))
            self.Model.EffData = np.append(self.Model.EffData, float(Cells[2]))

        # Perform least squares fitting
        self.LSFit()

    def LSFit(self):
        """
        Computes cubic least squares fits for head and efficiency data.
        Stores results in the model's LSFitHead and LSFitEff objects.
        """
        self.Model.LSFitHead.x = self.Model.FlowData
        self.Model.LSFitHead.y = self.Model.HeadData
        self.Model.LSFitHead.LeastSquares(3)

        self.Model.LSFitEff.x = self.Model.FlowData
        self.Model.LSFitEff.y = self.Model.EffData
        self.Model.LSFitEff.LeastSquares(3)
    # endregion

    # region functions interacting with view
    def setViewWidgets(self, w):
        """
        Pass GUI display widgets to the view for updating.
        :param w: List of widgets [name, units, coefs, axes, canvas]
        """
        self.View.setViewWidgets(w)

    def updateView(self):
        """
        Call the view's update function to refresh GUI with model data.
        """
        self.View.updateView(self.Model)
    # endregion


class Pump_View():
    """
    The View class holds GUI elements (widgets) and displays data.
    Responsible for visual updates and plotting.
    """
    def __init__(self):
        """Initialize widgets and placeholders for canvas and axes."""
        self.LE_PumpName = qtw.QLineEdit()
        self.LE_FlowUnits = qtw.QLineEdit()
        self.LE_HeadUnits = qtw.QLineEdit()
        self.LE_HeadCoefs = qtw.QLineEdit()
        self.LE_EffCoefs = qtw.QLineEdit()
        self.ax = None
        self.canvas = None

    def updateView(self, Model):
        """
        Update all view widgets with values from the model.

        :param Model: Pump_Model instance containing current values
        """
        self.LE_PumpName.setText(Model.PumpName)
        self.LE_FlowUnits.setText(Model.FlowUnits)
        self.LE_HeadUnits.setText(Model.HeadUnits)
        self.LE_HeadCoefs.setText(Model.LSFitHead.GetCoeffsString())
        self.LE_EffCoefs.setText(Model.LSFitEff.GetCoeffsString())
        self.DoPlot(Model)

    def DoPlot(self, Model):
        """
        Plot flow vs head and flow vs efficiency using matplotlib.

        :param Model: Pump_Model instance with data and curve fits
        """
        headx, heady, headRSq = Model.LSFitHead.GetPlotInfo(3, npoints=500)
        effx, effy, effRSq = Model.LSFitEff.GetPlotInfo(3, npoints=500)

        axes = self.ax
        axes.clear()  # Clear previous plot

        # Plot raw head data and fitted curve
        axes.plot(Model.FlowData, Model.HeadData, 'bo', label='Head Data')
        axes.plot(headx, heady, 'b-', label=f'Head Fit (R²={headRSq:.3f})')

        # Plot raw efficiency data and fitted curve
        axes.plot(Model.FlowData, Model.EffData, 'go', label='Efficiency Data')
        axes.plot(effx, effy, 'g-', label=f'Efficiency Fit (R²={effRSq:.3f})')

        # Format plot appearance
        axes.set_title(f"Pump Curve: {Model.PumpName}")
        axes.set_xlabel(f"Flow ({Model.FlowUnits})")
        axes.set_ylabel(f"Head / Efficiency ({Model.HeadUnits}, -)")
        axes.grid(True)
        axes.legend()

        self.canvas.draw()  # Refresh the canvas

    def setViewWidgets(self, w):
        """
        Assign actual GUI widgets to class attributes from provided list.

        :param w: List of widgets [PumpName, FlowUnits, HeadUnits, HeadCoefs, EffCoefs, ax, canvas]
        """
        self.LE_PumpName, self.LE_FlowUnits, self.LE_HeadUnits, self.LE_HeadCoefs, self.LE_EffCoefs, self.ax, self.canvas = w
# endregion


