import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QSizePolicy
from PyQt5.QtCore import Qt

# Configure matplotlib backend before importing matplotlib
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to prevent popup windows

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class TabFactory:
    """Factory class to create reusable tabs for the inversion application"""
    
    @staticmethod
    def _create_tab_structure(parent, titles=None):
        """Create a standard 2x2 grid of plots with splitters and titles"""
        # Create the tab widget
        tab = QWidget(parent)
        layout = QVBoxLayout(tab)
        
        # Create 2x2 grid using splitters
        vsplitter = QSplitter(Qt.Vertical)
        hsplitter1 = QSplitter(Qt.Horizontal)
        hsplitter2 = QSplitter(Qt.Horizontal)
        
        # Create figure widgets list
        figures = []
        canvases = []
        plot_widgets = []
        title_labels = []
        
        # Default titles if none provided
        if titles is None:
            titles = ["Plot 1", "Plot 2", "Plot 3", "Plot 4"]
        
        # Create 4 figure widgets
        for i in range(4):
            # Create a container widget with title and plot
            container = QWidget()
            container.setMinimumSize(150, 150)  # Set minimum size
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(10, 10, 10, 10)  # Equal margins on all sides
            
            # Create horizontal layout for title and toolbar
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add title label
            title_label = QLabel(titles[i])
            title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            header_layout.addWidget(title_label)
            title_labels.append(title_label)
            
            # Create figure widget
            fig = Figure(figsize=(5, 3.5), constrained_layout=True)
            canvas = FigureCanvas(fig)
            canvas.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Expanding
            )
            canvas.setMinimumSize(150, 150)
            toolbar = NavigationToolbar(canvas, parent)

            # Add a post-creation adjustment to ensure proper centering
            def on_draw(event):
                # Fine-tune layout after initial drawing
                event.canvas.figure.set_constrained_layout_pads(
                    w_pad=0.01,  # Horizontal padding between subplots
                    h_pad=0.01,  # Vertical padding
                    wspace=0.01,  # Width padding
                    hspace=0.01   # Height padding
                )

            # Connect the event handler
            canvas.mpl_connect('draw_event', on_draw)
            
            # Add toolbar to header layout
            header_layout.addWidget(toolbar)
            
            # Add header layout and canvas to container
            container_layout.addLayout(header_layout)
            container_layout.addWidget(canvas)
            
            # Store references
            figures.append(fig)
            canvases.append(canvas)
            plot_widgets.append(container)
        
        # Add widgets to splitters
        hsplitter1.addWidget(plot_widgets[0])
        hsplitter1.addWidget(plot_widgets[1])
        hsplitter2.addWidget(plot_widgets[2])
        hsplitter2.addWidget(plot_widgets[3])
        vsplitter.addWidget(hsplitter1)
        vsplitter.addWidget(hsplitter2)
        
        # Set equal sizes for horizontal splitters (centered)
        hsplitter1.setSizes([500, 500])  # Equal width for the top two widgets
        hsplitter2.setSizes([500, 500])  # Equal width for the bottom two widgets
        vsplitter.setSizes([500, 500])   # Equal height for top and bottom rows
        
        # Set stretch factors to maintain equal sizes when resized
        hsplitter1.setStretchFactor(0, 1)  # Left widget gets equal stretch
        hsplitter1.setStretchFactor(1, 1)  # Right widget gets equal stretch
        hsplitter2.setStretchFactor(0, 1)  # Left widget gets equal stretch
        hsplitter2.setStretchFactor(1, 1)  # Right widget gets equal stretch
        vsplitter.setStretchFactor(0, 1)   # Top row gets equal stretch
        vsplitter.setStretchFactor(1, 1)   # Bottom row gets equal stretch
        
        # Add to tab layout
        layout.addWidget(vsplitter)
        
        # Store properties
        tab.figures = figures
        tab.canvases = canvases
        tab.title_labels = title_labels
        tab.splitters = (vsplitter, hsplitter1, hsplitter2)
        
        return tab
    
    @staticmethod
    def create_data_tab(parent, refrac_manager=None, params=None):
        """Create the Data tab"""
        # Create the standard tab structure
        titles = ["Observed traveltime curves", "Topography and mesh", "Data setup", "Observed traveltime histogram"]
        tab = TabFactory._create_tab_structure(parent, titles)
        
        # If data is provided, populate the figures
        if refrac_manager is not None:
            try:
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
                
                vis = InversionVisualizations(refrac_manager)
                
                # Clear figures
                for fig in tab.figures:
                    fig.clear()
                
                # Setup the plots
                ax1 = tab.figures[0].add_subplot(111)
                ax2 = tab.figures[1].add_subplot(111)
                ax3 = tab.figures[2].add_subplot(111)
                ax4 = tab.figures[3].add_subplot(111)
                
                # Use visualization methods
                vis.plot_traveltime_curves(ax1, time_in_ms=True)
                vis.plot_topography(ax2)
                vis.plot_setup(ax3, color_by='observed', time_in_ms=True)
                vis.plot_histogram(ax4, time_in_ms=True)
                
                # Update all canvases
                for canvas in tab.canvases:
                    canvas.draw()
                    
            except Exception as e:
                print(f"Error populating Data and Inversion tab: {e}")
                import traceback
                traceback.print_exc()
        
        return tab
    
    @staticmethod
    def create_models_tab(parent, refrac_manager=None, params=None):
        """Create the Model Visualization tab with model views"""
        # Create the standard tab structure
        titles = ["Starting model", "Inverted model with ray paths", "Inverted model", "Inverted model masked with ray coverage"]
        tab = TabFactory._create_tab_structure(parent, titles)
        
        # If data is provided, populate the figures
        if refrac_manager is not None and params is not None:
            try:
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
                
                vis = InversionVisualizations(refrac_manager)

                # Clear figures
                for fig in tab.figures:
                    fig.clear()
                
                # Setup the plots
                ax1 = tab.figures[0].add_subplot(111)
                ax2 = tab.figures[1].add_subplot(111)
                ax3 = tab.figures[2].add_subplot(111)
                ax4 = tab.figures[3].add_subplot(111)
                
                # Populate with data if available
                if hasattr(refrac_manager, 'model') and refrac_manager.model is not None:
                    vis.plot_starting_model(ax1)
                    vis.plot_model_with_rays(ax2)
                    vis.plot_inverted_model(ax3)
                    vis.plot_masked_model(ax4)
                else:
                    for ax in [ax1, ax2, ax3, ax4]:
                        ax.text(0.5, 0.5, "Run inversion to view models", 
                                ha='center', va='center', transform=ax.transAxes,
                                fontsize=12)
                        ax.axis('off')
                
                # Update all canvases
                for canvas in tab.canvases:
                    canvas.draw()
                    
            except Exception as e:
                print(f"Error populating Model Visualization tab: {e}")
                import traceback
                traceback.print_exc()
        
        return tab
        
    @staticmethod
    def create_traveltimes_tab(parent, refrac_manager=None, params=None):
        """Create the Traveltimes tab with traveltime curves"""
        # Create the standard tab structure
        titles = ["Observed and simulated traveltime curves", "Observed vs simulated traveltimes residuals", "Rays with traveltime difference", "Traveltime residual histogram"]
        tab = TabFactory._create_tab_structure(parent, titles)
        
        # If data is provided, populate the figures
        if refrac_manager is not None:
            try:
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
                
                vis = InversionVisualizations(refrac_manager)

                # Clear figures
                for fig in tab.figures:
                    fig.clear()
                
                # Setup the plots
                ax1 = tab.figures[0].add_subplot(111)
                ax2 = tab.figures[1].add_subplot(111)
                ax3 = tab.figures[2].add_subplot(111)
                ax4 = tab.figures[3].add_subplot(111)
                
                # Populate with data if available
                vis.plot_traveltime_curves(ax1,plot_sim_data=True)
                vis.plot_traveltime_comparison(ax2)
                vis.plot_rays_with_traveltime_diff(ax3,color_by='rel_diff')
                vis.plot_histogram(ax4, data_type='rel_diff')
                
                # Update all canvases
                for canvas in tab.canvases:
                    canvas.draw()
                    
            except Exception as e:
                print(f"Error populating Traveltimes tab: {e}")
                import traceback
                traceback.print_exc()
        
        return tab
    
    @staticmethod
    def create_source_receiver_tab(parent, refrac_manager=None, params=None):
        """Create the Setup tab with survey setup and ray coverage"""
        # Create the standard tab structure
        titles = ["Observed traveltime", "Traveltime difference", "Simulated traveltime", "Relative traveltime difference"]
        tab = TabFactory._create_tab_structure(parent, titles)
        
        # If data is provided, populate the figures
        if refrac_manager is not None:
            try:
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
                
                vis = InversionVisualizations(refrac_manager)

                # Clear figures
                for fig in tab.figures:
                    fig.clear()
                
                # Setup the plots
                ax1 = tab.figures[0].add_subplot(111)
                ax2 = tab.figures[1].add_subplot(111)
                ax3 = tab.figures[2].add_subplot(111)
                ax4 = tab.figures[3].add_subplot(111)
                
                # Populate with data if available
                vis.plot_setup(ax1, color_by='observed')
                vis.plot_setup(ax2, color_by='diff')
                vis.plot_setup(ax3, color_by='simulated')
                vis.plot_setup(ax4, color_by='rel_diff')
                
                # Update all canvases
                for canvas in tab.canvases:
                    canvas.draw()
                    
            except Exception as e:
                print(f"Error populating Setup tab: {e}")
                import traceback
                traceback.print_exc()
        
        return tab