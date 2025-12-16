import numpy as np
import numpy.ma as ma

# Configure matplotlib backend before importing matplotlib - prevent popup windows
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to prevent popup windows

import pygimli as pg
from pygimli.viewer.mpl.colorbar import cmapFromName
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTabWidget, QSplitter, QLabel
from PyQt5.QtCore import Qt

# Try different import approaches
try:
    # Try relative import first (when part of a package)
    from .visualization_utils import InversionVisualizations
except ImportError:
    try:
        # Try absolute import next (when package is installed)
        from pyckster.visualization_utils import InversionVisualizations
    except ImportError:
        # Finally try direct import (when in same directory)
        from visualization_utils import InversionVisualizations

class InversionVisualizer(QMainWindow):
    def __init__(self, refrac_manager, inversion_params=None, parent=None):
        super().__init__(parent)
        self.refrac_manager = refrac_manager
        self.inversion_params = inversion_params
        
        # Create the visualization object
        self.visualizer = InversionVisualizations(refrac_manager, inversion_params)
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Inversion Results Visualization")
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        self.resize(int(screen_size.width() * 0.9), int(screen_size.height() * 0.9))  # Resize to 90% of the screen size
        
        # Main widget and layout
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        mainLayout = QVBoxLayout(mainWidget)
        
        # Create tab widget for multiple views
        tabWidget = QTabWidget()
        mainLayout.addWidget(tabWidget)

        # Tab 1: Data and Inversion
        dataInvTab = QWidget()
        dataInvLayout = QVBoxLayout(dataInvTab)

        # Create a main splitter for horizontal division
        dataInvMainSplitter = QSplitter(Qt.Horizontal)
        dataInvLayout.addWidget(dataInvMainSplitter)

        # Left splitter for top-left and bottom-left subplots
        dataInvLeftSplitter = QSplitter(Qt.Vertical)
        dataInvMainSplitter.addWidget(dataInvLeftSplitter)

        # Right splitter for top-right and bottom-right subplots
        dataInvRightSplitter = QSplitter(Qt.Vertical)
        dataInvMainSplitter.addWidget(dataInvRightSplitter)

        # Top-left: Setup with observed traveltimes
        dataInvObservedWidget = QWidget()
        dataInvObservedLayout = QVBoxLayout(dataInvObservedWidget)
        dataInvObservedTitle = QLabel("Observed Data Setup")
        dataInvObservedTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        dataInvObservedLayout.addWidget(dataInvObservedTitle)
        dataInvObservedFig = Figure(figsize=(5, 4), dpi=100)
        dataInvObservedCanvas = FigureCanvas(dataInvObservedFig)
        dataInvObservedToolbar = NavigationToolbar(dataInvObservedCanvas, self)
        dataInvObservedLayout.addWidget(dataInvObservedToolbar)
        dataInvObservedLayout.addWidget(dataInvObservedCanvas)
        dataInvObservedAx = dataInvObservedFig.add_subplot(111)
        self.plotSetup(dataInvObservedAx, color_by='observed', time_in_ms=True)
        dataInvLeftSplitter.addWidget(dataInvObservedWidget)

        # Bottom-left: Traveltime curves
        dataInvCurvesWidget = QWidget()
        dataInvCurvesLayout = QVBoxLayout(dataInvCurvesWidget)
        dataInvCurvesTitle = QLabel("Traveltime Curves")
        dataInvCurvesTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        dataInvCurvesLayout.addWidget(dataInvCurvesTitle)
        dataInvCurvesFig = Figure(figsize=(5, 4), dpi=100)
        dataInvCurvesCanvas = FigureCanvas(dataInvCurvesFig)
        dataInvCurvesToolbar = NavigationToolbar(dataInvCurvesCanvas, self)
        dataInvCurvesLayout.addWidget(dataInvCurvesToolbar)
        dataInvCurvesLayout.addWidget(dataInvCurvesCanvas)
        dataInvCurvesAx = dataInvCurvesFig.add_subplot(111)
        self.plotTraveltimeCurves(dataInvCurvesAx)
        dataInvLeftSplitter.addWidget(dataInvCurvesWidget)

        # Top-right: Topography
        dataInvTopoWidget = QWidget()
        dataInvTopoLayout = QVBoxLayout(dataInvTopoWidget)
        dataInvTopoTitle = QLabel("Survey Topography")
        dataInvTopoTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        dataInvTopoLayout.addWidget(dataInvTopoTitle)
        dataInvTopoFig = Figure(figsize=(5, 4), dpi=100)
        dataInvTopoCanvas = FigureCanvas(dataInvTopoFig)
        dataInvTopoToolbar = NavigationToolbar(dataInvTopoCanvas, self)
        dataInvTopoLayout.addWidget(dataInvTopoToolbar)
        dataInvTopoLayout.addWidget(dataInvTopoCanvas)
        dataInvTopoAx = dataInvTopoFig.add_subplot(111)
        self.plotTopography(dataInvTopoAx)
        dataInvRightSplitter.addWidget(dataInvTopoWidget)

        # Bottom-right: Parameter information
        dataInvInfoWidget = QWidget()
        dataInvInfoLayout = QVBoxLayout(dataInvInfoWidget)
        dataInvInfoTitle = QLabel("Inversion Parameters")
        dataInvInfoTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        dataInvInfoLayout.addWidget(dataInvInfoTitle)
        dataInvInfoFig = Figure(figsize=(5, 4), dpi=100)
        dataInvInfoCanvas = FigureCanvas(dataInvInfoFig)
        dataInvInfoToolbar = NavigationToolbar(dataInvInfoCanvas, self)
        dataInvInfoLayout.addWidget(dataInvInfoToolbar)
        dataInvInfoLayout.addWidget(dataInvInfoCanvas)
        dataInvInfoAx = dataInvInfoFig.add_subplot(111)
        self.plotParameterInfo(dataInvInfoAx)
        dataInvRightSplitter.addWidget(dataInvInfoWidget)

        # Add the tab to the tab widget 
        tabWidget.addTab(dataInvTab, "Data and Inversion")
        
        # Tab 2: Models
        modelsTab = QWidget()
        modelsLayout = QVBoxLayout(modelsTab)
        
        # Create a main splitter for horizontal division
        modelsMainSplitter = QSplitter(Qt.Horizontal)
        modelsLayout.addWidget(modelsMainSplitter)
        
        # Left splitter for top-left and bottom-left subplots
        modelsLeftSplitter = QSplitter(Qt.Vertical)
        modelsMainSplitter.addWidget(modelsLeftSplitter)
        
        # Right splitter for top-right and bottom-right subplots
        modelsRightSplitter = QSplitter(Qt.Vertical)
        modelsMainSplitter.addWidget(modelsRightSplitter)
        
        # Top-left: Starting Model
        startingModelWidget = QWidget()
        startingModelLayout = QVBoxLayout(startingModelWidget)
        startingModelTitle = QLabel("Starting model")
        startingModelTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        startingModelLayout.addWidget(startingModelTitle)
        startingFig = Figure(figsize=(5, 4), dpi=100)
        startingCanvas = FigureCanvas(startingFig)
        startingToolbar = NavigationToolbar(startingCanvas, self)
        startingModelLayout.addWidget(startingToolbar)
        startingModelLayout.addWidget(startingCanvas)
        startingAx = startingFig.add_subplot(111)
        self.plotStartingModel(startingAx)
        modelsLeftSplitter.addWidget(startingModelWidget)
        
        # Bottom-left: Inverted Model
        invertedModelWidget = QWidget()
        invertedModelLayout = QVBoxLayout(invertedModelWidget)
        invertedModelTitle = QLabel("Inverted model")
        invertedModelTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        invertedModelLayout.addWidget(invertedModelTitle)
        invertedFig = Figure(figsize=(5, 4), dpi=100)
        invertedCanvas = FigureCanvas(invertedFig)
        invertedToolbar = NavigationToolbar(invertedCanvas, self)
        invertedModelLayout.addWidget(invertedToolbar)
        invertedModelLayout.addWidget(invertedCanvas)
        invertedAx = invertedFig.add_subplot(111)
        self.plotInvertedModel(invertedAx)
        modelsLeftSplitter.addWidget(invertedModelWidget)
        
        # Top-right: Model with Rays
        raysModelWidget = QWidget()
        raysModelLayout = QVBoxLayout(raysModelWidget)
        raysModelTitle = QLabel("Inverted model with ray paths")
        raysModelTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        raysModelLayout.addWidget(raysModelTitle)
        raysFig = Figure(figsize=(5, 4), dpi=100)
        raysCanvas = FigureCanvas(raysFig)
        raysToolbar = NavigationToolbar(raysCanvas, self)
        raysModelLayout.addWidget(raysToolbar)
        raysModelLayout.addWidget(raysCanvas)
        raysAx = raysFig.add_subplot(111)
        self.plotModelWithRays(raysAx)
        modelsRightSplitter.addWidget(raysModelWidget)
        
        # Bottom-right: Coverage Masked Model
        coverageWidget = QWidget()
        coverageLayout = QVBoxLayout(coverageWidget)
        coverageTitle = QLabel("Inverted model with coverage mask")
        coverageTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        coverageLayout.addWidget(coverageTitle)
        coverageFig = Figure(figsize=(5, 4), dpi=100)
        coverageCanvas = FigureCanvas(coverageFig)
        coverageToolbar = NavigationToolbar(coverageCanvas, self)
        coverageLayout.addWidget(coverageToolbar)
        coverageLayout.addWidget(coverageCanvas)
        coverageAx = coverageFig.add_subplot(111)
        self.plotMaskedModel(coverageAx)
        modelsRightSplitter.addWidget(coverageWidget)
        
        # Add the models tab to the tab widget
        tabWidget.addTab(modelsTab, "Models")
        
        # Tab 3: Traveltimes
        traveltimesTab = QWidget()
        traveltimesLayout = QHBoxLayout(traveltimesTab)
        
        # Create a splitter for adjustable panels
        ttMainSplitter = QSplitter(Qt.Horizontal)
        traveltimesLayout.addWidget(ttMainSplitter)

        # Create a splitter for adjustable panels (left side)
        ttLeftSplitter = QSplitter(Qt.Vertical)
        ttMainSplitter.addWidget(ttLeftSplitter)        

        # Create a splitter for adjustable panels (right side)
        ttRightSplitter = QSplitter(Qt.Vertical)
        ttMainSplitter.addWidget(ttRightSplitter)
        
        # Traveltime curves figure
        ttCurvesWidget = QWidget()
        ttCurvesLayout = QVBoxLayout(ttCurvesWidget)
        ttCurvesTitle = QLabel("Traveltime curves")
        ttCurvesTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        ttCurvesLayout.addWidget(ttCurvesTitle)
        ttCurvesFig = Figure(figsize=(5, 4), dpi=100)
        ttCurvesCanvas = FigureCanvas(ttCurvesFig)
        ttCurvesToolbar = NavigationToolbar(ttCurvesCanvas, self)
        ttCurvesLayout.addWidget(ttCurvesToolbar)
        ttCurvesLayout.addWidget(ttCurvesCanvas)
        ttCurvesAx = ttCurvesFig.add_subplot(111)
        self.plotTraveltimeCurves(ttCurvesAx)
        ttLeftSplitter.addWidget(ttCurvesWidget)

        # Rays with travel time difference figure
        ttRaysWidget = QWidget()
        ttRaysLayout = QVBoxLayout(ttRaysWidget)
        ttRaysTitle = QLabel("Rays with traveltime difference")
        ttRaysTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        ttRaysLayout.addWidget(ttRaysTitle)
        ttRaysFig = Figure(figsize=(5, 4), dpi=100)
        ttRaysCanvas = FigureCanvas(ttRaysFig)
        ttRaysToolbar = NavigationToolbar(ttRaysCanvas, self)
        ttRaysLayout.addWidget(ttRaysToolbar)
        ttRaysLayout.addWidget(ttRaysCanvas)
        ttRaysAx = ttRaysFig.add_subplot(111)
        self.plotRaysWithTravelTimeDiff(ttRaysAx, time_in_ms=True, cmap='bwr')
        ttLeftSplitter.addWidget(ttRaysWidget)
        
        # observed vs simulated figure
        ttComparisonWidget = QWidget()
        ttComparisonLayout = QVBoxLayout(ttComparisonWidget)
        ttComparisonTitle = QLabel("Observed vs simulated traveltimes")
        ttComparisonTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        ttComparisonLayout.addWidget(ttComparisonTitle)
        ttComparisonFig = Figure(figsize=(5, 4), dpi=100)
        ttComparisonCanvas = FigureCanvas(ttComparisonFig)
        ttComparisonToolbar = NavigationToolbar(ttComparisonCanvas, self)
        ttComparisonLayout.addWidget(ttComparisonToolbar)
        ttComparisonLayout.addWidget(ttComparisonCanvas)
        ttComparisonAx = ttComparisonFig.add_subplot(111)
        self.plotTraveltimeComparison(ttComparisonAx)
        ttRightSplitter.addWidget(ttComparisonWidget)

        # Histogram of traveltimes difference
        histogramWidget = QWidget()
        histogramLayout = QVBoxLayout(histogramWidget)
        histogramTitle = QLabel("Histogram of traveltime relative differences")
        histogramTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        histogramLayout.addWidget(histogramTitle)
        histogramFig = Figure(figsize=(5, 4), dpi=100)
        histogramCanvas = FigureCanvas(histogramFig)
        histogramToolbar = NavigationToolbar(histogramCanvas, self)
        histogramLayout.addWidget(histogramToolbar)
        histogramLayout.addWidget(histogramCanvas)
        histogramAx = histogramFig.add_subplot(111)
        self.plotHistogram(histogramAx, data_type='rel_diff', bins=30, time_in_ms=True)
        ttRightSplitter.addWidget(histogramWidget)
        
        tabWidget.addTab(traveltimesTab, "Traveltimes")

        # Tab 4: Acquisition Setup
        setupTab = QWidget()
        setupLayout = QVBoxLayout(setupTab)

        # Create a main splitter for horizontal division
        setupMainSplitter = QSplitter(Qt.Horizontal)
        setupLayout.addWidget(setupMainSplitter)

        # Left splitter for top-left and bottom-left subplots
        setupLeftSplitter = QSplitter(Qt.Vertical)
        setupMainSplitter.addWidget(setupLeftSplitter)

        # Right splitter for top-right and bottom-right subplots
        setupRightSplitter = QSplitter(Qt.Vertical)
        setupMainSplitter.addWidget(setupRightSplitter)

        # Top-left: Setup with observed traveltimes
        observedWidget = QWidget()
        observedLayout = QVBoxLayout(observedWidget)
        observedTitle = QLabel("Observed traveltimes")
        observedTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        observedLayout.addWidget(observedTitle)
        observedFig = Figure(figsize=(5, 4), dpi=100)
        observedCanvas = FigureCanvas(observedFig)
        observedToolbar = NavigationToolbar(observedCanvas, self)
        observedLayout.addWidget(observedToolbar)
        observedLayout.addWidget(observedCanvas)
        observedAx = observedFig.add_subplot(111)
        self.plotSetup(observedAx, color_by='observed', time_in_ms=True, colormap='plasma')
        setupLeftSplitter.addWidget(observedWidget)

        # Bottom-left: Setup with simulated traveltimes
        simulatedWidget = QWidget()
        simulatedLayout = QVBoxLayout(simulatedWidget)
        simulatedTitle = QLabel("Simulated traveltimes")
        simulatedTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        simulatedLayout.addWidget(simulatedTitle)
        simulatedFig = Figure(figsize=(5, 4), dpi=100)
        simulatedCanvas = FigureCanvas(simulatedFig)
        simulatedToolbar = NavigationToolbar(simulatedCanvas, self)
        simulatedLayout.addWidget(simulatedToolbar)
        simulatedLayout.addWidget(simulatedCanvas)
        simulatedAx = simulatedFig.add_subplot(111)
        self.plotSetup(simulatedAx, color_by='simulated', time_in_ms=True, colormap='plasma')
        setupLeftSplitter.addWidget(simulatedWidget)

        # Top-right: Setup with difference
        DiffWidget = QWidget()
        DiffLayout = QVBoxLayout(DiffWidget)
        DiffTitle = QLabel("Traveltime differences")
        DiffTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        DiffLayout.addWidget(DiffTitle)
        DiffFig = Figure(figsize=(5, 4), dpi=100)
        DiffCanvas = FigureCanvas(DiffFig)
        DiffToolbar = NavigationToolbar(DiffCanvas, self)
        DiffLayout.addWidget(DiffToolbar)
        DiffLayout.addWidget(DiffCanvas)
        DiffAx = DiffFig.add_subplot(111)
        self.plotSetup(DiffAx, color_by='diff', time_in_ms=True, colormap='bwr')
        setupRightSplitter.addWidget(DiffWidget)

        # Bottom-right: Setup with relative difference
        relDiffWidget = QWidget()
        relDiffLayout = QVBoxLayout(relDiffWidget)
        relDiffTitle = QLabel("Relative traveltime differences")
        relDiffTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        relDiffLayout.addWidget(relDiffTitle)
        relDiffFig = Figure(figsize=(5, 4), dpi=100)
        relDiffCanvas = FigureCanvas(relDiffFig)
        relDiffToolbar = NavigationToolbar(relDiffCanvas, self)
        relDiffLayout.addWidget(relDiffToolbar)
        relDiffLayout.addWidget(relDiffCanvas)
        relDiffAx = relDiffFig.add_subplot(111)
        self.plotSetup(relDiffAx, color_by='rel_diff', time_in_ms=True, colormap='bwr')
        setupRightSplitter.addWidget(relDiffWidget)

        # Add the setup tab to the tab widget
        tabWidget.addTab(setupTab, "Sources vs Receiver diagrams")                   

    # Delegate visualization methods to the visualization utils class
    def plotStartingModel(self, ax):
        return self.visualizer.plot_starting_model(ax)
    
    def plotInvertedModel(self, ax):
        return self.visualizer.plot_inverted_model(ax)
    
    def plotModelWithRays(self, ax):
        return self.visualizer.plot_model_with_rays(ax)
    
    def plotMaskedModel(self, ax):
        return self.visualizer.plot_masked_model(ax)
    
    def plotRaysWithTravelTimeDiff(self, ax, color_by='rel_diff', 
                             time_in_ms=True, cmap='bwr', percentile=95,
                             min_width=0.5, max_width=3.0, add_title=False):
        return self.visualizer.plot_rays_with_traveltime_diff(ax, color_by, 
                                                     time_in_ms, cmap, percentile,
                                                     min_width, max_width, add_title)
    def plotTraveltimeCurves(self, ax):
        return self.visualizer.plot_traveltime_curves(ax)
    
    def plotTraveltimeComparison(self, ax):
        return self.visualizer.plot_traveltime_comparison(ax)
    
    def plotHistogram(self, ax, data_type='rel_diff', bins=30, time_in_ms=True):
        return self.visualizer.plot_histogram(ax, data_type, bins, time_in_ms)
    
    def plotSetup(self, ax, color_by='observed', time_in_ms=True, colormap='plasma'):
        return self.visualizer.plot_setup(ax, color_by, time_in_ms, colormap)
    
    def plotTopography(self, ax):
        """Plot the topography from sensor positions"""
        try:
            # Get sensor positions
            sensors = self.refrac_manager.data.sensors()
            x = sensors.array()[:, 0]  # X coordinates
            z = sensors.array()[:, 1]  # Z coordinates (elevation)
            
            # Plot the topography
            ax.plot(x, z, 'ko-', linewidth=1.5, markersize=4)
            
            # Mark shot positions with red stars
            shot_indices = np.unique(self.refrac_manager.data['s'])
            shot_x = x[shot_indices]
            shot_z = z[shot_indices]
            ax.plot(shot_x, shot_z, '*', color='red', markersize=10, label='Shot positions')
            
            # Set labels and title
            ax.set_xlabel('Distance (m)')
            ax.set_ylabel('Elevation (m)')
            ax.set_title('Survey Topography')
            
            # Add legend and grid
            ax.legend()
            ax.grid(True, linestyle=':')
            
            # Equal aspect ratio for better visualization
            ax.set_aspect('equal')
            
        except Exception as e:
            print(f"Error plotting topography: {e}")
            ax.text(0.5, 0.5, f"Error plotting topography: {str(e)}", 
                    ha='center', va='center', transform=ax.transAxes)

    def plotParameterInfo(self, ax):
        """Display inversion parameters in a text box"""
        if not self.inversion_params:
            ax.text(0.5, 0.5, "No inversion parameters available", 
                    ha='center', va='center', transform=ax.transAxes,
                    fontsize=12)
            ax.axis('off')
            return
            
        # Create parameter text
        param_text = "Inversion Parameters:\n\n"
        for key, value in self.inversion_params.items():
            param_text += f"{key}: {value}\n"
        
        # Display as a text box
        ax.text(0.5, 0.5, param_text, 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=10, bbox=dict(facecolor='lightgray', alpha=0.5))
        ax.axis('off')
    
def display_inversion_results(refrac_manager, inversion_params=None):
    """
    Create and show an InversionVisualizer window with the given refraction manager
    
    Parameters:
    -----------
    refrac_manager : TravelTimeManager
        PyGIMLI's TravelTimeManager with data and results
    inversion_params : dict, optional
        Dictionary containing inversion parameters
        
    Returns:
    --------
    visualizer : InversionVisualizer
        The created visualizer window
    """
    import sys
    # Create QApplication if one doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create the visualizer
    visualizer = InversionVisualizer(refrac_manager, inversion_params)
    
    # Show the window
    visualizer.show()
    
    # Return the visualizer (keep reference to prevent garbage collection)
    return visualizer