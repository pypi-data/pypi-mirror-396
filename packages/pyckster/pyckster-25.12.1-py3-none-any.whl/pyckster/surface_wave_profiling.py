#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Surface Wave Profiling Module for PyCKSTER

This module provides a windowing and profiling approach for surface wave analysis, including:
- Multi-shot windowing for dispersion curve analysis
- Window-based profiling along survey lines
- Extraction of traces from multiple shots within windows
- Interactive visualization of windowed dispersion images and seismograms

Copyright (C) 2025 Sylvain Pasquet
Email: sylvain.pasquet@sorbonne-universite.fr

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import sys
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QListWidget, QListWidgetItem, QLabel, QPushButton, QGroupBox,
    QFormLayout, QLineEdit, QCheckBox, QComboBox, QMessageBox,
    QProgressDialog, QDialog, QDialogButtonBox, QTextEdit, QTabWidget,
    QDoubleSpinBox, QFrame, QApplication, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

# Import surface wave analysis functions
from .obspy_utils import check_format
from .sw_utils import phase_shift, lorentzian_error
from .pyqtgraph_utils import createImageItem


class SurfaceWaveParametersDialog(QDialog):
    """Dialog for setting surface wave analysis parameters"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Surface Wave Analysis Parameters")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Create form layout for parameters
        form_layout = QFormLayout()
        
        # Phase Shift Calculation Parameters
        phase_shift_label = QLabel("Phase Shift Calculation Parameters:")
        phase_shift_label.setFont(QFont("Arial", 10, QFont.Bold))
        form_layout.addRow(phase_shift_label)
        
        # Velocity range parameters
        self.vmin_edit = QLineEdit("0")
        self.vmax_edit = QLineEdit("1500")
        self.dv_edit = QLineEdit("10")
        form_layout.addRow("Min velocity (m/s):", self.vmin_edit)
        form_layout.addRow("Max velocity (m/s):", self.vmax_edit)
        form_layout.addRow("Velocity step (m/s):", self.dv_edit)
        
        # Frequency parameters
        self.fmin_edit = QLineEdit("0")
        form_layout.addRow("Min frequency (Hz):", self.fmin_edit)
        self.fmax_edit = QLineEdit("200")
        form_layout.addRow("Max frequency (Hz):", self.fmax_edit)
        
        # Normalization options
        self.norm_combo = QComboBox()
        self.norm_combo.addItems(["Frequencies", "Velocities", "Global", "None"])
        self.norm_combo.setCurrentText("Frequencies")
        form_layout.addRow("Normalization:", self.norm_combo)
        
        # Add spacing
        form_layout.addRow(QLabel(""), QLabel(""))
        
        # Processing Options
        processing_label = QLabel("Processing Options:")
        processing_label.setFont(QFont("Arial", 10, QFont.Bold))
        form_layout.addRow(processing_label)
        
        # Include elevation checkbox
        self.include_elevation_check = QCheckBox()
        self.include_elevation_check.setChecked(False)
        self.include_elevation_check.setToolTip("Include elevation (Z coordinate) in 3D distance calculation for phase shift")
        form_layout.addRow("Include elevation:", self.include_elevation_check)
        
        layout.addLayout(form_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def getParameters(self):
        """Return the analysis parameters"""
        try:
            return {
                'vmin': float(self.vmin_edit.text()),
                'vmax': float(self.vmax_edit.text()),
                'dv': float(self.dv_edit.text()),
                'fmin': float(self.fmin_edit.text()),
                'fmax': float(self.fmax_edit.text()),
                'normalization': self.norm_combo.currentText(),
                'include_elevation': self.include_elevation_check.isChecked()
            }
        except ValueError as e:
            # Re-raise with more context
            raise ValueError(f"Invalid parameter: {e}")


class SurfaceWaveWorker(QThread):
    """Worker thread for surface wave analysis computations"""
    
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def __init__(self, streams, shot_positions, parameters):
        super().__init__()
        self.streams = streams
        self.shot_positions = shot_positions
        self.parameters = parameters
    
    def run(self):
        """Run surface wave analysis in background thread"""
        try:
            results = {}
            skipped_shots = []
            total_shots = len(self.streams)
            
            for i, stream in enumerate(self.streams):
                # Update progress
                progress_percent = int((i / total_shots) * 100)
                self.progress.emit(progress_percent)

                # Determine input format
                input_format = check_format(stream)
                
                # Extract data for current shot
                data_matrix = []
                offsets = []
                trace_positions = []
                receiver_coords_x = []
                receiver_coords_y = []
                receiver_coords_z = []
                
                # Get source position from first trace
                first_trace = stream[0]
                source_coordinate_x = first_trace.stats[input_format].trace_header.source_coordinate_x
                source_coordinate_y = first_trace.stats[input_format].trace_header.source_coordinate_y
                
                # Get source elevation if available and needed
                if self.parameters['include_elevation']:
                    try:
                        source_coordinate_z = first_trace.stats[input_format].trace_header.source_elevation
                    except (AttributeError, KeyError):
                        source_coordinate_z = 0.0  # Default to 0 if not available
                        print(f"Warning: Source elevation not available for shot {i+1}, using 0.0")
                else:
                    source_coordinate_z = 0.0
                    
                scalar = first_trace.stats[input_format].trace_header.scalar_to_be_applied_to_all_coordinates
                
                # Apply scalar to source coordinates
                if scalar < 0:
                    source_coordinate_x = source_coordinate_x / abs(scalar)
                    source_coordinate_y = source_coordinate_y / abs(scalar)
                    if self.parameters['include_elevation']:
                        source_coordinate_z = source_coordinate_z / abs(scalar)
                else:
                    source_coordinate_x = source_coordinate_x * scalar
                    source_coordinate_y = source_coordinate_y * scalar
                    if self.parameters['include_elevation']:
                        source_coordinate_z = source_coordinate_z * scalar
                
                for trace in stream:
                    data_matrix.append(trace.data)
                    
                    # Get group coordinates (receiver position)
                    group_coord_x = trace.stats[input_format].trace_header.group_coordinate_x
                    group_coord_y = trace.stats[input_format].trace_header.group_coordinate_y
                    
                    # Get receiver elevation if available and needed
                    if self.parameters['include_elevation']:
                        try:
                            group_coord_z = trace.stats[input_format].trace_header.receiver_group_elevation
                        except (AttributeError, KeyError):
                            group_coord_z = 0.0  # Default to 0 if not available
                    else:
                        group_coord_z = 0.0
                    
                    scalar = trace.stats[input_format].trace_header.scalar_to_be_applied_to_all_coordinates
                    
                    # Apply scalar to group coordinates
                    if scalar < 0:
                        group_coord_x = group_coord_x / abs(scalar)
                        group_coord_y = group_coord_y / abs(scalar)
                        if self.parameters['include_elevation']:
                            group_coord_z = group_coord_z / abs(scalar)
                    else:
                        group_coord_x = group_coord_x * scalar
                        group_coord_y = group_coord_y * scalar
                        if self.parameters['include_elevation']:
                            group_coord_z = group_coord_z * scalar
                    
                    # Store coordinates
                    receiver_coords_x.append(group_coord_x)
                    receiver_coords_y.append(group_coord_y)
                    receiver_coords_z.append(group_coord_z)
                    trace_positions.append(group_coord_x)  # Keep for compatibility
                    
                    # Calculate offset as difference between receiver and source positions (for sorting)
                    offset = group_coord_x - source_coordinate_x
                    offsets.append(offset)
                
                # Convert to numpy arrays
                XT = np.array(data_matrix)
                offsets = np.array(offsets)
                trace_positions = np.array(trace_positions)
                receiver_coords_x = np.array(receiver_coords_x)
                receiver_coords_y = np.array(receiver_coords_y)
                receiver_coords_z = np.array(receiver_coords_z)
                
                # Calculate distances from source to each receiver
                if self.parameters['include_elevation']:
                    # 3D distance calculation including elevation
                    distances = np.sqrt((receiver_coords_x - source_coordinate_x)**2 + 
                                      (receiver_coords_y - source_coordinate_y)**2 +
                                      (receiver_coords_z - source_coordinate_z)**2)
                    distance_type = "3D"
                else:
                    # 2D distance calculation (horizontal only)
                    distances = np.sqrt((receiver_coords_x - source_coordinate_x)**2 + 
                                      (receiver_coords_y - source_coordinate_y)**2)
                    distance_type = "2D"
                
                # Sort data by offset before processing (handles negative offsets correctly)
                sort_indices = np.argsort(offsets)
                XT_sorted = XT[sort_indices, :]
                offsets_sorted = offsets[sort_indices]
                trace_positions_sorted = trace_positions[sort_indices]
                receiver_coords_x_sorted = receiver_coords_x[sort_indices]
                receiver_coords_y_sorted = receiver_coords_y[sort_indices]
                receiver_coords_z_sorted = receiver_coords_z[sort_indices]
                distances_sorted = distances[sort_indices]
                
                # Apply trace windowing if specified
                num_traces = self.parameters['num_traces']
                trace_offset = self.parameters['trace_offset']
                side_preference = self.parameters.get('side_preference', 'Auto (based on offset)')
                side_restriction = self.parameters.get('side_restriction', 'Use both sides')
                
                if num_traces > 0 and num_traces < len(XT_sorted):
                    # Separate positive and negative offset traces
                    positive_mask = offsets_sorted > 0
                    negative_mask = offsets_sorted < 0
                    
                    positive_indices = np.where(positive_mask)[0]
                    negative_indices = np.where(negative_mask)[0]
                    
                    selected_indices = None
                    skip_reason = None
                    
                    # Check side restriction first
                    if side_restriction == "Left side only":
                        if len(negative_indices) < num_traces:
                            skip_reason = f"Left side only selected but insufficient left traces. Left offsets: {len(negative_indices)}, Required: {num_traces}"
                        else:
                            # Select from left side based on trace_offset
                            if trace_offset <= 0:
                                # Use trace_offset from the end of negative indices
                                start_idx = max(0, len(negative_indices) + trace_offset - num_traces + 1)
                                end_idx = len(negative_indices) + trace_offset + 1
                                if start_idx < end_idx and end_idx <= len(negative_indices):
                                    selected_indices = negative_indices[start_idx:end_idx]
                            else:
                                # Positive trace_offset on left side - skip from beginning
                                if trace_offset < len(negative_indices):
                                    start_idx = trace_offset
                                    end_idx = min(start_idx + num_traces, len(negative_indices))
                                    selected_indices = negative_indices[start_idx:end_idx]
                                    
                    elif side_restriction == "Right side only":
                        if len(positive_indices) < num_traces:
                            skip_reason = f"Right side only selected but insufficient right traces. Right offsets: {len(positive_indices)}, Required: {num_traces}"
                        else:
                            # Select from right side based on trace_offset
                            if trace_offset >= 0:
                                # Use trace_offset from the beginning of positive indices
                                if trace_offset < len(positive_indices):
                                    end_idx = min(trace_offset + num_traces, len(positive_indices))
                                    selected_indices = positive_indices[trace_offset:end_idx]
                            else:
                                # Negative trace_offset on right side - select from end
                                start_idx = max(0, len(positive_indices) + trace_offset - num_traces + 1)
                                end_idx = len(positive_indices) + trace_offset + 1
                                if start_idx < end_idx and end_idx <= len(positive_indices):
                                    selected_indices = positive_indices[start_idx:end_idx]
                                    
                    else:  # "Use both sides"
                        # Determine preferred side based on preference setting
                        prefer_left = False
                        prefer_right = False
                        
                        if side_preference == "Prefer Left":
                            prefer_left = True
                        elif side_preference == "Prefer Right":
                            prefer_right = True
                        else:  # "Auto (based on offset)"
                            if trace_offset < 0:
                                prefer_left = True
                            else:
                                prefer_right = True
                        
                        # Try preferred side first
                        if prefer_left and len(negative_indices) >= num_traces:
                            # Try left side first
                            if trace_offset <= 0:
                                start_idx = max(0, len(negative_indices) + trace_offset - num_traces + 1)
                                end_idx = len(negative_indices) + trace_offset + 1
                                if start_idx < end_idx and end_idx <= len(negative_indices):
                                    selected_indices = negative_indices[start_idx:end_idx]
                            else:
                                if trace_offset < len(negative_indices):
                                    start_idx = trace_offset
                                    end_idx = min(start_idx + num_traces, len(negative_indices))
                                    selected_indices = negative_indices[start_idx:end_idx]
                                    
                        elif prefer_right and len(positive_indices) >= num_traces:
                            # Try right side first
                            if trace_offset >= 0:
                                if trace_offset < len(positive_indices):
                                    end_idx = min(trace_offset + num_traces, len(positive_indices))
                                    selected_indices = positive_indices[trace_offset:end_idx]
                            else:
                                start_idx = max(0, len(positive_indices) + trace_offset - num_traces + 1)
                                end_idx = len(positive_indices) + trace_offset + 1
                                if start_idx < end_idx and end_idx <= len(positive_indices):
                                    selected_indices = positive_indices[start_idx:end_idx]
                        
                        # If preferred side didn't work, try the other side
                        if selected_indices is None or len(selected_indices) < num_traces:
                            if prefer_left and len(positive_indices) >= num_traces:
                                # Try right side as fallback
                                selected_indices = positive_indices[:num_traces]
                            elif prefer_right and len(negative_indices) >= num_traces:
                                # Try left side as fallback
                                selected_indices = negative_indices[-num_traces:]
                    
                    # Check if we have enough traces
                    if selected_indices is None or len(selected_indices) < num_traces:
                        if skip_reason is None:
                            skip_reason = f"Not enough traces available. Positive offsets: {len(positive_indices)}, Negative offsets: {len(negative_indices)}, Required: {num_traces}, Side preference: {side_preference}, Side restriction: {side_restriction}"
                        skipped_shots.append((i+1, skip_reason))
                        print(f"Skipping shot {i+1}: {skip_reason}")
                        continue
                    
                    # Verify all selected traces are on the same side
                    selected_offsets = offsets_sorted[selected_indices]
                    if not (np.all(selected_offsets > 0) or np.all(selected_offsets < 0)):
                        skip_reason = "Selected traces are not all on the same side of the shot"
                        skipped_shots.append((i+1, skip_reason))
                        print(f"Skipping shot {i+1}: {skip_reason}")
                        continue
                    
                    # Apply windowing to all arrays using selected indices
                    XT_sorted = XT_sorted[selected_indices, :]
                    offsets_sorted = offsets_sorted[selected_indices]
                    trace_positions_sorted = trace_positions_sorted[selected_indices]
                    receiver_coords_x_sorted = receiver_coords_x_sorted[selected_indices]
                    receiver_coords_y_sorted = receiver_coords_y_sorted[selected_indices]
                    receiver_coords_z_sorted = receiver_coords_z_sorted[selected_indices]
                    distances_sorted = distances_sorted[selected_indices]
                
                # Get sampling interval
                si = stream[0].stats.delta
                
                # Get velocity parameters and handle vmin=0 case
                vmin = self.parameters['vmin']
                vmax = self.parameters['vmax']
                dv = self.parameters['dv']
                
                # If vmin is 0, use dv as minimum to avoid numerical issues
                if vmin == 0:
                    vmin = dv
                    print(f"Warning: vmin was 0, using dv={dv} as minimum velocity to avoid numerical issues")
                
                # Perform phase shift analysis using calculated distances
                fs, vs, FV = phase_shift(
                    XT_sorted, si, distances_sorted,
                    vmin, vmax, dv,
                    self.parameters['fmax'],
                    self.parameters.get('fmin', 0)
                )
                
                # Store results (keep original signed offsets and coordinates for display)
                results[f'shot_{i}'] = {
                    'frequencies': fs,
                    'velocities': vs,
                    'dispersion_image': FV,
                    'data_matrix': XT_sorted,
                    'offsets': offsets_sorted,  # Keep signed offsets for proper axis labeling
                    'trace_positions': trace_positions_sorted,
                    'receiver_coords_x': receiver_coords_x_sorted,
                    'receiver_coords_y': receiver_coords_y_sorted,
                    'receiver_coords_z': receiver_coords_z_sorted,
                    'distances': distances_sorted,  # Store distances used for phase shift
                    'distance_type': distance_type,  # Store whether 2D or 3D distances were used
                    'source_position': source_coordinate_x,
                    'source_position_x': source_coordinate_x,
                    'source_position_y': source_coordinate_y,
                    'source_position_z': source_coordinate_z,
                    'include_elevation': self.parameters['include_elevation'],
                    'sampling_interval': si,
                    'shot_position': self.shot_positions[i] if i < len(self.shot_positions) else source_coordinate_x
                }
            
            self.progress.emit(100)
            
            # Add skipped shots information to results
            if skipped_shots:
                results['_skipped_shots'] = skipped_shots
                
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))


class SurfaceWaveProfilingWindow(QMainWindow):
    """Main window for surface wave profiling with windowing approach"""
    
    def __init__(self, parent, streams, shot_positions):
        super().__init__(parent)
        self.parent_window = parent
        self.streams = streams.copy()  # Keep reference to streams
        self.shot_positions = shot_positions.copy()  # Keep reference to shot positions
        
        # Calculate survey geometry first to set proper defaults
        survey_extent, default_window_size, max_shot_offset = self._calculateSurveyGeometry()
        
        # Calculate default window step (geophone spacing)
        default_window_step = self._calculateDefaultWindowStep()
        
        # Profiling-specific attributes
        self.window_size = default_window_size  # Default to 100% of survey extent
        self.window_step = default_window_step  # Step between windows (default: geophone spacing)
        # Min shot offset from window edge (0 = shot can be at first/last trace position)
        self.min_shot_offset = 0.0  # Minimum shot offset from window edge
        self.max_shot_offset = max_shot_offset  # Maximum shot offset from window edge
        self.side = 'left'  # Default side: 'left', 'right', or 'both'
        self.window_num_traces = None  # Number of traces that best matches window size
        self.actual_window_size = None  # Actual window size based on trace count
        self.available_windows = []  # List of available window positions (Xmids)
        self.window_subsets = {}  # Dictionary mapping Xmid to available subset combinations
        self.survey_extent = survey_extent  # Store for validation
        self.max_possible_window_size = survey_extent  # Store for validation (100% of survey extent)
        self.current_window_index = 0  # Currently selected window
        self.current_subset_index = 0  # Currently selected subset within window
        
        self.analysis_results = {}
        self.current_result = None  # Store current displayed result for wiggle refresh
        self.stacked_results = {}  # Store single stacked dispersion result for each window (latest only)
        self.current_stacked_id = None  # Currently displayed stacked result ID
        
        # Initialize default analysis parameters
        self.current_params = {
            'vmin': 0,
            'vmax': 1500,
            'dv': 10,
            'fmin': 0,
            'fmax': 200,
            'normalization': 'None',

            'include_elevation': False
        }
        
        # Initialize picking-related variables
        self.picking_mode = False
        self.removal_mode = False
        self.picked_points = []  # Store (freq, velocity) tuples for curve points
        self.picked_point_items = []  # Store plot items for picked points
        self.curve_line = None
        self.current_dispersion_data = None
        self.extracted_curves = {}  # Store extracted curves for each shot
        self.window_curves = {}  # Store picked curves for each window - NEW
        self.current_window_key = None  # Track current window - NEW
        
        # Mode selection variables
        self.current_mode = 0  # Default to fundamental mode (M0)
        print(f"DEBUG: Initialized current_mode to {self.current_mode}")
        self.mode_colors = {
            0: 'red',      # M0 - Fundamental (red)
            1: 'blue',     # M1 - 1st Higher (blue)
            2: 'green',    # M2 - 2nd Higher (green)
            3: 'magenta',  # M3 - 3rd Higher (magenta)
            4: 'orange'    # M4 - 4th Higher (orange)
        }
        
        # Error bar display variables
        self.show_error_bars = False
        self.error_bar_items = []  # Store error bar plot items
        
        self.setWindowTitle("Surface Wave Profiling")
        self.setGeometry(100, 100, 1400, 900)
        
        # Setup UI
        self.setupUI()
        
        # Windows will be calculated only when "Compute Window Geometry" button is clicked
        # Initialize empty lists
        self.available_windows = []
        self.window_subsets = {}
        
        # Show window
        self.show()
    
    def setupUI(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create horizontal splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Stream list and controls
        left_panel = self.createLeftPanel()
        left_panel.setMinimumWidth(200)  # Set minimum width
        left_panel.setMaximumWidth(400)  # Set maximum width for better layout
        splitter.addWidget(left_panel)
        
        # Right panel - Analysis plots
        right_panel = self.createRightPanel()
        splitter.addWidget(right_panel)
        
        # Configure splitter after adding widgets
        splitter.setCollapsible(0, False)  # Prevent left panel from collapsing completely
        splitter.setCollapsible(1, False)  # Prevent right panel from collapsing completely
        
        # Set splitter proportions (left panel width, right panel width)
        splitter.setSizes([280, 1120])  # Reduced left panel default width
    
    def createLeftPanel(self):
        """Create left panel with window list and controls"""
        # Create main panel
        panel = QWidget()
        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create scrollable content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Title
        title_label = QLabel("Surface Wave Profiling")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Clear results button - moved to top, fixed width
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clearResults)
        self.clear_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.clear_button.setMaximumWidth(250)  # Prevent button from being too wide
        layout.addWidget(self.clear_button)
        
        # Windowing Parameters (standard groupbox)
        config_group = QGroupBox("Windowing Parameters")
        config_layout = QFormLayout(config_group)
        
        # Window size
        self.window_size_edit = QDoubleSpinBox()
        self.window_size_edit.setRange(0.1, max(1000.0, self.max_possible_window_size * 1.1))  # Allow slightly above max for validation
        self.window_size_edit.setValue(self.window_size)
        self.window_size_edit.setSuffix(" m")
        self.window_size_edit.setDecimals(1)
        self.window_size_edit.setSingleStep(0.1)
        self.window_size_edit.setToolTip(f"Maximum possible window size: {self.max_possible_window_size:.1f}m (survey extent: {self.survey_extent:.1f}m)")
        self.window_size_edit.valueChanged.connect(self.onWindowConfigChanged)
        config_layout.addRow("Window Size:", self.window_size_edit)
        
        # Window step
        self.window_step_edit = QDoubleSpinBox()
        self.window_step_edit.setRange(0.1, 100.0)
        self.window_step_edit.setValue(self.window_step)
        self.window_step_edit.setSuffix(" m")
        self.window_step_edit.setDecimals(1)
        self.window_step_edit.setSingleStep(0.1)
        self.window_step_edit.setToolTip(f"Step between windows (default: geophone spacing = {self.window_step:.1f}m)")
        self.window_step_edit.valueChanged.connect(self.onWindowConfigChanged)
        config_layout.addRow("Window Step:", self.window_step_edit)
        
        # Min shot offset
        self.min_shot_offset_edit = QDoubleSpinBox()
        self.min_shot_offset_edit.setRange(0.0, 1000.0)
        self.min_shot_offset_edit.setValue(self.min_shot_offset)
        self.min_shot_offset_edit.setSuffix(" m")
        self.min_shot_offset_edit.setDecimals(1)
        self.min_shot_offset_edit.setSingleStep(0.1)
        self.min_shot_offset_edit.setToolTip("Minimum shot offset from window edge (0 = shot can be at edge, but not inside window)")
        self.min_shot_offset_edit.valueChanged.connect(self.onWindowConfigChanged)
        config_layout.addRow("Min Shot Offset:", self.min_shot_offset_edit)
        
        # Max shot offset
        self.max_shot_offset_edit = QDoubleSpinBox()
        self.max_shot_offset_edit.setRange(0.1, max(1000.0, self.survey_extent * 2))
        self.max_shot_offset_edit.setValue(self.max_shot_offset)
        self.max_shot_offset_edit.setSuffix(" m")
        self.max_shot_offset_edit.setDecimals(1)
        self.max_shot_offset_edit.setSingleStep(0.1)
        self.max_shot_offset_edit.setToolTip("Maximum shot offset from window edge")
        self.max_shot_offset_edit.valueChanged.connect(self.onWindowConfigChanged)
        config_layout.addRow("Max Shot Offset:", self.max_shot_offset_edit)
        
        # Side selection
        self.side_combo = QComboBox()
        self.side_combo.addItems(['left', 'right', 'both'])
        self.side_combo.setCurrentText(self.side)
        self.side_combo.currentTextChanged.connect(self.onWindowConfigChanged)
        config_layout.addRow("Side:", self.side_combo)
        
        # Window size info display
        self.window_info_label = QLabel("Click 'Compute Window Geometry' to calculate windows")
        self.window_info_label.setStyleSheet("QLabel { color: #FF6600; font-size: 10px; font-weight: bold; }")
        config_layout.addRow("", self.window_info_label)
        
        # Compute window geometry button (integrated into windowing parameters)
        self.compute_geometry_button = QPushButton("Compute Window Geometry")
        self.compute_geometry_button.clicked.connect(self.computeWindowGeometry)
        self.compute_geometry_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; }")
        self.compute_geometry_button.setToolTip("Calculate available windows based on current configuration")
        self.compute_geometry_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.compute_geometry_button.setMaximumWidth(250)  # Prevent button from being too wide
        config_layout.addRow("", self.compute_geometry_button)
        
        layout.addWidget(config_group)
        
        # Window list (Xmids) - scrollable with maximum height
        windows_group = QGroupBox("Available Windows (Xmid)")
        windows_layout = QVBoxLayout(windows_group)
        
        self.window_list = QListWidget()
        self.window_list.itemSelectionChanged.connect(self.onWindowSelectionChanged)
        self.window_list.setMaximumHeight(150)  # Set maximum height for scrolling
        self.window_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        windows_layout.addWidget(self.window_list)
        
        layout.addWidget(windows_group)
        
        # Subset list for selected window - scrollable with maximum height
        subsets_group = QGroupBox("Available Trace Subsets")
        subsets_layout = QVBoxLayout(subsets_group)
        
        self.subset_list = QListWidget()
        self.subset_list.itemSelectionChanged.connect(self.onSubsetSelectionChanged)
        self.subset_list.setMaximumHeight(150)  # Set maximum height for scrolling
        self.subset_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        subsets_layout.addWidget(self.subset_list)
        
        layout.addWidget(subsets_group)
        
        # Phase Shift Parameters (standard groupbox with inline controls)
        params_group = QGroupBox("Phase Shift Parameters")
        params_layout = QFormLayout(params_group)
        
        # Min velocity control
        self.vmin_edit = QLineEdit("0")
        self.vmin_edit.setMaximumWidth(100)
        self.vmin_edit.setToolTip("Minimum velocity in m/s")
        self.vmin_edit.textChanged.connect(self.onParameterChanged)  # Real-time update
        params_layout.addRow("Min velocity (m/s):", self.vmin_edit)
        
        # Max velocity control  
        self.vmax_edit = QLineEdit("1500")
        self.vmax_edit.setMaximumWidth(100)
        self.vmax_edit.setToolTip("Maximum velocity in m/s")
        self.vmax_edit.textChanged.connect(self.onParameterChanged)  # Real-time update
        params_layout.addRow("Max velocity (m/s):", self.vmax_edit)
        
        # Velocity step control
        self.dv_edit = QLineEdit("10")
        self.dv_edit.setMaximumWidth(100)
        self.dv_edit.setToolTip("Velocity step in m/s")
        params_layout.addRow("Velocity step (m/s):", self.dv_edit)
        
        # Min frequency control
        self.fmin_edit = QLineEdit("0")
        self.fmin_edit.setMaximumWidth(100)
        self.fmin_edit.setToolTip("Minimum frequency in Hz")
        params_layout.addRow("Min frequency (Hz):", self.fmin_edit)
        
        # Max frequency control
        self.fmax_edit = QLineEdit("200")
        self.fmax_edit.setMaximumWidth(100)
        self.fmax_edit.setToolTip("Maximum frequency in Hz")
        self.fmax_edit.textChanged.connect(self.onParameterChanged)  # Real-time update
        params_layout.addRow("Max frequency (Hz):", self.fmax_edit)
        
        # Normalization control
        self.norm_combo = QComboBox()
        self.norm_combo.addItems(["None", "Frequencies", "Velocities"])
        self.norm_combo.setCurrentText("Frequencies")
        self.norm_combo.setMaximumWidth(120)
        self.norm_combo.currentTextChanged.connect(self.onParameterChanged)  # Real-time update
        params_layout.addRow("Normalization:", self.norm_combo)
        
        # Additional options
        self.include_elevation_check = QCheckBox("Include elevation")
        self.include_elevation_check.setChecked(False)
        params_layout.addRow("", self.include_elevation_check)
        
        # Analyze button - reduced width
        self.analyze_button = QPushButton("Compute Dispersion Images")
        self.analyze_button.clicked.connect(self.runAnalysis)
        self.analyze_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.analyze_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.analyze_button.setMaximumWidth(250)
        params_layout.addRow("", self.analyze_button)
        
        # Diagnostic button
        self.diagnose_button = QPushButton("Diagnose Setup")
        self.diagnose_button.clicked.connect(self.diagnoseProfiling)
        self.diagnose_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")
        self.diagnose_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.diagnose_button.setMaximumWidth(250)
        params_layout.addRow("", self.diagnose_button)
        
        layout.addWidget(params_group)
        
        # Shot Selection and Stacking Controls
        # Individual Subset Images section
        subset_group = QGroupBox("Individual Subset Images")
        subset_layout = QVBoxLayout(subset_group)
        
        # Subset list for current window
        subset_list_label = QLabel("Available Subset Images for Current Window:")
        subset_layout.addWidget(subset_list_label)
        
        self.subset_image_list = QListWidget()
        self.subset_image_list.setMaximumHeight(120)
        self.subset_image_list.itemChanged.connect(self.onSubsetImageSelectionChanged)
        self.subset_image_list.itemClicked.connect(self.onSubsetImageClicked)
        self.subset_image_list.currentItemChanged.connect(self.onSubsetImageCurrentChanged)
        subset_layout.addWidget(self.subset_image_list)
        
        # Preview controls
        preview_controls = QHBoxLayout()
        self.preview_subset_button = QPushButton("Preview Selected")
        self.preview_subset_button.clicked.connect(self.previewSelectedSubset)
        self.preview_subset_button.setEnabled(False)
        preview_controls.addWidget(self.preview_subset_button)
        
        preview_controls.addStretch()
        subset_layout.addLayout(preview_controls)
        
        # Stacking controls
        stacking_controls = QHBoxLayout()
        
        self.select_all_subsets_button = QPushButton("Select All")
        self.select_all_subsets_button.clicked.connect(self.selectAllSubsets)
        self.select_all_subsets_button.setEnabled(False)
        stacking_controls.addWidget(self.select_all_subsets_button)
        
        self.select_none_subsets_button = QPushButton("Select None")
        self.select_none_subsets_button.clicked.connect(self.selectNoSubsets)
        self.select_none_subsets_button.setEnabled(False)
        stacking_controls.addWidget(self.select_none_subsets_button)
        
        self.stack_subsets_button = QPushButton("Stack Selected")
        self.stack_subsets_button.clicked.connect(self.stackSelectedSubsets)
        self.stack_subsets_button.setEnabled(False)
        self.stack_subsets_button.setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-weight: bold; }")
        stacking_controls.addWidget(self.stack_subsets_button)
        
        subset_layout.addLayout(stacking_controls)
        
        # Subset info display
        self.subset_info_text = QTextEdit()
        self.subset_info_text.setMaximumHeight(60)
        self.subset_info_text.setReadOnly(True)
        subset_layout.addWidget(self.subset_info_text)
        
        layout.addWidget(subset_group)
        
        # Stacked Results section
        stacked_group = QGroupBox("Stacked Dispersion Results")
        stacked_layout = QVBoxLayout(stacked_group)
        
        # Stacked images list
        stacked_list_label = QLabel("Stacked Images for Current Window:")
        stacked_layout.addWidget(stacked_list_label)
        
        self.stacked_results_list = QListWidget()
        self.stacked_results_list.setMaximumHeight(100)
        self.stacked_results_list.itemClicked.connect(self.onStackedResultClicked)
        stacked_layout.addWidget(self.stacked_results_list)
        
        # Stacked image controls
        stacked_controls = QHBoxLayout()
        
        self.show_stacked_button = QPushButton("Show Selected")
        self.show_stacked_button.clicked.connect(self.showSelectedStackedResult)
        self.show_stacked_button.setEnabled(False)
        stacked_controls.addWidget(self.show_stacked_button)
        
        self.delete_stacked_button = QPushButton("Delete")
        self.delete_stacked_button.clicked.connect(self.deleteSelectedStackedResult)
        self.delete_stacked_button.setEnabled(False)
        stacked_controls.addWidget(self.delete_stacked_button)
        
        stacked_controls.addStretch()
        stacked_layout.addLayout(stacked_controls)
        
        layout.addWidget(stacked_group)
        
        # Curve picking controls
        picking_group = QGroupBox("Dispersion Curve Picking")
        picking_layout = QVBoxLayout(picking_group)
        
        # Picking mode selection
        picking_mode_layout = QHBoxLayout()
        picking_mode_layout.addWidget(QLabel("Picking Mode:"))
        self.picking_mode_combo = QComboBox()
        self.picking_mode_combo.addItems(["Manual", "Auto (find maximum)"])
        self.picking_mode_combo.setCurrentIndex(1)  # Default to auto
        picking_mode_layout.addWidget(self.picking_mode_combo)
        picking_layout.addLayout(picking_mode_layout)
        
        # Mode selection for dispersion picking
        mode_selection_layout = QHBoxLayout()
        mode_selection_layout.addWidget(QLabel("Dispersion Mode:"))
        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "M0 - Fundamental", 
            "M1 - 1st Higher", 
            "M2 - 2nd Higher", 
            "M3 - 3rd Higher",
            "M4 - 4th Higher"
        ])
        self.mode_selector.setCurrentIndex(0)  # Default to fundamental mode
        self.mode_selector.currentIndexChanged.connect(self.onModeChanged)
        mode_selection_layout.addWidget(self.mode_selector)
        picking_layout.addLayout(mode_selection_layout)
        
        # Picking mode toggle
        self.picking_button = QPushButton("Start Picking")
        self.picking_button.clicked.connect(self.togglePicking)
        self.picking_button.setEnabled(False)  # Disabled until analysis is done
        picking_layout.addWidget(self.picking_button)
        
        # Point removal mode toggle
        self.removal_button = QPushButton("Remove Points")
        self.removal_button.clicked.connect(self.toggleRemoval)
        self.removal_button.setEnabled(False)
        picking_layout.addWidget(self.removal_button)
        
        # Interpolate curve button
        self.interpolate_button = QPushButton("Interpolate Curve")
        self.interpolate_button.clicked.connect(self.interpolateCurve)
        self.interpolate_button.setEnabled(False)
        picking_layout.addWidget(self.interpolate_button)
        
        # Clear all points button
        self.clear_picking_button = QPushButton("Clear All Points")
        self.clear_picking_button.clicked.connect(self.clearPicking)
        self.clear_picking_button.setEnabled(False)
        picking_layout.addWidget(self.clear_picking_button)
        
        # Show/Hide error bars button
        self.show_errors_button = QPushButton("Show Error Bars")
        self.show_errors_button.clicked.connect(self.toggleErrorBars)
        self.show_errors_button.setEnabled(False)
        self.show_errors_button.setCheckable(True)
        picking_layout.addWidget(self.show_errors_button)
        
        # Export curves button
        self.export_curves_button = QPushButton("Export Curves")
        self.export_curves_button.clicked.connect(self.exportCurves)
        self.export_curves_button.setEnabled(False)
        picking_layout.addWidget(self.export_curves_button)
        
        # Window curves status
        self.window_curves_status = QLabel("Window Curves: 0")
        self.window_curves_status.setStyleSheet("font-weight: bold; color: #0066cc;")
        picking_layout.addWidget(self.window_curves_status)
        
        # Add info about Lorentzian errors
        error_info_label = QLabel("Note: Lorentzian velocity errors calculated automatically")
        error_info_label.setStyleSheet("font-size: 10px; color: #666666; font-style: italic;")
        picking_layout.addWidget(error_info_label)
        
        layout.addWidget(picking_group)
        
        # Current parameters display
        params_group = QGroupBox("Current Parameters")
        params_layout = QVBoxLayout(params_group)
        
        self.params_text = QTextEdit()
        self.params_text.setMaximumHeight(120)
        self.params_text.setReadOnly(True)
        params_layout.addWidget(self.params_text)
        
        layout.addWidget(params_group)
        
        # Set default parameters (using current_params to match existing code)
        self.current_params = {
            'vmin': 0, 'vmax': 1500, 'dv': 10, 'fmin': 0, 'fmax': 200,
            'normalization': 'Frequencies', 'include_elevation': False
        }
        
        # Add stretch
        layout.addStretch()
        
        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        
        return panel
    
    def _calculateSurveyGeometry(self):
        """Calculate survey extent, default window size, and maximum shot offset based on data"""
        if not self.streams or not self.shot_positions:
            return 100.0, 10.0, 50.0  # Fallback defaults
            
        # Get all available trace positions across all shots to determine survey extent
        all_positions = set()
        debug_info = []  # For debugging coordinate issues
        
        # Store all geophone positions for each shot for offset calculation
        shot_geophone_positions = {}
        
        for i, stream in enumerate(self.streams):
            shot_pos = self.shot_positions[i]
            geophone_positions = []
            
            for j, trace in enumerate(stream):
                # Get trace position from group coordinates (receiver position), not shot + distance
                try:
                    # Try to get group coordinates like in surface_wave_analysis.py
                    if hasattr(trace.stats, 'segy') and hasattr(trace.stats.segy, 'trace_header'):
                        group_coord_x = trace.stats.segy.trace_header.group_coordinate_x
                        scalar = trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                        input_format = 'segy'
                    elif hasattr(trace.stats, 'su') and hasattr(trace.stats.su, 'trace_header'):
                        group_coord_x = trace.stats.su.trace_header.group_coordinate_x
                        scalar = trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                        input_format = 'su'
                    else:
                        # Fallback: try using distance but without adding to shot position
                        if hasattr(trace.stats, 'distance'):
                            group_coord_x = trace.stats.distance
                            scalar = 1
                            input_format = 'fallback'
                        else:
                            # Last resort: assume regular spacing from shot
                            group_coord_x = shot_pos + j * 2.0  # 2m spacing as default
                            scalar = 1
                            input_format = 'default'
                    
                    # Apply coordinate scalar if available
                    if scalar != 0:
                        if scalar < 0:
                            trace_pos = group_coord_x / abs(scalar)
                        else:
                            trace_pos = group_coord_x * scalar
                    else:
                        trace_pos = group_coord_x
                    
                    # Debug: collect info for first few traces
                    if len(debug_info) < 10:
                        debug_info.append(f"Shot {i+1} trace {j+1}: {input_format} group_coord_x={group_coord_x}, scalar={scalar}, final_pos={trace_pos:.1f}")
                        
                except (AttributeError, KeyError):
                    # Fallback: assume regular spacing from shot
                    trace_pos = shot_pos + j * 2.0  # 2m spacing as default
                    if len(debug_info) < 10:
                        debug_info.append(f"Shot {i+1} trace {j+1}: shot_pos={shot_pos:.1f}, fallback_pos={trace_pos:.1f}")
                        
                all_positions.add(trace_pos)
                geophone_positions.append(trace_pos)
            
            shot_geophone_positions[i] = geophone_positions
        
        if not all_positions:
            return 100.0, 10.0, 50.0  # Fallback defaults
            
        all_positions = sorted(list(all_positions))
        min_pos = min(all_positions)
        max_pos = max(all_positions)
        survey_extent = max_pos - min_pos
        
        # Set reasonable defaults: use 100% of survey extent as default window size
        default_window_size = max(1.0, survey_extent)
        
        # Calculate maximum shot offset based on survey extent
        # For initial setup, use a reasonable default based on the survey geometry
        max_offset = 0
        min_pos = min(all_positions)
        max_pos = max(all_positions)
        
        for shot_pos in self.shot_positions:
            # Distance from shot to closest edge of survey
            offset_to_start = abs(shot_pos - min_pos)
            offset_to_end = abs(shot_pos - max_pos)
            shot_max_offset = min(offset_to_start, offset_to_end)
            max_offset = max(max_offset, shot_max_offset)
        
        max_shot_offset = max(10.0, max_offset)  # At least 10m minimum
        
        print(f"Survey geometry calculation debug:")
        for info in debug_info:
            print(f"  {info}")
        print(f"Survey geometry: extent = {survey_extent:.1f}m (from {min_pos:.1f}m to {max_pos:.1f}m)")
        print(f"Default window size set to {default_window_size:.1f}m (100% of survey extent)")
        print(f"Maximum shot offset calculated: {max_shot_offset:.1f}m")
        
        return survey_extent, default_window_size, max_shot_offset
    
    def _calculateDefaultWindowStep(self):
        """Calculate default window step based on geophone spacing"""
        all_geophones = []
        
        # Collect all geophone positions
        for stream in self.streams:
            for trace in stream:
                try:
                    # Try to get group coordinates like in surface_wave_analysis.py
                    if hasattr(trace.stats, 'segy') and hasattr(trace.stats.segy, 'trace_header'):
                        group_coord_x = trace.stats.segy.trace_header.group_coordinate_x
                        scalar = trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                    elif hasattr(trace.stats, 'su') and hasattr(trace.stats.su, 'trace_header'):
                        group_coord_x = trace.stats.su.trace_header.group_coordinate_x
                        scalar = trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                    else:
                        # Fallback: try using distance
                        if hasattr(trace.stats, 'distance'):
                            group_coord_x = trace.stats.distance
                            scalar = 1
                        else:
                            continue  # Skip this trace
                    
                    # Apply coordinate scalar if available
                    if scalar != 0:
                        if scalar < 0:
                            trace_pos = group_coord_x / abs(scalar)
                        else:
                            trace_pos = group_coord_x * scalar
                    else:
                        trace_pos = group_coord_x
                        
                    all_geophones.append(trace_pos)
                        
                except (AttributeError, KeyError):
                    continue
        
        if len(all_geophones) < 2:
            return 2.0  # Default 2m step if can't determine spacing
        
        # Remove duplicates and sort
        unique_geophones = sorted(list(set(all_geophones)))
        
        if len(unique_geophones) < 2:
            return 2.0  # Default 2m step
        
        # Calculate spacings between consecutive geophones
        spacings = [unique_geophones[i+1] - unique_geophones[i] 
                   for i in range(len(unique_geophones)-1)]
        
        # Use median spacing as default step
        spacings.sort()
        median_spacing = spacings[len(spacings) // 2]
        
        return median_spacing
    
    def _calculateMaxShotOffset(self, window_size):
        """Calculate maximum shot offset based on window size and survey geometry"""
        # For a window of given size, the max offset should be the distance
        # from the shot to the edge of the window when positioned at survey extremes
        
        # Get all shot and geophone positions
        shot_positions = []
        geophone_positions = []
        
        for i, stream in enumerate(self.streams):
            shot_positions.append(self.shot_positions[i])
            
            for trace in stream:
                try:
                    # Get geophone position
                    if hasattr(trace.stats, 'segy') and hasattr(trace.stats.segy, 'trace_header'):
                        group_coord_x = trace.stats.segy.trace_header.group_coordinate_x
                        scalar = trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                    elif hasattr(trace.stats, 'su') and hasattr(trace.stats.su, 'trace_header'):
                        group_coord_x = trace.stats.su.trace_header.group_coordinate_x
                        scalar = trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                    else:
                        if hasattr(trace.stats, 'distance'):
                            group_coord_x = trace.stats.distance
                            scalar = 1
                        else:
                            continue
                    
                    # Apply coordinate scalar
                    if scalar != 0:
                        if scalar < 0:
                            geophone_pos = group_coord_x / abs(scalar)
                        else:
                            geophone_pos = group_coord_x * scalar
                    else:
                        geophone_pos = group_coord_x
                        
                    geophone_positions.append(geophone_pos)
                        
                except (AttributeError, KeyError):
                    continue
        
        if not shot_positions or not geophone_positions:
            return 100.0  # Default fallback
        
        min_geophone = min(geophone_positions)
        max_geophone = max(geophone_positions)
        min_shot = min(shot_positions)
        max_shot = max(shot_positions)
        
        # Calculate the maximum possible offset:
        # - Window can be positioned from min_geophone to (max_geophone - window_size)
        # - For each window position, calculate max distance to any shot
        max_offset = 0.0
        
        # Test window at leftmost position
        window_left = min_geophone
        window_right = window_left + window_size
        if window_right <= max_geophone:
            # Distance from leftmost shot to left edge, or rightmost shot to right edge
            left_edge_offset = max(0, window_left - min_shot)
            right_edge_offset = max(0, max_shot - window_right)
            max_offset = max(max_offset, left_edge_offset, right_edge_offset)
        
        # Test window at rightmost position
        window_right = max_geophone
        window_left = window_right - window_size
        if window_left >= min_geophone:
            # Distance from leftmost shot to left edge, or rightmost shot to right edge
            left_edge_offset = max(0, window_left - min_shot)
            right_edge_offset = max(0, max_shot - window_right)
            max_offset = max(max_offset, left_edge_offset, right_edge_offset)
        
        return max(10.0, max_offset)  # At least 10m minimum
    
    def calculateWindows(self):
        """Calculate all possible window positions (Xmids) based on trace count that matches window size"""
        # Store existing data to preserve where possible
        previous_windows = self.available_windows.copy() if hasattr(self, 'available_windows') else []
        previous_subsets = self.window_subsets.copy() if hasattr(self, 'window_subsets') else {}
        
        # Reset for recalculation
        self.available_windows = []
        self.window_subsets = {}
        
        if not self.streams or not self.shot_positions:
            return
            
        # Get offset constraints from spinboxes
        min_shot_offset = self.min_shot_offset_edit.value()
        max_shot_offset = self.max_shot_offset_edit.value()
        
        # First, determine the optimal number of traces for the desired window size
        self._calculateOptimalTraceCount()
        
        if self.window_num_traces is None:
            return
            
        # Get all available trace positions across all shots to determine survey extent
        all_positions = set()
        for i, stream in enumerate(self.streams):
            shot_pos = self.shot_positions[i]
            for j, trace in enumerate(stream):
                # Get trace position from group coordinates (receiver position), not shot + distance
                try:
                    # Try to get group coordinates like in surface_wave_analysis.py
                    if hasattr(trace.stats, 'segy') and hasattr(trace.stats.segy, 'trace_header'):
                        group_coord_x = trace.stats.segy.trace_header.group_coordinate_x
                        scalar = trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                    elif hasattr(trace.stats, 'su') and hasattr(trace.stats.su, 'trace_header'):
                        group_coord_x = trace.stats.su.trace_header.group_coordinate_x
                        scalar = trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                    else:
                        # Fallback: try using distance but without adding to shot position
                        if hasattr(trace.stats, 'distance'):
                            group_coord_x = trace.stats.distance
                            scalar = 1
                        else:
                            # Last resort: assume regular spacing from shot
                            group_coord_x = shot_pos + j * 2.0  # 2m spacing as default
                            scalar = 1
                    
                    # Apply coordinate scalar if available
                    if scalar != 0:
                        if scalar < 0:
                            trace_pos = group_coord_x / abs(scalar)
                        else:
                            trace_pos = group_coord_x * scalar
                    else:
                        trace_pos = group_coord_x
                        
                except (AttributeError, KeyError):
                    # Fallback: assume regular spacing from shot
                    trace_pos = shot_pos + j * 2.0  # 2m spacing as default
                all_positions.add(trace_pos)
        
        all_positions = sorted(list(all_positions))
        min_pos = min(all_positions)
        max_pos = max(all_positions)
        
        # Calculate possible window centers (Xmids) using user-defined step
        current_xmid = min_pos + self.actual_window_size / 2
        tolerance = 1e-6  # Small tolerance for floating point precision
        
        while current_xmid + self.actual_window_size / 2 <= max_pos + tolerance:
            # Find all valid subset combinations for this window
            subsets = self.findWindowSubsets(current_xmid, min_shot_offset, max_shot_offset)
            
            if subsets:
                self.available_windows.append(current_xmid)
                self.window_subsets[current_xmid] = subsets
            
            current_xmid += self.window_step
    
    def _calculateOptimalTraceCount(self):
        """Calculate the number of traces that best matches the desired window size"""
        if not self.streams or not self.shot_positions:
            self.window_num_traces = None
            self.actual_window_size = None
            return
        
        # Find a representative shot to determine trace spacing
        trace_spacings = []
        
        for i, stream in enumerate(self.streams):
            if len(stream) < 2:
                continue
                
            shot_pos = self.shot_positions[i]
            positions = []
            
            for j, trace in enumerate(stream):
                # Get trace position from group coordinates (receiver position), not shot + distance
                try:
                    # Try to get group coordinates like in surface_wave_analysis.py
                    if hasattr(trace.stats, 'segy') and hasattr(trace.stats.segy, 'trace_header'):
                        group_coord_x = trace.stats.segy.trace_header.group_coordinate_x
                        scalar = trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                    elif hasattr(trace.stats, 'su') and hasattr(trace.stats.su, 'trace_header'):
                        group_coord_x = trace.stats.su.trace_header.group_coordinate_x
                        scalar = trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                    else:
                        # Fallback: try using distance but without adding to shot position
                        if hasattr(trace.stats, 'distance'):
                            group_coord_x = trace.stats.distance
                            scalar = 1
                        else:
                            # Last resort: assume regular spacing from shot
                            group_coord_x = shot_pos + j * 2.0  # 2m spacing as default
                            scalar = 1
                    
                    # Apply coordinate scalar if available
                    if scalar != 0:
                        if scalar < 0:
                            trace_pos = group_coord_x / abs(scalar)
                        else:
                            trace_pos = group_coord_x * scalar
                    else:
                        trace_pos = group_coord_x
                        
                except (AttributeError, KeyError):
                    # Fallback: assume regular spacing from shot
                    trace_pos = shot_pos + j * 2.0  # 2m spacing as default
                positions.append(trace_pos)
            
            if len(positions) >= 2:
                # Calculate average spacing for this shot
                spacings = [positions[j+1] - positions[j] for j in range(len(positions)-1)]
                avg_spacing = sum(spacings) / len(spacings)
                trace_spacings.append(avg_spacing)
        
        if not trace_spacings:
            # Fallback to default
            self.window_num_traces = int(self.window_size / 2.0)  # Assume 2m spacing
            self.actual_window_size = self.window_num_traces * 2.0
            return
        
        # Use the median spacing as representative
        trace_spacings.sort()
        median_spacing = trace_spacings[len(trace_spacings) // 2]
        
        # Calculate optimal number of traces
        # For window size W with spacing S, we need W/S intervals, which means (W/S + 1) traces
        num_intervals = self.window_size / median_spacing
        optimal_num_traces = round(num_intervals) + 1  # +1 because N intervals need N+1 traces
        optimal_num_traces = max(2, optimal_num_traces)  # At least 2 traces (1 interval)
        
        self.window_num_traces = optimal_num_traces
        # Actual window size is determined by the number of intervals, not traces
        self.actual_window_size = (optimal_num_traces - 1) * median_spacing
        
        print(f"Window size optimization: {self.window_size:.1f}m → {num_intervals:.1f} intervals → {optimal_num_traces} traces → {self.actual_window_size:.1f}m actual")
        
    def findWindowSubsets(self, window_center, min_shot_offset, max_shot_offset):
        """Find all valid subset combinations for a given window center using fixed trace count"""
        subsets = []
        
        if self.window_num_traces is None:
            return subsets
        
        # Get current side selection
        selected_side = self.side_combo.currentText()
        
        for i, stream in enumerate(self.streams):
            shot_pos = self.shot_positions[i]
            
            # Calculate window boundaries
            window_half_size = self.actual_window_size / 2
            window_start = window_center - window_half_size  # First trace position
            window_end = window_center + window_half_size    # Last trace position
            
            # Add small tolerance for floating point precision
            tolerance = 1e-6
            
            # Calculate offset from window edges (not center)
            # Offset is the distance from shot to the nearest window edge
            if shot_pos < (window_start - tolerance):
                # Shot is to the left of window
                shot_offset = window_start - shot_pos
            elif shot_pos > (window_end + tolerance):
                # Shot is to the right of window  
                shot_offset = shot_pos - window_end
            else:
                # Shot is at window edge or inside the window
                # Calculate the actual distance to nearest edge
                left_distance = abs(shot_pos - window_start)
                right_distance = abs(shot_pos - window_end)
                
                if left_distance <= tolerance or right_distance <= tolerance:
                    # Shot is essentially at the edge (within tolerance)
                    shot_offset = 0.0
                else:
                    # Shot is truly inside the window - exclude it
                    shot_offset = -1.0
            
            
            # Check if shot is within the allowed offset range
            # min_shot_offset: minimum distance from window edge (0 means shot can be at edge, but not inside)
            # max_shot_offset: maximum distance from window edge
            # Exclude shots inside the window (shot_offset < 0)
            
            if shot_offset < 0 or shot_offset < min_shot_offset or shot_offset > max_shot_offset:
                continue  # Skip this shot if inside window or offset is outside allowed range
            
            # Apply side filtering based on shot position relative to window center
            if selected_side == 'left' and shot_pos >= window_center:
                continue  # Skip shots on right side when left is selected
            elif selected_side == 'right' and shot_pos <= window_center:
                continue  # Skip shots on left side when right is selected
            # For 'both', include shots from both sides (no additional filtering)
            
            # Find all traces and their positions for this shot
            trace_info = []
            for j, trace in enumerate(stream):
                # Get trace position from group coordinates (receiver position), not shot + distance
                try:
                    # Try to get group coordinates like in surface_wave_analysis.py
                    if hasattr(trace.stats, 'segy') and hasattr(trace.stats.segy, 'trace_header'):
                        group_coord_x = trace.stats.segy.trace_header.group_coordinate_x
                        scalar = trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                    elif hasattr(trace.stats, 'su') and hasattr(trace.stats.su, 'trace_header'):
                        group_coord_x = trace.stats.su.trace_header.group_coordinate_x
                        scalar = trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                    else:
                        # Fallback: try using distance but without adding to shot position
                        if hasattr(trace.stats, 'distance'):
                            group_coord_x = trace.stats.distance
                            scalar = 1
                        else:
                            # Last resort: assume regular spacing from shot
                            group_coord_x = shot_pos + j * 2.0  # 2m spacing as default
                            scalar = 1
                    
                    # Apply coordinate scalar if available
                    if scalar != 0:
                        if scalar < 0:
                            trace_pos = group_coord_x / abs(scalar)
                        else:
                            trace_pos = group_coord_x * scalar
                    else:
                        trace_pos = group_coord_x
                        
                except (AttributeError, KeyError):
                    # Fallback: assume regular spacing from shot
                    trace_pos = j * 2.0  # 2m spacing from origin, not from shot
                
                trace_info.append({
                    'shot_index': i,
                    'trace_index': j,
                    'position': trace_pos,
                    'distance_to_center': abs(trace_pos - window_center)
                })
            
            # Sort traces by position (not distance to center) for interval calculation
            trace_info.sort(key=lambda x: x['position'])
            
            # Select traces with proper intervals
            if len(trace_info) >= self.window_num_traces:
                # Find the best contiguous subset that spans the window
                window_half_size = self.actual_window_size / 2
                window_start = window_center - window_half_size
                window_end = window_center + window_half_size
                
                # Add small tolerance to handle floating point precision issues
                tolerance = 1e-6  # Small tolerance for floating point comparison
                
                # Filter traces that fall within the window bounds (with tolerance)
                window_traces = [t for t in trace_info 
                               if (window_start - tolerance) <= t['position'] <= (window_end + tolerance)]
                
                if len(window_traces) >= self.window_num_traces:
                    # Take evenly spaced traces from within the window
                    if len(window_traces) == self.window_num_traces:
                        selected_traces = window_traces
                    else:
                        # Select evenly distributed traces
                        indices = np.linspace(0, len(window_traces)-1, self.window_num_traces, dtype=int)
                        selected_traces = [window_traces[idx] for idx in indices]
                else:
                    # Not enough traces in window, take closest ones
                    trace_info.sort(key=lambda x: x['distance_to_center'])
                    selected_traces = trace_info[:self.window_num_traces]
                
                # Get FFID from first trace if available
                ffid = f'Shot_{i+1}'  # Default
                if stream and len(stream) > 0:
                    first_trace = stream[0]
                    if hasattr(first_trace, 'stats') and hasattr(first_trace.stats, 'ffid'):
                        ffid = first_trace.stats.ffid
                
                # Add ffid to each trace info
                for trace in selected_traces:
                    trace['ffid'] = ffid
                
                subsets.append({
                    'shot_index': i,
                    'traces': selected_traces,
                    'count': len(selected_traces),
                    'shot_position': shot_pos,
                    'shot_offset': shot_offset
                })
        
        return subsets
    
    def onWindowConfigChanged(self):
        """Handle window configuration changes - validate but don't auto-correct values"""
        # Just update internal values without forcing corrections
        self.window_size = self.window_size_edit.value()
        self.window_step = self.window_step_edit.value()
        self.min_shot_offset = self.min_shot_offset_edit.value()
        self.max_shot_offset = self.max_shot_offset_edit.value()
        self.side = self.side_combo.currentText()
        
        # Clear previous results to indicate recalculation is needed
        self.available_windows = []
        self.window_subsets = {}
        self.window_list.clear()
        self.subset_list.clear()
        
        # Update window info display to show that geometry computation is needed
        if hasattr(self, 'window_info_label'):
            self.window_info_label.setText("Click 'Compute Window Geometry' to calculate windows")
            self.window_info_label.setStyleSheet("QLabel { color: #FF6600; font-size: 10px; font-weight: bold; }")
    
    def _validateWindowingParameters(self):
        """Validate windowing parameters and return list of warnings"""
        warnings = []
        
        # Get current values
        window_size = self.window_size_edit.value()
        window_step = self.window_step_edit.value()
        min_offset = self.min_shot_offset_edit.value()
        max_offset = self.max_shot_offset_edit.value()
        
        # Calculate defaults for validation
        if hasattr(self, 'window_step'):
            default_step = self._calculateDefaultWindowStep()  # Geophone spacing
        else:
            default_step = 2.0  # Fallback
        
        # Validate window size
        if hasattr(self, 'max_possible_window_size'):
            if window_size > self.max_possible_window_size:
                warnings.append(f"Window size ({window_size:.1f}m) exceeds maximum possible size ({self.max_possible_window_size:.1f}m)")
        
        if window_size < default_step * 1.5:  # Less than ~2 traces worth
            warnings.append(f"Window size ({window_size:.1f}m) is smaller than minimum recommended size (~{default_step * 1.5:.1f}m for 2+ traces)")
        
        # Validate window step
        if window_step < default_step * 0.8:  # Smaller than geophone spacing
            warnings.append(f"Window step ({window_step:.1f}m) is smaller than geophone spacing ({default_step:.1f}m)")
        
        if hasattr(self, 'max_possible_window_size') and window_step > self.max_possible_window_size:
            warnings.append(f"Window step ({window_step:.1f}m) exceeds maximum survey width ({self.max_possible_window_size:.1f}m)")
        
        # Validate offsets
        if min_offset < 0 and max_offset < 0:
            warnings.append("Both minimum and maximum shot offsets are negative")
        
        if min_offset > max_offset:
            warnings.append(f"Minimum offset ({min_offset:.1f}m) is greater than maximum offset ({max_offset:.1f}m)")
        
        if max_offset == 0:
            warnings.append("Maximum shot offset is zero - this may exclude all shots")
        
        return warnings
    
    
    def computeWindowGeometry(self):
        """Compute window geometry based on current settings"""
        if not self.streams:
            QMessageBox.warning(self, "No Data", "Please load seismic data first.")
            return
            
        try:
            # First, validate parameters and warn about issues
            warnings = self._validateWindowingParameters()
            if warnings:
                warning_text = "Parameter Issues Detected:\n\n" + "\n".join(f"• {w}" for w in warnings)
                warning_text += "\n\nDo you want to continue with these parameters anyway?"
                
                reply = QMessageBox.question(
                    self, 
                    "Parameter Validation Warning", 
                    warning_text,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
            
            # Calculate survey geometry for window calculations (but don't reset max offset)
            survey_extent, default_window_size, _ = self._calculateSurveyGeometry()
            
            # Keep user-defined max shot offset (don't override it)
            # Only update the tooltip with calculated max for reference
            if hasattr(self, 'max_shot_offset_edit'):
                calculated_max = self._calculateMaxShotOffset(self.window_size)
                self.max_shot_offset_edit.setToolTip(f"Maximum shot offset (distance from window edge). Suggested max: {calculated_max:.1f}m")
            
            # Calculate windows based on current settings
            self.calculateWindows()
            self.populateWindowList()
            
            # If we have windows, automatically display the first window's seismogram and spectrum
            if self.available_windows and self.window_subsets:
                # Select first window automatically
                self.window_list.setCurrentRow(0)
                
                # Trigger initial visualization of first window/subset
                if hasattr(self, 'updateVisualization'):
                    # Add a small delay to ensure the UI is updated before visualization
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(100, self.updateVisualization)
            
            # Provide feedback to user
            if self.available_windows:
                num_windows = len(self.available_windows)
                if hasattr(self, 'actual_window_size') and self.actual_window_size is not None:
                    window_size_info = f"{self.actual_window_size:.1f}m actual size"
                else:
                    window_size_info = f"{self.window_size:.1f}m requested size"
                    
                trace_info = f"{self.window_num_traces} traces per window" if self.window_num_traces else "variable traces"
                
                # Update window info display with successful computation results
                if hasattr(self, 'window_info_label'):
                    if self.window_num_traces is not None and self.actual_window_size is not None:
                        self.window_info_label.setText(f"→ {self.window_num_traces} traces, {self.actual_window_size:.1f}m actual size")
                    else:
                        self.window_info_label.setText("Window geometry computed successfully")
                    # Reset styling to normal
                    self.window_info_label.setStyleSheet("QLabel { color: #666; font-size: 10px; }")
                
                QMessageBox.information(
                    self, 
                    "Window Geometry Computed", 
                    f"Successfully computed {num_windows} analysis windows.\n\n"
                    f"Window configuration:\n"
                    f"• {window_size_info}\n"
                    f"• {trace_info}\n"
                    f"• Survey extent: {self.survey_extent:.1f}m\n\n"
                    f"Ready for dispersion analysis."
                )
                
                # Enable seismogram controls now that geometry is computed and traces can be displayed
                self.enableSeismogramControls(True)
            else:
                QMessageBox.warning(
                    self, 
                    "No Windows Generated", 
                    "No analysis windows could be generated with the current settings.\n\n"
                    "Please check your window size and offset constraints."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error Computing Geometry", 
                f"An error occurred while computing window geometry:\n\n{str(e)}"
            )
    
    def populateWindowList(self):
        """Populate the window list with available Xmids"""
        # Store current selection to restore it after repopulating
        current_selection = None
        current_item = self.window_list.currentItem()
        if current_item:
            current_selection = current_item.data(Qt.UserRole)  # The xmid value
        
        self.window_list.clear()
        
        for xmid in self.available_windows:
            subsets = self.window_subsets[xmid]
            valid_shot_count = len(subsets)
            
            # All shots should have the same number of traces now
            if self.window_num_traces is not None and self.actual_window_size is not None:
                item_text = f"Xmid: {xmid:.1f} m ({valid_shot_count} shots, {self.window_num_traces} traces each, {self.actual_window_size:.1f}m actual)"
            else:
                # Fallback for cases where optimization failed
                shot_info_parts = []
                for subset in subsets:
                    trace_count = subset['count']
                    shot_info_parts.append(f"{trace_count}")
                
                shot_info = f"[{', '.join(shot_info_parts)}]"
                item_text = f"Xmid: {xmid:.1f} m ({valid_shot_count} shots: {shot_info} traces)"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, xmid)
            self.window_list.addItem(item)
        
        # Restore previous selection if it still exists, otherwise select first window
        selection_restored = False
        if current_selection is not None:
            for i in range(self.window_list.count()):
                item = self.window_list.item(i)
                if item.data(Qt.UserRole) == current_selection:
                    self.window_list.setCurrentRow(i)
                    selection_restored = True
                    break
        
        # If selection couldn't be restored and we have windows, select first one
        if not selection_restored and self.available_windows:
            self.window_list.setCurrentRow(0)
    
    def populateSubsetList(self, xmid):
        """Populate the subset list for the selected window"""
        # Store current subset selection to restore it after repopulating
        current_subset_selection = self.subset_list.currentRow()
        
        self.subset_list.clear()
        
        if xmid not in self.window_subsets:
            return
            
        subsets = self.window_subsets[xmid]
        for i, subset in enumerate(subsets):
            shot_index = subset['shot_index']
            trace_count = subset['count']
            shot_offset = subset.get('shot_offset', 0.0)
            ffid = subset['traces'][0]['ffid'] if subset['traces'] else f'Shot_{shot_index+1}'
            
            item_text = f"{ffid}: {trace_count} traces (offset: {shot_offset:.1f}m)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, i)
            self.subset_list.addItem(item)
        
        # Restore previous subset selection if valid, otherwise select first subset
        if (current_subset_selection is not None and 
            current_subset_selection >= 0 and 
            current_subset_selection < len(subsets)):
            self.subset_list.setCurrentRow(current_subset_selection)
        elif subsets:
            self.subset_list.setCurrentRow(0)
    
    def onWindowSelectionChanged(self):
        """Handle window selection change"""
        # Save current window's curve if any
        self.saveCurrentWindowCurve()
        
        current_item = self.window_list.currentItem()
        if current_item:
            xmid = current_item.data(Qt.UserRole)
            # Find the closest match in available_windows to handle floating point precision
            if self.available_windows:
                self.current_window_index = min(range(len(self.available_windows)),
                                              key=lambda i: abs(self.available_windows[i] - xmid))
            
            # Update current window key
            self.current_window_key = f'window_{xmid:.1f}'
            
            self.populateSubsetList(xmid)
            
            # Populate the new dispersion workflow lists
            window_key = f'window_{xmid:.1f}'
            self.populateSubsetImageList(window_key)
            self.populateStackedResultsList(window_key)
            
            # Check if we have stacked results for this window
            has_stacked_result = (hasattr(self, 'stacked_results') and 
                                window_key in self.stacked_results)
            
            if has_stacked_result:
                # If we have stacked results, show them directly and skip updateVisualization
                print(f"Auto-displaying stacked result for {window_key}")
                self.showStackedResult(window_key)
            else:
                # No stacked results, use normal visualization update
                self.updateVisualization()
            
            # Load saved curve for this window if any (curves go on top of whatever is displayed)
            self.loadWindowCurve()
            
            # Update pseudo-section plot to reflect any curve changes
            self.updatePseudoSection()
    
    def onSubsetSelectionChanged(self):
        """Handle subset selection change"""
        current_item = self.subset_list.currentItem()
        if current_item:
            self.current_subset_index = current_item.data(Qt.UserRole)
            
            # Update visualization first
            self.updateVisualization()
            
            # Update spatial layout for this trace subset
            self.updateSpatialLayoutForTraceSubset()
            
            # Check if dispersion analysis has been completed for this subset
            current_window_item = self.window_list.currentItem()
            if current_window_item:
                window_xmid = current_window_item.data(Qt.UserRole)
                window_key = f'window_{window_xmid:.1f}'
                
                # Look for corresponding dispersion image
                if (hasattr(self, 'analysis_results') and 
                    window_key in self.analysis_results):
                    
                    subset_dispersions = self.analysis_results[window_key].get('subset_dispersions', {})
                    subset_key = f'subset_{self.current_subset_index}'
                    
                    if subset_key in subset_dispersions:
                        # Dispersion image exists, display it automatically
                        print(f"Auto-displaying dispersion image for {subset_key}")
                        self.previewSubsetImage(subset_key)
                        return
            
            # Clear analysis results for new selection if no dispersion image found
            if hasattr(self, 'analysis_results'):
                current_key = self.getCurrentSubsetKey()
                if current_key not in self.analysis_results:
                    self.clearAnalysisPlots()
    
    def getCurrentSubsetKey(self):
        """Get key for current window/subset combination"""
        current_window_item = self.window_list.currentItem()
        current_subset_item = self.subset_list.currentItem()
        
        if current_window_item and current_subset_item:
            window_xmid = current_window_item.data(Qt.UserRole)  # Float value
            subset_index = current_subset_item.data(Qt.UserRole)  # Int index
            if window_xmid is not None and subset_index is not None:
                return f'window_{window_xmid:.1f}_subset_{subset_index}'
        return None
    
    def clearAnalysisPlots(self):
        """Clear analysis plots"""
        self.spectrum_plot.clear()
        self.dispersion_plot.clear()
        
    def onModeChanged(self):
        """Handle mode selection change"""
        old_mode = self.current_mode
        self.current_mode = self.mode_selector.currentIndex()
        print(f"DEBUG: Mode changed from M{old_mode} to M{self.current_mode} ({self.mode_selector.currentText()})")
        
        # NOTE: Do NOT change existing point colors - they should keep their original mode colors
        # Only new points will use the new mode
        
        # Update curve line color if it exists (for current interpolated curve)
        if self.curve_line is not None:
            current_color = self.mode_colors.get(self.current_mode, 'red')
            self.curve_line.setPen(pg.mkPen(color=current_color, width=2))
        
        # Update pseudo-section if it has curves displayed
        self.updatePseudoSection()

    def saveCurrentWindowCurve(self):
        """Save the current window's picked curve to memory"""
        if (self.current_window_key and 
            len(self.picked_points) > 0 and 
            self.curve_line is not None):
            
            # Get current curve data
            curve_data = {
                'picked_points': self.picked_points.copy(),
                'frequencies': [],
                'velocities': [],
                'interpolated': True
            }
            
            # If we have an interpolated curve, get its data
            if hasattr(self.curve_line, 'xData') and hasattr(self.curve_line, 'yData'):
                curve_data['frequencies'] = self.curve_line.xData
                curve_data['velocities'] = self.curve_line.yData
            
            # Store in window curves dictionary
            self.window_curves[self.current_window_key] = curve_data
            print(f"Saved curve for {self.current_window_key} with {len(self.picked_points)} picked points")
            self.updateWindowCurvesStatus()

    def loadWindowCurve(self):
        """Load and display saved curve for current window"""
        if not self.current_window_key:
            return
            
        # Clear current picking state
        self.clearCurrentPickingDisplay()
        
        # Check if we have a saved curve for this window
        if self.current_window_key in self.window_curves:
            curve_data = self.window_curves[self.current_window_key]
            
            # Restore picked points
            self.picked_points = curve_data['picked_points'].copy()
            
            # Restore picked point visual items
            self.picked_point_items = []
            for point_data in self.picked_points:
                # Handle both old and new data formats
                if isinstance(point_data, dict):
                    freq = point_data['frequency']
                    vel = point_data['velocity']
                    mode = point_data.get('mode', 0)  # Default to fundamental mode
                else:
                    freq, vel = point_data  # Old format compatibility
                    mode = 0  # Default to fundamental mode
                
                # Get color for this point's mode
                point_color = self.mode_colors.get(mode, 'red')
                
                point_item = pg.ScatterPlotItem(
                    x=[freq], y=[vel],
                    pen=pg.mkPen(color=point_color, width=2),
                    brush=pg.mkBrush(color=point_color),
                    size=5, symbol='o'
                )
                self.dispersion_plot.addItem(point_item)
                self.picked_point_items.append(point_item)
            
            # Restore interpolated curve if available
            if ('frequencies' in curve_data and 'velocities' in curve_data and 
                len(curve_data['frequencies']) > 0):
                
                # Use current mode's color for the curve line
                current_color = self.mode_colors.get(self.current_mode, 'red')
                
                self.curve_line = pg.PlotDataItem(
                    x=curve_data['frequencies'], y=curve_data['velocities'],
                    pen=pg.mkPen(color=current_color, width=3)
                )
                self.dispersion_plot.addItem(self.curve_line)
            
            # Enable/disable buttons based on curve state
            if len(self.picked_points) >= 2:
                self.interpolate_button.setEnabled(True)
            if len(self.picked_points) > 0:
                self.clear_picking_button.setEnabled(True)
                
            print(f"Loaded curve for {self.current_window_key} with {len(self.picked_points)} picked points")

    def clearCurrentPickingDisplay(self):
        """Clear current picking display without affecting stored curves"""
        # Remove visual items from plot
        for item in self.picked_point_items:
            if item is not None:
                self.dispersion_plot.removeItem(item)
        
        if self.curve_line is not None:
            self.dispersion_plot.removeItem(self.curve_line)
            self.curve_line = None
        
        # Clear current state
        self.picked_points = []
        self.picked_point_items = []

    def updateWindowCurvesStatus(self):
        """Update the status display for window curves"""
        curve_count = len(self.window_curves)
        self.window_curves_status.setText(f"Window Curves: {curve_count}")
        
        # Enable export if we have any curves
        if curve_count > 0 or self.extracted_curves:
            self.export_curves_button.setEnabled(True)
        else:
            self.export_curves_button.setEnabled(False)

    def createRightPanel(self):
        """Create right panel with analysis plots"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Create vertical splitter for three plots
        v_splitter = QSplitter(Qt.Vertical)
        layout.addWidget(v_splitter)
        
        # Top plot - Dispersion image
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        disp_label = QLabel("Dispersion Image (Phase Shift Method)")
        disp_label.setFont(QFont("Arial", 10, QFont.Bold))
        top_layout.addWidget(disp_label)
        
        # Dispersion colormap controls
        disp_controls_widget = QWidget()
        disp_controls_layout = QHBoxLayout(disp_controls_widget)
        disp_controls_layout.setContentsMargins(0, 5, 0, 5)
        
        disp_colormap_label = QLabel("Colormap:")
        disp_controls_layout.addWidget(disp_colormap_label)
        
        self.disp_colormap_combo = QComboBox()
        self.disp_colormap_combo.addItems(['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'turbo', 'hot', 'cool', 'coolwarm', 'seismic', 'RdBu', 'spring', 'summer', 'autumn', 'winter', 'gray', 'bone', 'copper', 'Blues', 'Reds', 'Greens', 'Oranges', 'Purples', 'Greys', 'jet', 'rainbow', 'pink', 'terrain', 'ocean'])
        self.disp_colormap_combo.setCurrentText("gray")
        self.disp_colormap_combo.currentTextChanged.connect(self.refreshDispersionColormap)
        disp_controls_layout.addWidget(self.disp_colormap_combo)
        
        disp_controls_layout.addStretch()  # Push controls to the left
        top_layout.addWidget(disp_controls_widget)
        
        # Dispersion plot widget with colorbar layout
        dispersion_plot_widget = QWidget()
        dispersion_plot_layout = QHBoxLayout(dispersion_plot_widget)
        dispersion_plot_layout.setContentsMargins(0, 0, 0, 0)
        
        self.dispersion_plot = pg.PlotWidget()
        self.dispersion_plot.setBackground('w')
        
        # Set initial zoom limits to prevent excessive zoom-out
        self.dispersion_plot.getViewBox().setLimits(
            xMin=0, xMax=500,     # Reasonable frequency range
            yMin=0, yMax=2000     # Reasonable velocity range
        )
        
        # Set margins to prevent axis labels from being cut off
        self.dispersion_plot.getPlotItem().setContentsMargins(10, 10, 10, 10)  # left, top, right, bottom margins
        
        # Show top and right axes without labels
        self.dispersion_plot.showAxis('top')
        self.dispersion_plot.showAxis('right')
        self.dispersion_plot.getAxis('top').setStyle(showValues=False)
        self.dispersion_plot.getAxis('right').setStyle(showValues=False)
        self.dispersion_plot.getAxis('top').setLabel('')
        self.dispersion_plot.getAxis('right').setLabel('')
        self.dispersion_plot.setLabel('left', 'Phase Velocity', 'm/s')
        self.dispersion_plot.setLabel('bottom', 'Frequency', 'Hz')
        self.dispersion_plot.showAxis('top')
        dispersion_plot_layout.addWidget(self.dispersion_plot)
        
        # Initialize dispersion colorbar (will be added when plotting)
        self.dispersion_colorbar = None
        
        top_layout.addWidget(dispersion_plot_widget)
        
        v_splitter.addWidget(top_widget)
        
        # Middle widget - Tabbed view (Spectrum/Wiggle)
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        
        # Create tab widget
        self.data_tabs = QTabWidget()
        middle_layout.addWidget(self.data_tabs)
        
        # Spectrum tab
        spectrum_tab = QWidget()
        spectrum_tab_layout = QVBoxLayout(spectrum_tab)
        
        # Spectrum colormap controls
        spectrum_controls_widget = QWidget()
        spectrum_controls_layout = QHBoxLayout(spectrum_controls_widget)
        spectrum_controls_layout.setContentsMargins(0, 5, 0, 5)
        
        spectrum_colormap_label = QLabel("Colormap:")
        spectrum_controls_layout.addWidget(spectrum_colormap_label)
        
        self.spectrum_colormap_combo = QComboBox()
        self.spectrum_colormap_combo.addItems(['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'turbo', 'hot', 'cool', 'coolwarm', 'seismic', 'RdBu', 'spring', 'summer', 'autumn', 'winter', 'gray', 'bone', 'copper', 'Blues', 'Reds', 'Greens', 'Oranges', 'Purples', 'Greys', 'jet', 'rainbow', 'pink', 'terrain', 'ocean'])
        self.spectrum_colormap_combo.setCurrentText("viridis")
        self.spectrum_colormap_combo.currentTextChanged.connect(self.refreshSpectrumColormap)
        spectrum_controls_layout.addWidget(self.spectrum_colormap_combo)
        
        spectrum_controls_layout.addStretch()  # Push controls to the left
        spectrum_tab_layout.addWidget(spectrum_controls_widget)
        
        # Spectrum plot widget with colorbar layout
        spectrum_plot_widget = QWidget()
        spectrum_plot_layout = QHBoxLayout(spectrum_plot_widget)
        spectrum_plot_layout.setContentsMargins(0, 0, 0, 0)
        
        self.spectrum_plot = pg.PlotWidget()
        self.spectrum_plot.setBackground('w')
        
        # Set initial zoom limits to prevent excessive zoom-out
        self.spectrum_plot.getViewBox().setLimits(
            xMin=0, xMax=200,     # Reasonable frequency range
            yMin=0, yMax=1000     # Reasonable geophone position range
        )
        
        # Set margins to prevent axis labels from being cut off
        self.spectrum_plot.getPlotItem().setContentsMargins(10, 10, 10, 10)  # left, top, right, bottom margins
        
        # Show top and right axes without labels
        self.spectrum_plot.showAxis('top')
        self.spectrum_plot.showAxis('right')
        self.spectrum_plot.getAxis('top').setStyle(showValues=False)
        self.spectrum_plot.getAxis('right').setStyle(showValues=False)
        self.spectrum_plot.getAxis('top').setLabel('')
        self.spectrum_plot.getAxis('right').setLabel('')
        self.spectrum_plot.setLabel('left', 'X (m)', 'm')
        self.spectrum_plot.setLabel('bottom', 'Frequency', 'Hz')
        self.spectrum_plot.showAxis('top')
        spectrum_plot_layout.addWidget(self.spectrum_plot)
        
        # Initialize spectrum colorbar (will be added when plotting)
        self.spectrum_colorbar = None
        
        spectrum_tab_layout.addWidget(spectrum_plot_widget)
        
        # Wiggle tab
        wiggle_tab = QWidget()
        wiggle_tab_layout = QVBoxLayout(wiggle_tab)
        
        # Seismogram controls
        seismogram_controls = QWidget()
        seismogram_controls_layout = QHBoxLayout(seismogram_controls)
        seismogram_controls_layout.setContentsMargins(5, 5, 5, 5)
        
        # Helper function to add vertical separator
        def add_separator():
            separator = QFrame()
            separator.setFrameShape(QFrame.VLine)
            separator.setFrameShadow(QFrame.Sunken)
            separator.setLineWidth(1)
            separator.setMidLineWidth(0)
            seismogram_controls_layout.addWidget(separator)
        
        # GROUP 1: Display & Trace Options
        # Display mode control (Image/Wiggle)
        seismogram_controls_layout.addWidget(QLabel("Display:"))
        self.display_mode_combo = QComboBox()
        self.display_mode_combo.addItems(["Wiggle", "Image"])
        self.display_mode_combo.setCurrentText("Wiggle")
        self.display_mode_combo.currentTextChanged.connect(self.refreshSeismogram)
        seismogram_controls_layout.addWidget(self.display_mode_combo)
        
        # Trace by control (moved after Display)
        seismogram_controls_layout.addWidget(QLabel("Trace by:"))
        self.trace_by_combo = QComboBox()
        self.trace_by_combo.addItems(["Number", "Position"])
        self.trace_by_combo.setCurrentText("Position")
        self.trace_by_combo.currentTextChanged.connect(self.refreshSeismogram)
        seismogram_controls_layout.addWidget(self.trace_by_combo)
        
        # Separator between groups
        add_separator()
        
        # GROUP 2: Processing Options (Normalize to Clip)
        # Normalize checkbox
        self.normalize_check = QCheckBox("Normalize")
        self.normalize_check.setChecked(True)
        self.normalize_check.toggled.connect(self.refreshSeismogram)
        seismogram_controls_layout.addWidget(self.normalize_check)
        
        # Gain control (wiggle-only)
        self.gain_label = QLabel("Gain:")
        seismogram_controls_layout.addWidget(self.gain_label)
        self.gain_spinbox = QDoubleSpinBox()
        self.gain_spinbox.setRange(1.0, 20.0)
        self.gain_spinbox.setValue(1.0)
        self.gain_spinbox.setSingleStep(1.0)
        self.gain_spinbox.valueChanged.connect(self.refreshSeismogram)
        seismogram_controls_layout.addWidget(self.gain_spinbox)
        
        # Fill mode (wiggle-only)
        self.fill_label = QLabel("Fill:")
        seismogram_controls_layout.addWidget(self.fill_label)
        self.fill_combo = QComboBox()
        self.fill_combo.addItems(["Positive", "Negative", "None"])
        self.fill_combo.setCurrentText("Negative")
        self.fill_combo.currentTextChanged.connect(self.refreshSeismogram)
        seismogram_controls_layout.addWidget(self.fill_combo)
        
        # Clip checkbox (wiggle-only)
        self.clip_check = QCheckBox("Clip")
        self.clip_check.setChecked(True)
        self.clip_check.toggled.connect(self.refreshSeismogram)
        seismogram_controls_layout.addWidget(self.clip_check)
        
        # Colormap control (image-only)
        self.colormap_label = QLabel("Colormap:")
        seismogram_controls_layout.addWidget(self.colormap_label)
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'turbo', 'hot', 'cool', 'coolwarm', 'seismic', 'RdBu', 'spring', 'summer', 'autumn', 'winter', 'gray', 'bone', 'copper', 'Blues', 'Reds', 'Greens', 'Oranges', 'Purples', 'Greys', 'jet', 'rainbow', 'pink', 'terrain', 'ocean'])
        self.colormap_combo.setCurrentText("gray")
        self.colormap_combo.currentTextChanged.connect(self.refreshSeismogram)
        seismogram_controls_layout.addWidget(self.colormap_combo)
        
        # Separator between groups
        add_separator()
        
        # GROUP 3: Time Options (Max time to Fix max time)
        # Max time control
        seismogram_controls_layout.addWidget(QLabel("Max time:"))
        self.max_time_spinbox = QDoubleSpinBox()
        self.max_time_spinbox.setRange(0.001, 10.0)
        self.max_time_spinbox.setValue(0.150)
        self.max_time_spinbox.setSingleStep(0.001)
        self.max_time_spinbox.setDecimals(3)
        self.max_time_spinbox.setSuffix(" s")
        self.max_time_spinbox.valueChanged.connect(self.refreshSeismogram)
        seismogram_controls_layout.addWidget(self.max_time_spinbox)
        
        # Fix max time checkbox
        self.fix_max_time_check = QCheckBox("Fix max time")
        self.fix_max_time_check.setChecked(False)
        self.fix_max_time_check.toggled.connect(self.refreshSeismogram)
        seismogram_controls_layout.addWidget(self.fix_max_time_check)
        
        seismogram_controls_layout.addStretch()
        wiggle_tab_layout.addWidget(seismogram_controls)
        
        # Initialize control visibility based on default display mode
        self.updateControlsForDisplayMode()
        
        # Initially disable seismogram controls until geometry is computed
        self.enableSeismogramControls(False)
        
        # Seismogram plot widget with colorbar layout
        seismogram_plot_widget = QWidget()
        seismogram_plot_layout = QHBoxLayout(seismogram_plot_widget)
        seismogram_plot_layout.setContentsMargins(0, 0, 0, 0)
        
        self.wiggle_plot = pg.PlotWidget()
        self.wiggle_plot.setBackground('w')
        
        # Set initial zoom limits to prevent excessive zoom-out
        self.wiggle_plot.getViewBox().setLimits(
            xMin=-1000, xMax=1000,  # Reasonable distance range
            yMin=0, yMax=10         # Reasonable time range
        )
        
        # Set margins to prevent axis labels from being cut off
        self.wiggle_plot.getPlotItem().setContentsMargins(10, 10, 10, 10)  # left, top, right, bottom margins
        
        # Show top and right axes without labels
        self.wiggle_plot.showAxis('top')
        self.wiggle_plot.showAxis('right')
        self.wiggle_plot.getAxis('top').setStyle(showValues=False)
        self.wiggle_plot.getAxis('right').setStyle(showValues=False)
        self.wiggle_plot.getAxis('top').setLabel('')
        self.wiggle_plot.getAxis('right').setLabel('')
        self.wiggle_plot.setLabel('left', 'Time', 's')
        self.wiggle_plot.setLabel('bottom', 'X (m)', 'm')
        self.wiggle_plot.showAxis('top')
        # Set reverse Y axis for seismic convention (time increases downward)
        self.wiggle_plot.getViewBox().invertY(True)
        seismogram_plot_layout.addWidget(self.wiggle_plot)
        
        # Initialize seismogram colorbar (will be added when plotting in image mode)
        self.seismogram_colorbar = None
        
        wiggle_tab_layout.addWidget(seismogram_plot_widget)
        
        # Spatial Layout tab
        spatial_tab = QWidget()
        spatial_tab_layout = QVBoxLayout(spatial_tab)
        
        # Spatial plot widget
        self.spatial_plot = pg.PlotWidget()
        self.spatial_plot.setBackground('w')
        
        # Set initial zoom limits to prevent excessive zoom-out
        self.spatial_plot.getViewBox().setLimits(
            xMin=-1000, xMax=1000,   # Reasonable coordinate range
            yMin=-1000, yMax=1000    # Reasonable coordinate range
        )
        
        # Set margins to prevent axis labels from being cut off
        self.spatial_plot.getPlotItem().setContentsMargins(10, 10, 10, 10)  # left, top, right, bottom margins
        
        # Show top and right axes without labels
        self.spatial_plot.showAxis('top')
        self.spatial_plot.showAxis('right')
        self.spatial_plot.getAxis('top').setStyle(showValues=False)
        self.spatial_plot.getAxis('right').setStyle(showValues=False)
        self.spatial_plot.getAxis('top').setLabel('')
        self.spatial_plot.getAxis('right').setLabel('')
        self.spatial_plot.setLabel('left', '')
        self.spatial_plot.setLabel('bottom', '')
        spatial_tab_layout.addWidget(self.spatial_plot)
        
        # Pseudo-Section tab
        pseudosection_tab = QWidget()
        pseudosection_tab_layout = QVBoxLayout(pseudosection_tab)
        
        # Mode display controls (for visualization only)
        mode_display_widget = QWidget()
        mode_display_layout = QHBoxLayout(mode_display_widget)
        mode_display_layout.setContentsMargins(5, 5, 5, 5)
        
        # Mode display dropdown (read-only for visualization)
        mode_display_label = QLabel("Display Mode:")
        self.mode_display_selector = QComboBox()
        self.mode_display_selector.addItems([
            "M0 - Fundamental", 
            "M1 - 1st Higher", 
            "M2 - 2nd Higher", 
            "M3 - 3rd Higher",
            "M4 - 4th Higher"
        ])
        self.mode_display_selector.setCurrentIndex(0)  # Default to fundamental mode
        # Connect to update pseudo-section when display mode changes
        self.mode_display_selector.currentIndexChanged.connect(self.updatePseudoSection)
        # Note: This is for display only, the actual picking mode is controlled in picking parameters
        
        mode_display_layout.addWidget(mode_display_label)
        mode_display_layout.addWidget(self.mode_display_selector)
        mode_display_layout.addStretch()
        
        pseudosection_tab_layout.addWidget(mode_display_widget)
        
        # Pseudo-section plot widget with colorbar layout
        pseudosection_plot_widget = QWidget()
        pseudosection_plot_layout = QHBoxLayout(pseudosection_plot_widget)
        pseudosection_plot_layout.setContentsMargins(0, 0, 0, 0)
        
        self.pseudosection_plot = pg.PlotWidget()
        self.pseudosection_plot.setBackground('w')
        
        # Set initial zoom limits to prevent excessive zoom-out
        self.pseudosection_plot.getViewBox().setLimits(
            xMin=-1000, xMax=1000,   # Reasonable position range
            yMin=0, yMax=1000        # Reasonable wavelength range
        )
        
        # Set margins to prevent axis labels from being cut off
        self.pseudosection_plot.getPlotItem().setContentsMargins(10, 10, 10, 10)
        
        # Show top and right axes without labels
        self.pseudosection_plot.showAxis('top')
        self.pseudosection_plot.showAxis('right')
        self.pseudosection_plot.getAxis('top').setStyle(showValues=False)
        self.pseudosection_plot.getAxis('right').setStyle(showValues=False)
        self.pseudosection_plot.getAxis('top').setLabel('')
        self.pseudosection_plot.getAxis('right').setLabel('')
        self.pseudosection_plot.setLabel('left', 'Wavelength', 'm')
        self.pseudosection_plot.setLabel('bottom', 'X (m)', 'm')
        
        # Invert Y axis so wavelength increases downward (depth-like)
        self.pseudosection_plot.getViewBox().invertY(True)
        
        pseudosection_plot_layout.addWidget(self.pseudosection_plot)
        
        # Initialize pseudo-section colorbar (will be added when plotting)
        self.pseudosection_colorbar = None
        
        pseudosection_tab_layout.addWidget(pseudosection_plot_widget)

        # Add tabs in the desired order: Spatial Layout first
        self.data_tabs.addTab(spatial_tab, "Spatial Layout")
        self.data_tabs.addTab(spectrum_tab, "Frequency Spectrum")
        self.data_tabs.addTab(wiggle_tab, "Seismogram")
        self.data_tabs.addTab(pseudosection_tab, "Pseudo-Section")
        
        v_splitter.addWidget(middle_widget)
        
        # Set splitter proportions (dispersion plot takes more space now)
        v_splitter.setSizes([700, 300])  # Dispersion: 70%, Tabs: 30%
        
        return panel
    
    def updateVisualization(self):
        """Update all visualization plots based on current window and subset selection"""
        print("updateVisualization called")
        
        current_window_item = self.window_list.currentItem()
        current_subset_item = self.subset_list.currentItem()
        
        print(f"Current window item: {current_window_item}")
        print(f"Current subset item: {current_subset_item}")
        
        if current_window_item is None or current_subset_item is None:
            print("No current window or subset item selected - populating lists first")
            # Try to populate and select the first available window/subset
            if hasattr(self, 'analysis_results') and self.analysis_results:
                first_window_key = list(self.analysis_results.keys())[0]
                print(f"Using first available window: {first_window_key}")
                self.populateSubsetImageList(first_window_key)
                self.populateStackedResultsList(first_window_key)
            return
            
        # Get the selected window Xmid and subset index
        window_xmid = current_window_item.data(Qt.UserRole)
        subset_index = current_subset_item.data(Qt.UserRole)
        
        print(f"Window Xmid: {window_xmid}, Subset index: {subset_index}")
        
        if window_xmid is None or subset_index is None:
            print("Window Xmid or subset index is None")
            return
            
        # Get the actual subset data from window_subsets
        if window_xmid not in self.window_subsets:
            print(f"Window {window_xmid} not found in window_subsets")
            return
            
        subsets = self.window_subsets[window_xmid]
        if subset_index >= len(subsets):
            print(f"Subset index {subset_index} >= len(subsets) {len(subsets)}")
            return
            
        selected_subset = subsets[subset_index]
        print(f"Selected subset: shot {selected_subset['shot_index']}, {len(selected_subset['traces'])} traces")
        
        # Extract shot indices and trace numbers from subset
        shot_indices = []
        trace_numbers = []
        
        print(f"Extracting shot indices and trace numbers from {len(selected_subset['traces'])} traces")
        for i, trace_info in enumerate(selected_subset['traces']):
            print(f"  Trace {i}: shot_index={trace_info.get('shot_index')}, trace_index={trace_info.get('trace_index')}")
            shot_indices.append(trace_info['shot_index'])
            trace_numbers.append(trace_info['trace_index'])
        
        # Create a result dict for the spatial layout plot
        # Get geophone positions and shot position for this subset
        shot_index = selected_subset['shot_index']
        print(f"Getting shot position for shot_index {shot_index}")
        
        if shot_index >= len(self.shot_positions):
            print(f"ERROR: shot_index {shot_index} >= len(self.shot_positions) {len(self.shot_positions)}")
            return
            
        shot_position = self.shot_positions[shot_index]
        print(f"Shot position: {shot_position}")
        
        # Extract geophone positions from traces
        geophone_x = []
        geophone_y = []
        print(f"Extracting geophone positions...")
        for i, trace_info in enumerate(selected_subset['traces']):
            geophone_x.append(trace_info['position'])
            geophone_y.append(0.0)  # Assume linear array
        
        print(f"Geophone positions: {len(geophone_x)} points from {min(geophone_x):.1f} to {max(geophone_x):.1f}")
        
        result_for_spatial = {
            'receiver_coords_x': np.array(geophone_x),
            'receiver_coords_y': np.array(geophone_y),
            'source_position_x': shot_position,
            'source_position_y': 0.0
        }
        
        # Update spatial plot using the new method
        print(f"Updating spatial plot...")
        try:
            self.plotSpatialLayout(result_for_spatial, window_xmid)
            print(f"Spatial plot updated successfully")
        except Exception as spatial_error:
            print(f"Error updating spatial plot: {spatial_error}")
            import traceback
            traceback.print_exc()
        
        # Update seismogram plot with selected traces
        print(f"Updating seismogram plot with {len(shot_indices)} shot indices and {len(trace_numbers)} trace numbers")
        try:
            self.updateSeismogramPlot(shot_indices, trace_numbers)
            print(f"Seismogram plot updated successfully")
        except Exception as seismo_error:
            print(f"Error updating seismogram plot: {seismo_error}")
            import traceback
            traceback.print_exc()
        
        # Show spectrum when computing window - update spectrum plot
        print(f"Updating spectrum plot...")
        try:
            self.updateSpectrumPlot(shot_indices, trace_numbers)
            print(f"Spectrum plot updated successfully")
        except Exception as spectrum_error:
            print(f"Error updating spectrum plot: {spectrum_error}")
            import traceback
            traceback.print_exc()
        
        # Populate dispersion workflow lists if analysis results are available
        window_key = f'window_{window_xmid:.1f}'
        print(f"Populating subset image list for {window_key}...")
        try:
            self.populateSubsetImageList(window_key)
            print(f"Subset image list populated successfully")
        except Exception as subset_error:
            print(f"Error populating subset image list: {subset_error}")
            import traceback
            traceback.print_exc()
            
        print(f"Populating stacked results list for {window_key}...")
        try:
            self.populateStackedResultsList(window_key)
            print(f"Stacked results list populated successfully")
        except Exception as stacked_error:
            print(f"Error populating stacked results list: {stacked_error}")
            import traceback
            traceback.print_exc()
        
        print(f"updateVisualization completed")
    
    def updateSpatialPlot(self, window_xmid, selected_subset=None):
        """Update spatial plot to show shot positions, current window, and highlight used shots"""
        self.spatial_plot.clear()
        
        if not self.shot_positions:
            return
        
        # Get shots used in current analysis
        used_shot_indices = set()
        if selected_subset is not None:
            used_shot_indices.add(selected_subset.get('shot_index', -1))
        elif window_xmid is not None and window_xmid in self.window_subsets:
            # If no specific subset selected, get all shots for this window
            subsets = self.window_subsets[window_xmid]
            for subset in subsets:
                used_shot_indices.add(subset.get('shot_index', -1))
        
        # Extract shot Y coordinates from first trace of each shot
        shot_y_coordinates = []
        for shot_idx, shot_pos in enumerate(self.shot_positions):
            shot_y = 0  # Default Y coordinate
            if shot_idx < len(self.streams) and len(self.streams[shot_idx]) > 0:
                first_trace = self.streams[shot_idx][0]
                try:
                    # Try to get source coordinates from trace headers
                    if hasattr(first_trace.stats, 'segy') and hasattr(first_trace.stats.segy, 'trace_header'):
                        source_coord_y = first_trace.stats.segy.trace_header.source_coordinate_y
                        scalar = first_trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                    elif hasattr(first_trace.stats, 'su') and hasattr(first_trace.stats.su, 'trace_header'):
                        source_coord_y = first_trace.stats.su.trace_header.source_coordinate_y
                        scalar = first_trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                    else:
                        source_coord_y = 0
                        scalar = 1
                    
                    # Apply coordinate scalar if available
                    if scalar != 0:
                        if scalar < 0:
                            shot_y = source_coord_y / abs(scalar)
                        else:
                            shot_y = source_coord_y * scalar
                    else:
                        shot_y = source_coord_y
                        
                except (AttributeError, KeyError):
                    shot_y = 0  # Fallback
            shot_y_coordinates.append(shot_y)
                
        # Plot shot positions as circles - highlight used shots
        for shot_idx, (shot_pos, shot_y) in enumerate(zip(self.shot_positions, shot_y_coordinates)):
            if shot_idx in used_shot_indices:
                # Highlight used shots in red
                self.spatial_plot.plot([shot_pos], [shot_y], pen=None, symbol='o', 
                                    symbolBrush='red', symbolSize=12, 
                                    symbolPen=pg.mkPen('darkred', width=2),
                                    name=f'Shot {shot_idx+1} (Used)')
            else:
                # Regular shots in blue
                self.spatial_plot.plot([shot_pos], [shot_y], pen=None, symbol='o', 
                                    symbolBrush='lightblue', symbolSize=8, 
                                    name=f'Shot {shot_idx+1}')
        
        # Plot traces for each shot
        for shot_idx, shot_pos in enumerate(self.shot_positions):
            if shot_idx < len(self.streams):
                stream = self.streams[shot_idx]
                trace_x_positions = []
                trace_y_positions = []
                for j, tr in enumerate(stream):
                    # Get trace X and Y positions from group coordinates (receiver position)
                    try:
                        # Try to get group coordinates like in surface_wave_analysis.py
                        if hasattr(tr.stats, 'segy') and hasattr(tr.stats.segy, 'trace_header'):
                            group_coord_x = tr.stats.segy.trace_header.group_coordinate_x
                            group_coord_y = tr.stats.segy.trace_header.group_coordinate_y
                            scalar = tr.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                        elif hasattr(tr.stats, 'su') and hasattr(tr.stats.su, 'trace_header'):
                            group_coord_x = tr.stats.su.trace_header.group_coordinate_x
                            group_coord_y = tr.stats.su.trace_header.group_coordinate_y
                            scalar = tr.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                        else:
                            # Fallback: try using distance but without adding to shot position
                            if hasattr(tr.stats, 'distance'):
                                group_coord_x = tr.stats.distance
                                group_coord_y = 0  # No Y info available
                                scalar = 1
                            else:
                                # Last resort: assume regular spacing from shot
                                group_coord_x = shot_pos + j * 2.0  # 2m spacing as default
                                group_coord_y = shot_y_coordinates[shot_idx]  # Same Y as shot
                                scalar = 1
                        
                        # Apply coordinate scalar if available
                        if scalar != 0:
                            if scalar < 0:
                                trace_x_pos = group_coord_x / abs(scalar)
                                trace_y_pos = group_coord_y / abs(scalar)
                            else:
                                trace_x_pos = group_coord_x * scalar
                                trace_y_pos = group_coord_y * scalar
                        else:
                            trace_x_pos = group_coord_x
                            trace_y_pos = group_coord_y
                            
                    except (AttributeError, KeyError):
                        # Fallback: assume regular spacing from shot
                        trace_x_pos = j * 2.0  # 2m spacing from origin, not from shot
                        trace_y_pos = shot_y_coordinates[shot_idx]  # Same Y as shot
                    
                    trace_x_positions.append(trace_x_pos)
                    trace_y_positions.append(trace_y_pos)
                
                # Color traces differently for used vs unused shots
                if shot_idx in used_shot_indices:
                    self.spatial_plot.plot(trace_x_positions, trace_y_positions, pen=None, 
                                                symbol='s', symbolBrush='orange', 
                                                symbolSize=6, name=f'Shot {shot_idx+1} traces (Used)')
                else:
                    self.spatial_plot.plot(trace_x_positions, trace_y_positions, pen=None, 
                                                symbol='s', symbolBrush='lightgreen', 
                                                symbolSize=4, name=f'Shot {shot_idx+1} traces')
        
        # Highlight current window
        if window_xmid is not None:
            window_size = self.window_size_edit.value()
            window_left = window_xmid - window_size / 2
            window_right = window_xmid + window_size / 2
            
            # Draw window boundaries as vertical lines spanning the Y range
            # Get Y range from all plotted points
            all_y_coords = shot_y_coordinates.copy()
            for shot_idx in range(len(self.streams)):
                if shot_idx < len(self.streams):
                    stream = self.streams[shot_idx]
                    for tr in stream:
                        try:
                            if hasattr(tr.stats, 'segy') and hasattr(tr.stats.segy, 'trace_header'):
                                group_coord_y = tr.stats.segy.trace_header.group_coordinate_y
                                scalar = tr.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                            elif hasattr(tr.stats, 'su') and hasattr(tr.stats.su, 'trace_header'):
                                group_coord_y = tr.stats.su.trace_header.group_coordinate_y
                                scalar = tr.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                            else:
                                group_coord_y = shot_y_coordinates[shot_idx]
                                scalar = 1
                            
                            if scalar != 0:
                                if scalar < 0:
                                    trace_y = group_coord_y / abs(scalar)
                                else:
                                    trace_y = group_coord_y * scalar
                            else:
                                trace_y = group_coord_y
                            all_y_coords.append(trace_y)
                        except (AttributeError, KeyError):
                            all_y_coords.append(shot_y_coordinates[shot_idx])
            
            y_min = min(all_y_coords) if all_y_coords else 0
            y_max = max(all_y_coords) if all_y_coords else 0
            y_range = y_max - y_min
            if y_range == 0:
                y_range = 10  # Default range
                y_min -= 5
                y_max += 5
            else:
                margin = y_range * 0.1
                y_min -= margin
                y_max += margin
            
            # Draw window boundaries as vertical infinite lines
            left_line = pg.InfiniteLine(pos=window_left, angle=90, 
                                       pen=pg.mkPen('red', width=1, style=2))  # Dashed
            right_line = pg.InfiniteLine(pos=window_right, angle=90, 
                                        pen=pg.mkPen('red', width=1, style=2))  # Dashed
            self.spatial_plot.addItem(left_line)
            self.spatial_plot.addItem(right_line)
            
            # Add vertical line at window center
            center_line = pg.InfiniteLine(pos=window_xmid, angle=90, 
                                        pen=pg.mkPen('red', width=2))
            self.spatial_plot.addItem(center_line)
            
            # Add text label for window center position
            window_text = pg.TextItem(f'xmid = {window_xmid:.1f} m', 
                                    color=(255, 0, 0), 
                                    anchor=(0.5, 1.0))  # Center horizontally, bottom of text at position
            window_text.setPos(window_xmid, y_max)
            self.spatial_plot.addItem(window_text)
        
        # Add text labels for shot positions
        for shot_idx, (shot_pos, shot_y) in enumerate(zip(self.shot_positions, shot_y_coordinates)):
            shot_text_color = (255, 0, 0) if shot_idx in used_shot_indices else (0, 0, 255)
            shot_text = pg.TextItem(f'Shot {shot_idx+1}\n{shot_pos:.1f} m', 
                                  color=shot_text_color, 
                                  anchor=(0.5, 0.0))  # Center horizontally, top of text at position
            shot_text.setPos(shot_pos, shot_y + (y_max - y_min) * 0.05)  # Slightly above shot position
            self.spatial_plot.addItem(shot_text)
    
    def updateSeismogramPlot(self, shot_indices, trace_numbers):
        """Update seismogram plot with selected traces from window"""
        self.wiggle_plot.clear()
        
        if not shot_indices or not trace_numbers:
            return
            
        # Collect all traces from the selected shots and trace numbers
        all_traces = []
        all_distances = []
        
        for i, shot_idx in enumerate(shot_indices):
            if shot_idx < len(self.streams):
                stream = self.streams[shot_idx]
                trace_num = trace_numbers[i]
                
                if trace_num < len(stream):
                    trace = stream[trace_num]
                    all_traces.append(trace)
                    
                    # Get trace position from group coordinates (receiver position), not shot + distance
                    shot_pos = self.shot_positions[shot_idx] if shot_idx < len(self.shot_positions) else 0
                    try:
                        # Try to get group coordinates like in surface_wave_analysis.py
                        if hasattr(trace.stats, 'segy') and hasattr(trace.stats.segy, 'trace_header'):
                            group_coord_x = trace.stats.segy.trace_header.group_coordinate_x
                            scalar = trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                        elif hasattr(trace.stats, 'su') and hasattr(trace.stats.su, 'trace_header'):
                            group_coord_x = trace.stats.su.trace_header.group_coordinate_x
                            scalar = trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                        else:
                            # Fallback: try using distance but without adding to shot position
                            if hasattr(trace.stats, 'distance'):
                                group_coord_x = trace.stats.distance
                                scalar = 1
                            else:
                                # Last resort: assume regular spacing from shot
                                group_coord_x = shot_pos + trace_num * 2.0  # 2m spacing as default
                                scalar = 1
                        
                        # Apply coordinate scalar if available
                        if scalar != 0:
                            if scalar < 0:
                                trace_distance = group_coord_x / abs(scalar)
                            else:
                                trace_distance = group_coord_x * scalar
                        else:
                            trace_distance = group_coord_x
                            
                    except (AttributeError, KeyError):
                        # Fallback: assume regular spacing from shot
                        trace_distance = shot_pos + trace_num * 2.0  # 2m spacing as default
                    all_distances.append(trace_distance)
        
        if not all_traces:
            return
            
        # Sort traces by distance
        sorted_pairs = sorted(zip(all_distances, all_traces), key=lambda x: x[0])
        sorted_distances, sorted_traces = zip(*sorted_pairs)
        
        # Plot seismogram data using proper wiggle plotting like surface wave analysis
        # Calculate time_max using data array length instead of npts
        time_max = 0
        for tr in sorted_traces:
            Nt = len(tr.data)
            trace_time_max = Nt * tr.stats.delta
            time_max = max(time_max, trace_time_max)

        min_delta = min(tr.stats.delta for tr in sorted_traces)
        time_array = np.arange(0, time_max, min_delta)
        
        # Calculate trace spacing for proper wiggle display
        if len(sorted_distances) > 1:
            mean_spacing = np.mean(np.diff(sorted(sorted_distances)))
        else:
            mean_spacing = 1.0
        
        if mean_spacing <= 0:
            mean_spacing = 1.0

        # Create data matrix like in surface wave analysis
        XT = []
        plot_positions = []
        for i, (distance, trace) in enumerate(zip(sorted_distances, sorted_traces)):
            # Resample trace to common time grid
            trace_time = np.arange(len(trace.data)) * trace.stats.delta
            resampled_data = np.interp(time_array, trace_time, trace.data)
            XT.append(resampled_data)
            plot_positions.append(distance)
        
        XT = np.array(XT)
        plot_positions = np.array(plot_positions)
        
        # Use the same plotting logic as _plotSeismogramWiggle
        # Get wiggle parameters
        normalize = True  # Default normalization
        gain = 1.0
        clip = True
        fill = 'negative'  # Default fill
        
        # Plot each trace as a wiggle
        for i, trace_data in enumerate(XT):
            if len(trace_data) == 0:
                continue
            
            # Get wiggle info
            x, x_filled, t_interpolated, fillLevel, mask = self.getWiggleInfo(
                trace_data, time_array, plot_positions[i], mean_spacing, 
                normalize, gain, clip, fill
            )
            
            # Plot the original curve
            self.wiggle_plot.plot(x, time_array, pen=pg.mkPen(color='black', width=1))
            
            # Plot the filled part
            if mask is not None and len(t_interpolated) > 0:
                fill_brush = pg.mkBrush(color='black', alpha=100)
                if fill_brush is not None:
                    self.wiggle_plot.plot(x_filled, t_interpolated, pen=None,
                                        fillLevel=fillLevel, brush=fill_brush)
        
        # Set ranges and limits like surface wave analysis
        if len(time_array) > 0:
            self.wiggle_plot.setYRange(time_array[0], time_array[-1])
            self.wiggle_plot.getViewBox().setLimits(yMin=time_array[0], yMax=time_array[-1])
        
        if len(plot_positions) > 0:
            pos_min, pos_max = np.min(plot_positions), np.max(plot_positions)
            pos_range = pos_max - pos_min
            # Use exactly 1 geophone spacing on each side as requested
            margin = mean_spacing
            self.wiggle_plot.setXRange(pos_min - margin, pos_max + margin)
            # Set limits with same margin to prevent excessive zoom-out
            if pos_range > 0:
                self.wiggle_plot.getViewBox().setLimits(
                    xMin=pos_min - margin, xMax=pos_max + margin
                )
            else:
                self.wiggle_plot.getViewBox().setLimits(
                    xMin=pos_min - 10, xMax=pos_max + 10
                )
        
        # Set labels - CORRECTED: Time on Y-axis (left), Distance on X-axis (bottom)
        self.wiggle_plot.setLabel('left', 'Time (s)')
        self.wiggle_plot.setLabel('bottom', 'X (m)')
        
        # Create a result structure so that seismogram controls can work
        # This allows controls to work even before dispersion analysis
        if len(XT) > 0:
            # Calculate sampling interval
            if len(sorted_traces) > 0:
                dt = sorted_traces[0].stats.delta
            else:
                dt = 0.01  # Default fallback
            
            # Create result structure compatible with plotSeismogram/refreshSeismogram
            self.current_result = {
                'data_matrix': XT,  # Shape: (traces, time_samples)
                'receiver_coords_x': plot_positions,
                'distances': plot_positions,  # For compatibility
                'trace_positions': plot_positions,
                'sampling_interval': dt,
                'time': time_array
            }
            
            print(f"Created current_result for seismogram controls with {len(XT)} traces")
    
    def updateSpectrumPlot(self, shot_indices, trace_numbers):
        """Compute and display frequency spectrum from raw trace data"""
        self.spectrum_plot.clear()
        
        if not shot_indices or not trace_numbers:
            return
        
        # Store data for colormap refresh
        self.current_spectrum_data = {
            'shot_indices': shot_indices,
            'trace_numbers': trace_numbers
        }
        
        # Collect traces and positions
        all_traces = []
        geophone_positions = []
        
        for i, shot_idx in enumerate(shot_indices):
            if shot_idx < len(self.streams):
                stream = self.streams[shot_idx]
                trace_num = trace_numbers[i]
                
                if trace_num < len(stream):
                    trace = stream[trace_num]
                    all_traces.append(trace)
                    
                    # Get geophone position
                    try:
                        if hasattr(trace.stats, 'segy') and hasattr(trace.stats.segy, 'trace_header'):
                            group_coord_x = trace.stats.segy.trace_header.group_coordinate_x
                            scalar = trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                        elif hasattr(trace.stats, 'su') and hasattr(trace.stats.su, 'trace_header'):
                            group_coord_x = trace.stats.su.trace_header.group_coordinate_x
                            scalar = trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                        else:
                            group_coord_x = trace.stats.distance if hasattr(trace.stats, 'distance') else trace_num * 2.0
                            scalar = 1
                        
                        if scalar != 0:
                            if scalar < 0:
                                geophone_pos = group_coord_x / abs(scalar)
                            else:
                                geophone_pos = group_coord_x * scalar
                        else:
                            geophone_pos = group_coord_x
                            
                    except (AttributeError, KeyError):
                        geophone_pos = trace_num * 2.0  # Default spacing
                    
                    geophone_positions.append(geophone_pos)
        
        if not all_traces:
            return
        
        # Get current fmax setting or use default
        try:
            fmax = float(self.fmax_edit.text()) if hasattr(self, 'fmax_edit') else 200
        except:
            fmax = 200  # Default fallback
        
        # Compute frequency spectrum for each trace
        dt = all_traces[0].stats.delta
        npts = len(all_traces[0].data)
        
        # Create frequency array
        frequencies = np.fft.fftfreq(npts, dt)
        positive_freq_mask = frequencies > 0
        frequencies = frequencies[positive_freq_mask]
        
        # Apply frequency limit based on fmax setting
        freq_mask = frequencies <= fmax
        frequencies = frequencies[freq_mask]
        
        # Compute FFT for each trace
        spectrum_matrix = []
        for trace in all_traces:
            # Apply window to reduce spectral leakage
            windowed_data = trace.data * np.hanning(len(trace.data))
            
            # Compute FFT
            fft_data = np.fft.fft(windowed_data)
            amplitude_spectrum = np.abs(fft_data[positive_freq_mask])
            
            # Apply frequency limit
            amplitude_spectrum = amplitude_spectrum[freq_mask]
            
            # Convert to dB
            amplitude_spectrum_db = 20 * np.log10(amplitude_spectrum + 1e-10)  # Add small value to avoid log(0)
            spectrum_matrix.append(amplitude_spectrum_db)
        
        spectrum_matrix = np.array(spectrum_matrix)
        geophone_positions = np.array(geophone_positions)
        
        # Sort by geophone position for proper display
        sort_indices = np.argsort(geophone_positions)
        spectrum_matrix = spectrum_matrix[sort_indices]
        geophone_positions = geophone_positions[sort_indices]
        
        # Get current colormap selection
        colormap = self.spectrum_colormap_combo.currentText() if hasattr(self, 'spectrum_colormap_combo') else 'viridis'
        
        # Create and display image
        from .pyqtgraph_utils import createImageItem
        
        # spectrum_matrix has shape (geophones, frequencies)
        # We want frequency on X-axis, geophone position on Y-axis
        img_item = createImageItem(spectrum_matrix, frequencies, geophone_positions, colormap)
        self.spectrum_plot.addItem(img_item)
        
        # Set labels and title
        self.spectrum_plot.setLabel('left', 'X (m)')
        self.spectrum_plot.setLabel('bottom', 'Frequency (Hz)')
        
        # Set frequency range to match fmax setting
        self.spectrum_plot.setXRange(0, fmax, padding=0.05)
        
        # Set proper zoom limits to prevent zooming out beyond data range
        y_min, y_max = geophone_positions.min(), geophone_positions.max()
        y_margin = (y_max - y_min) * 0.1 if y_max > y_min else 10
        self.spectrum_plot.getViewBox().setLimits(
            xMin=0, xMax=fmax * 1.1,
            yMin=y_min - y_margin, yMax=y_max + y_margin
        )
        self.spectrum_plot.setYRange(y_min - y_margin/2, y_max + y_margin/2)
        
        print(f"Computed frequency spectrum: {len(all_traces)} traces, {len(frequencies)} frequencies (0-{fmax} Hz)")
    
    def displaySubsetAnalysisResults(self, window_key, subset_index):
        """Display the analysis results for a specific subset within a window"""
        result = self.analysis_results[window_key]
        subset_dispersions = result.get('subset_dispersions', {})
        
        if not subset_dispersions:
            self.dispersion_plot.setTitle('No dispersion results available')
            return
        
        # Find the subset corresponding to the selected subset_index
        subset_key = f'subset_{subset_index}'
        
        if subset_key not in subset_dispersions:
            self.dispersion_plot.setTitle(f'No results for subset {subset_index}')
            return
        
        subset_data = subset_dispersions[subset_key]
        
        # Extract dispersion data
        frequencies = subset_data['frequencies']
        velocities = subset_data['velocities']
        dispersion_image = subset_data['dispersion_image']
        traces = subset_data['traces']
        distances = subset_data['distances']
        shot_position = subset_data['shot_position']
        shot_offset = subset_data['shot_offset']
        trace_count = subset_data['trace_count']
        ffid = subset_data.get('ffid', f'Shot_{subset_data["shot_index"]+1}')
        
        # Plot dispersion image
        self.dispersion_plot.clear()
        
        # Get current colormap selection
        colormap = self.disp_colormap_combo.currentText() if hasattr(self, 'disp_colormap_combo') else 'gray'
        
        img_item = createImageItem(dispersion_image.T, frequencies, velocities, colormap)
        
        self.dispersion_plot.addItem(img_item)
        self.dispersion_plot.setLabel('bottom', 'Frequency (Hz)')
        self.dispersion_plot.setLabel('left', 'Phase Velocity (m/s)')
        self.dispersion_plot.setTitle(f'Dispersion - {ffid} ({trace_count} traces, offset: {shot_offset:.1f}m)')
        
        # Set proper zoom limits and default view for dispersion plot
        f_min, f_max = frequencies.min(), frequencies.max()
        v_min, v_max = velocities.min(), velocities.max()
        f_margin = (f_max - f_min) * 0.05
        v_margin = (v_max - v_min) * 0.05
        
        # Set view range to show full data
        self.dispersion_plot.setXRange(f_min, f_max, padding=0)
        self.dispersion_plot.setYRange(v_min, v_max, padding=0)
        
        # Set limits to prevent zooming out beyond data range
        self.dispersion_plot.getViewBox().setLimits(
            xMin=f_min - f_margin, xMax=f_max + f_margin,
            yMin=v_min - v_margin, yMax=v_max + v_margin
        )
        
        # Store current dispersion data for picking
        self.current_dispersion_data = {
            'frequencies': frequencies,
            'velocities': velocities,
            'dispersion_image': dispersion_image
        }
        
        # Keep the existing frequency spectrum - don't override it during dispersion display
        # The spectrum should remain stable and show the original frequency content
        pass
        
        # Plot seismogram for this subset
        if traces and distances is not None:
            # Create a result structure similar to what plotSeismogram expects
            data_matrix = []
            sampling_interval = traces[0].stats.delta
            
            # Extract data from traces
            for trace in traces:
                data_matrix.append(trace.data.astype(float))
            
            data_matrix = np.array(data_matrix)
            
            # Create receiver coordinates (assuming X positions from distances)
            receiver_coords_x = np.array(distances)
            receiver_coords_y = np.zeros_like(receiver_coords_x)  # Assume 2D profile
            receiver_coords_z = np.zeros_like(receiver_coords_x)
            
            # Create result structure for plotSeismogram
            seismo_result = {
                'data_matrix': data_matrix,
                'receiver_coords_x': receiver_coords_x,
                'receiver_coords_y': receiver_coords_y, 
                'receiver_coords_z': receiver_coords_z,
                'distances': distances,
                'trace_positions': receiver_coords_x,  # Use X coordinates for trace positioning
                'sampling_interval': sampling_interval,
                'shot_x': shot_position[0] if isinstance(shot_position, (list, tuple, np.ndarray)) and len(shot_position) > 0 else (shot_position if shot_position is not None else 0.0),
                'shot_y': shot_position[1] if isinstance(shot_position, (list, tuple, np.ndarray)) and len(shot_position) > 1 else 0.0,
                'shot_z': shot_position[2] if isinstance(shot_position, (list, tuple, np.ndarray)) and len(shot_position) > 2 else 0.0,
            }
            
            # Plot the seismogram
            self.plotSeismogram(seismo_result)
        
        # Enable picking controls if dispersion data is available
        if hasattr(self, 'picking_button'):
            self.picking_button.setEnabled(True)
            self.removal_button.setEnabled(True)
            self.clear_picking_button.setEnabled(True)
            self.interpolate_button.setEnabled(True)
            self.export_curves_button.setEnabled(True)
        
        # Enable seismogram controls now that seismogram data is available
        self.enableSeismogramControls(True)

    def displayAnalysisResults(self, window_key):
        """Display the analysis results for a window (legacy method for compatibility)"""
        result = self.analysis_results[window_key]
        subset_dispersions = result.get('subset_dispersions', {})
        
        if not subset_dispersions:
            self.dispersion_plot.setTitle('No dispersion results available')
            return
        
        # Check if we have a stacked result to display
        stacked_result = result.get('stacked_dispersion')
        if stacked_result:
            # Display stacked result
            frequencies = stacked_result['frequencies']
            velocities = stacked_result['velocities']
            dispersion_image = stacked_result['dispersion_image']
            num_stacked = stacked_result['num_stacked']
            
            self.plotStackedDispersion(frequencies, velocities, dispersion_image, num_stacked)
            return
        
        # Show first available subset as preview
        if subset_dispersions:
            first_subset_key = list(subset_dispersions.keys())[0]
            first_subset_index = int(first_subset_key.split('_')[1])  # Extract index from 'subset_X'
            self.displaySubsetAnalysisResults(window_key, first_subset_index)
        else:
            self.dispersion_plot.setTitle('No subset results available')
    
    def onParameterChanged(self):
        """Handle real-time parameter changes from inline controls"""
        try:
            # Update parameters silently (don't show error dialogs for partial edits)
            old_fmax = self.current_params.get('fmax', 200)
            old_vmin = self.current_params.get('vmin', 0)
            old_vmax = self.current_params.get('vmax', 1500)
            
            # Try to get new parameter values
            try:
                new_fmax = float(self.fmax_edit.text())
                new_vmin = float(self.vmin_edit.text())
                new_vmax = float(self.vmax_edit.text())
            except:
                return  # Invalid values, ignore
            
            # Update current_params
            self.current_params['fmax'] = new_fmax
            self.current_params['vmin'] = new_vmin
            self.current_params['vmax'] = new_vmax
            self.current_params['normalization'] = self.norm_combo.currentText()
            
            # Update spectrum frequency range if fmax changed
            if old_fmax != new_fmax and hasattr(self, 'spectrum_plot'):
                # Update X-axis range and limits
                self.spectrum_plot.setXRange(0, new_fmax, padding=0.05)
                # Update zoom limits
                view_box = self.spectrum_plot.getViewBox()
                current_limits = view_box.limits
                if current_limits['xLimits']:
                    view_box.setLimits(
                        xMin=0, xMax=new_fmax * 1.1,
                        yMin=current_limits['yLimits'][0], yMax=current_limits['yLimits'][1]
                    )
                
                # Regenerate spectrum data with new frequency limit if we have current data
                if hasattr(self, 'current_spectrum_data') and self.current_spectrum_data:
                    shot_indices = self.current_spectrum_data['shot_indices']
                    trace_numbers = self.current_spectrum_data['trace_numbers']
                    self.updateSpectrumPlot(shot_indices, trace_numbers)
            
            # Update dispersion plot velocity range if velocity parameters changed
            if (old_vmin != new_vmin or old_vmax != new_vmax) and hasattr(self, 'dispersion_plot'):
                # Only update if we have current dispersion data
                if hasattr(self, 'current_dispersion_data') and self.current_dispersion_data:
                    # Get current data ranges
                    frequencies = self.current_dispersion_data['frequencies']
                    f_min, f_max = frequencies.min(), frequencies.max()
                    f_margin = (f_max - f_min) * 0.05
                    
                    # Use parameter ranges with margin for limits
                    v_margin = (new_vmax - new_vmin) * 0.05
                    
                    # Update dispersion plot limits to match new velocity parameters
                    self.dispersion_plot.getViewBox().setLimits(
                        xMin=f_min - f_margin, xMax=f_max + f_margin,
                        yMin=new_vmin - v_margin, yMax=new_vmax + v_margin
                    )
                    
                    # Optionally update the view range if it's outside the new limits
                    current_y_range = self.dispersion_plot.getViewBox().viewRange()[1]
                    if current_y_range[0] < new_vmin or current_y_range[1] > new_vmax:
                        self.dispersion_plot.setYRange(new_vmin, new_vmax, padding=0.05)
                
        except:
            pass  # Ignore errors during real-time updates
    
    def updateParametersFromControls(self):
        """Update current_params from inline control values and refresh spectrum display"""
        try:
            old_fmax = self.current_params.get('fmax', 100)
            
            self.current_params = {
                'vmin': float(self.vmin_edit.text()),
                'vmax': float(self.vmax_edit.text()),
                'dv': float(self.dv_edit.text()),
                'fmin': float(self.fmin_edit.text()),
                'fmax': float(self.fmax_edit.text()),
                'normalization': self.norm_combo.currentText(),
                'include_elevation': self.include_elevation_check.isChecked()
            }
            
            # Update spectrum frequency range if fmax changed
            new_fmax = self.current_params.get('fmax', 200)
            if old_fmax != new_fmax and hasattr(self, 'spectrum_plot'):
                self.spectrum_plot.setXRange(0, new_fmax, padding=0.05)
                    
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Parameters", f"Please check parameter values: {e}")
            return False
        return True
    
    def runAnalysis(self):
        """Run surface wave analysis on all windows, computing individual dispersion for each stream subset"""
        if not self.streams:
            QMessageBox.warning(self, "No Data", "No seismic data available for analysis.")
            return
            
        # Update parameters from inline controls
        if not self.updateParametersFromControls():
            return
            
        # Check if windows have been calculated
        if not hasattr(self, 'window_subsets') or not self.window_subsets:
            print("No windows calculated yet, calculating now...")
            self.calculateWindows()
            
            # Check again after calculation
            if not hasattr(self, 'window_subsets') or not self.window_subsets:
                QMessageBox.warning(self, "No Valid Windows", 
                                  "No valid windows found with current configuration. "
                                  "Please adjust window size, offset range, or side selection and try again.")
                return
        
        # Validate trace count consistency before analysis
        is_valid, validation_message = self.validateTraceCountConsistency()
        if not is_valid:
            reply = QMessageBox.question(self, "Trace Count Issues", 
                                       f"Trace count validation found issues:\n\n{validation_message}\n\n"
                                       f"Do you want to continue with analysis anyway?",
                                       QMessageBox.Yes | QMessageBox.No, 
                                       QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        # Validate shot positioning before analysis
        positioning_valid, positioning_message = self.validateShotPositioning(detailed=False)
        if not positioning_valid:
            # Show detailed breakdown of the issues
            detailed_valid, detailed_message = self.validateShotPositioning(detailed=True)
            
            reply = QMessageBox.question(self, "Shot Positioning Issues", 
                                       f"Shot positioning validation found issues:\n\n{positioning_message}\n\n"
                                       f"DETAILED BREAKDOWN:\n{detailed_message[:1000]}{'...' if len(detailed_message) > 1000 else ''}\n\n"
                                       f"Do you want to continue with analysis anyway?",
                                       QMessageBox.Yes | QMessageBox.No, 
                                       QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        # Disable analysis button during computation
        self.analyze_button.setEnabled(False)
        self.analyze_button.setText("Running...")
        
        # Clear previous results
        self.analysis_results = {}
        
        # Calculate total number of subsets for progress tracking
        total_subsets = sum(len(subsets) for subsets in self.window_subsets.values())
        
        # Show progress dialog
        progress = QProgressDialog("Running surface wave analysis for each stream subset...", "Cancel", 
                                 0, total_subsets, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        current_subset_idx = 0
        
        try:
            # Process each window
            for xmid, subsets in self.window_subsets.items():
                if progress.wasCanceled():
                    break
                
                window_key = f'window_{xmid:.1f}'
                subset_dispersions = {}
                
                # Process each subset (shot) in this window
                for subset_idx, subset in enumerate(subsets):
                    if progress.wasCanceled():
                        break
                        
                    current_subset_idx += 1
                    progress.setValue(current_subset_idx)
                    
                    shot_idx = subset['shot_index']
                    shot_pos = subset['shot_position']
                    shot_offset = subset['shot_offset']
                    
                    progress.setLabelText(f"Analyzing Xmid {xmid:.1f}m, Shot {shot_idx+1} (offset: {shot_offset:.1f}m)...")
                    QApplication.processEvents()
                    
                    print(f"Processing subset {subset_idx} of window {xmid:.1f}m:")
                    print(f"  - Shot index: {shot_idx}")
                    print(f"  - Shot position: {shot_pos:.1f}m")
                    print(f"  - Shot offset: {shot_offset:.1f}m")
                    print(f"  - Number of traces in subset: {len(subset['traces'])}")
                    
                    try:
                        # Extract traces for this subset
                        shot_traces = []
                        shot_positions = []  # Store receiver positions for sorting
                        
                        if shot_idx >= len(self.streams):
                            print(f"Warning: shot_idx {shot_idx} >= len(self.streams) {len(self.streams)}")
                            continue
                        
                        # Get shot position
                        shot_pos = self.shot_positions[shot_idx]
                        print(f"  - Shot position: {shot_pos:.1f}m")
                        print(f"  - Available traces in shot {shot_idx+1}: {len(self.streams[shot_idx])}")
                        
                        for trace_info in subset['traces']:
                            trace_num = trace_info['trace_index']
                            
                            if trace_num < len(self.streams[shot_idx]):
                                trace = self.streams[shot_idx][trace_num]
                                shot_traces.append(trace)
                                # Store receiver position (not distance) for proper spatial sorting
                                shot_positions.append(trace_info['position'])
                        
                        print(f"  - Extracted {len(shot_traces)} traces for analysis")
                        print(f"  - Receiver positions: {[f'{p:.1f}' for p in shot_positions]}")
                        
                        if len(shot_traces) >= 2:
                            # Sort by receiver position (spatial order) for proper analysis
                            sorted_pairs = sorted(zip(shot_positions, shot_traces), key=lambda x: x[0])
                            sorted_positions, sorted_traces = zip(*sorted_pairs)
                            
                            # Calculate distances from shot for phase shift after sorting
                            sorted_distances = [abs(pos - shot_pos) for pos in sorted_positions]
                            
                            print(f"  - Sorted receiver positions: {[f'{p:.1f}' for p in sorted_positions]}")
                            print(f"  - Corresponding distances: {[f'{d:.1f}' for d in sorted_distances]}")
                            
                            # Compute dispersion for this subset
                            from .sw_utils import phase_shift
                            
                            trace_matrix = np.array([tr.data for tr in sorted_traces])
                            distance_array = np.array(sorted_distances)
                            dt = sorted_traces[0].stats.delta
                            
                            # Get velocity parameters and handle vmin=0 case
                            vmin = self.current_params.get('vmin', 0)
                            vmax = self.current_params.get('vmax', 1500)
                            dv = self.current_params.get('dv', 10)
                            
                            # If vmin is 0, use dv as minimum to avoid numerical issues
                            if vmin == 0:
                                vmin = dv
                                print(f"  - Warning: vmin was 0, using dv={dv} as minimum velocity to avoid numerical issues")
                            
                            frequencies, velocities, dispersion_image = phase_shift(
                                trace_matrix, dt, distance_array,
                                vmin, vmax, dv,
                                self.current_params.get('fmax', 200),
                                self.current_params.get('fmin', 0)
                            )
                            
                            print(f"  - Dispersion computed successfully using spatial ordering!")
                            print(f"  - Frequencies shape: {frequencies.shape}, range: {frequencies.min():.1f} to {frequencies.max():.1f} Hz")
                            print(f"  - Velocities shape: {velocities.shape}, range: {velocities.min():.1f} to {velocities.max():.1f} m/s")
                            print(f"  - Dispersion image shape: {dispersion_image.shape}")
                            
                            # Store individual subset result
                            subset_key = f'subset_{subset_idx}'
                            subset_dispersions[subset_key] = {
                                'shot_index': shot_idx,
                                'subset_index': subset_idx,
                                'frequencies': frequencies,
                                'velocities': velocities,
                                'dispersion_image': dispersion_image,
                                'traces': sorted_traces,
                                'distances': sorted_distances,  # Absolute distances from shot for phase shift
                                'shot_position': shot_pos,
                                'shot_offset': shot_offset,   # Distance from shot to window edge (for windowing logic)
                                'trace_count': len(sorted_traces),
                                'selected': True,  # Default to selected for stacking
                                'ffid': subset['traces'][0]['ffid'] if subset['traces'] else f'Shot_{shot_idx+1}'
                            }
                            
                            print(f"  - Subset result stored as '{subset_key}'")
                            
                        else:
                            print(f"Warning: Only {len(shot_traces)} traces found for subset {subset_idx} of window {xmid:.1f}m (Shot {shot_idx+1}). Skipping - need at least 2 traces.")
                            continue
                            
                    except Exception as e:
                        print(f"Error processing subset {subset_idx} of window {xmid:.1f}m (Shot {shot_idx+1}): {e}")
                        import traceback
                        traceback.print_exc()
                        continue
                
                # Store window results if we have valid subset dispersions
                if subset_dispersions:
                    print(f"Window {xmid:.1f}m completed with {len(subset_dispersions)} valid dispersions")
                    
                    # Get representative frequency and velocity arrays (should be the same for all subsets)
                    first_subset = next(iter(subset_dispersions.values()))
                    
                    self.analysis_results[window_key] = {
                        'xmid': xmid,
                        'subset_dispersions': subset_dispersions,
                        'frequencies': first_subset['frequencies'],
                        'velocities': first_subset['velocities'],
                        'subset_count': len(subset_dispersions),
                        'window_size': self.actual_window_size,
                        'trace_count_per_subset': self.window_num_traces
                    }
                    
                    print(f"Window {xmid:.1f}m results stored in analysis_results['{window_key}']")
                else:
                    print(f"Window {xmid:.1f}m: No valid dispersions computed")
            
            progress.setValue(total_subsets)
            progress.close()
            
            print(f"\nAnalysis completed:")
            print(f"- Total windows processed: {len(self.window_subsets)}")
            print(f"- Windows with valid results: {len(self.analysis_results)}")
            print(f"- Analysis results keys: {list(self.analysis_results.keys())}")
            
            # Show completion message
            num_windows = len(self.analysis_results)
            total_analyzed_subsets = sum(result['subset_count'] for result in self.analysis_results.values())
            
            print(f"Showing completion message...")
            QMessageBox.information(self, "Analysis Complete", 
                                  f"Surface wave analysis completed:\n"
                                  f"• {num_windows} windows analyzed\n"
                                  f"• {total_analyzed_subsets} individual stream subsets processed\n"
                                  f"• {self.window_num_traces} traces per subset\n"
                                  f"• Auto-stacked dispersion images for all windows")
            
            # Update visualization and shot list
            print(f"Updating visualization...")
            try:
                self.updateVisualization()
                print(f"Visualization updated successfully")
            except Exception as viz_error:
                print(f"Error during visualization update: {viz_error}")
                import traceback
                traceback.print_exc()
                raise viz_error
            
            # Automatically stack all available images for each window
            print("Starting automatic stacking for all windows...")
            self.autoStackAllWindows()
            print("Automatic stacking completed")
            
        except Exception as e:
            print(f"Exception caught in runAnalysis: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Analysis Error", f"Error during analysis:\n{e}")
        finally:
            print(f"Cleaning up...")
            progress.close()
            self.resetAnalysisButton()

    def autoStackAllWindows(self):
        """Automatically stack all available dispersion images for each analyzed window"""
        if not hasattr(self, 'analysis_results') or not self.analysis_results:
            print("No analysis results available for auto-stacking")
            return
        
        print(f"Auto-stacking {len(self.analysis_results)} windows...")
        
        for window_key, window_result in self.analysis_results.items():
            try:
                subset_dispersions = window_result.get('subset_dispersions', {})
                if not subset_dispersions:
                    print(f"  - Skipping {window_key}: no subset dispersions")
                    continue
                
                xmid = window_result['xmid']
                print(f"  - Auto-stacking {window_key} with {len(subset_dispersions)} images...")
                
                # Get all dispersion images and select all by default
                images_to_stack = []
                for subset_key, subset_data in subset_dispersions.items():
                    images_to_stack.append({
                        'key': subset_key,
                        'data': subset_data,
                        'selected': True  # Auto-select all for stacking
                    })
                
                if len(images_to_stack) == 0:
                    print(f"    - No valid images to stack for {window_key}")
                    continue
                
                # Use the stacking logic to create stacked result
                selected_data = [img['data'] for img in images_to_stack if img['selected']]
                
                if len(selected_data) == 0:
                    print(f"    - No selected images for {window_key}")
                    continue
                
                # Get representative arrays from first dataset
                first_data = selected_data[0]
                frequencies = first_data['frequencies']
                velocities = first_data['velocities']
                
                # Stack all selected images
                stacked_images = []
                for data in selected_data:
                    stacked_images.append(data['dispersion_image'])
                
                # Compute average (could be other stacking methods in the future)
                stacked_image = np.mean(stacked_images, axis=0)
                
                # Store stacked result (replace any existing stacked result)
                if not hasattr(self, 'stacked_results'):
                    self.stacked_results = {}
                
                # Generate stack ID for auto-stacking
                import time
                stack_id = f"auto_{int(time.time() * 1000) % 100000}"  # Auto-generated ID
                
                self.stacked_results[window_key] = {
                    'xmid': xmid,
                    'dispersion_image': stacked_image,  # Changed from 'stacked_image' to match expected key
                    'frequencies': frequencies,
                    'velocities': velocities,
                    'num_stacked': len(selected_data),  # Changed from num_images to num_stacked
                    'selected_subsets': [img['key'] for img in images_to_stack if img['selected']],  # Changed from subset_keys
                    'auto_generated': True,
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'stack_id': stack_id
                }
                
                print(f"    - Auto-stacked {len(selected_data)} images for {window_key}")
                
            except Exception as e:
                print(f"  - Error auto-stacking {window_key}: {e}")
                import traceback
                traceback.print_exc()
        
        # Update the stacked results list display
        current_item = self.window_list.currentItem()
        if current_item:
            xmid = current_item.data(Qt.UserRole)
            window_key = f'window_{xmid:.1f}'
            self.populateStackedResultsList(window_key)
            
            # Auto-display the stacked dispersion image for the current window
            if window_key in self.stacked_results:
                stacked_data = self.stacked_results[window_key]
                self.plotStackedDispersion(
                    stacked_data['frequencies'],
                    stacked_data['velocities'], 
                    stacked_data['dispersion_image'],
                    stacked_data['num_stacked']
                )
                print(f"Auto-displayed stacked dispersion for {window_key}")
        
        print(f"Auto-stacking completed. Total stacked windows: {len(self.stacked_results) if hasattr(self, 'stacked_results') else 0}")
    
    def validateWindowSubsetLogic(self):
        """Cross-validate that the findWindowSubsets logic is correctly implemented"""
        if not hasattr(self, 'window_subsets') or not self.window_subsets:
            return True, "No window subsets to validate"
        
        # Get current configuration
        min_shot_offset = self.min_shot_offset_edit.value()
        max_shot_offset = self.max_shot_offset_edit.value()
        selected_side = self.side_combo.currentText()
        
        logic_issues = []
        
        for xmid, subsets in self.window_subsets.items():
            window_half_size = self.actual_window_size / 2
            window_start = xmid - window_half_size
            window_end = xmid + window_half_size
            tolerance = 1e-6
            
            # For each subset, verify it should actually be included
            for subset_idx, subset in enumerate(subsets):
                shot_idx = subset['shot_index']
                shot_pos = subset['shot_position']
                stored_offset = subset['shot_offset']
                
                # Recalculate offset using same logic as findWindowSubsets
                if shot_pos < (window_start - tolerance):
                    # Shot is to the left of window
                    calculated_offset = window_start - shot_pos
                    calculated_side = 'left'
                    is_outside = True
                elif shot_pos > (window_end + tolerance):
                    # Shot is to the right of window  
                    calculated_offset = shot_pos - window_end
                    calculated_side = 'right'
                    is_outside = True
                else:
                    # Shot is at window edge or inside the window
                    left_distance = abs(shot_pos - window_start)
                    right_distance = abs(shot_pos - window_end)
                    
                    if left_distance <= tolerance:
                        calculated_offset = 0.0
                        calculated_side = 'left_edge'
                        is_outside = True
                    elif right_distance <= tolerance:
                        calculated_offset = 0.0
                        calculated_side = 'right_edge'
                        is_outside = True
                    else:
                        calculated_offset = -1.0
                        calculated_side = 'inside'
                        is_outside = False
                
                # Check if this subset should have been included
                should_include = True
                exclusion_reasons = []
                
                # 1. Must be outside window
                if not is_outside:
                    should_include = False
                    exclusion_reasons.append("shot inside window")
                
                # 2. Must meet side constraint
                if selected_side == 'left' and shot_pos >= xmid:
                    should_include = False
                    exclusion_reasons.append(f"shot on right side but '{selected_side}' selected")
                elif selected_side == 'right' and shot_pos <= xmid:
                    should_include = False
                    exclusion_reasons.append(f"shot on left side but '{selected_side}' selected")
                
                # 3. Must meet offset constraints
                if is_outside and (calculated_offset < min_shot_offset or calculated_offset > max_shot_offset):
                    should_include = False
                    exclusion_reasons.append(f"offset {calculated_offset:.1f}m outside range [{min_shot_offset:.1f}, {max_shot_offset:.1f}]")
                
                # 4. Check offset calculation consistency
                if abs(calculated_offset - stored_offset) > 1e-6:
                    logic_issues.append(f"Window {xmid:.1f}m, Shot {shot_idx+1}: offset mismatch (calculated={calculated_offset:.1f}m, stored={stored_offset:.1f}m)")
                
                # 5. If subset exists but shouldn't be included
                if not should_include:
                    logic_issues.append(f"Window {xmid:.1f}m, Shot {shot_idx+1}: should be excluded ({', '.join(exclusion_reasons)})")
        
        # Also check if shots that should be included are missing
        missing_shots = []
        for xmid in self.available_windows:
            window_half_size = self.actual_window_size / 2
            window_start = xmid - window_half_size
            window_end = xmid + window_half_size
            tolerance = 1e-6
            
            included_shots = set()
            if xmid in self.window_subsets:
                included_shots = {subset['shot_index'] for subset in self.window_subsets[xmid]}
            
            for shot_idx, shot_pos in enumerate(self.shot_positions):
                # Calculate if this shot should be included
                if shot_pos < (window_start - tolerance):
                    calculated_offset = window_start - shot_pos
                    is_outside = True
                elif shot_pos > (window_end + tolerance):
                    calculated_offset = shot_pos - window_end
                    is_outside = True
                else:
                    left_distance = abs(shot_pos - window_start)
                    right_distance = abs(shot_pos - window_end)
                    if left_distance <= tolerance or right_distance <= tolerance:
                        calculated_offset = 0.0
                        is_outside = True
                    else:
                        is_outside = False
                        calculated_offset = -1.0
                
                should_include = True
                
                if not is_outside:
                    should_include = False
                elif selected_side == 'left' and shot_pos >= xmid:
                    should_include = False
                elif selected_side == 'right' and shot_pos <= xmid:
                    should_include = False
                elif is_outside and (calculated_offset < min_shot_offset or calculated_offset > max_shot_offset):
                    should_include = False
                
                # Check if shot should be included but is missing
                if should_include and shot_idx not in included_shots:
                    # Also check if there are enough traces for this shot
                    if shot_idx < len(self.streams) and len(self.streams[shot_idx]) >= self.window_num_traces:
                        missing_shots.append(f"Window {xmid:.1f}m, Shot {shot_idx+1}: should be included (offset={calculated_offset:.1f}m)")
        
        all_issues = logic_issues + missing_shots
        
        if all_issues:
            issue_summary = f"{len(all_issues)} logic validation issues found"
            return False, issue_summary + ":\n" + "\n".join(all_issues[:15]) + ("\n..." if len(all_issues) > 15 else "")
        else:
            return True, "Window subset logic validation passed"

    def validateShotPositioning(self, detailed=False):
        """Validate shot positioning criteria for all windows"""
        if not hasattr(self, 'window_subsets') or not self.window_subsets:
            return True, "No window subsets to validate"
        
        # Get current configuration
        min_shot_offset = self.min_shot_offset_edit.value()
        max_shot_offset = self.max_shot_offset_edit.value()
        selected_side = self.side_combo.currentText()
        
        positioning_issues = []
        total_shots_tested = 0
        valid_shots = 0
        
        for xmid, subsets in self.window_subsets.items():
            window_half_size = self.actual_window_size / 2
            window_start = xmid - window_half_size
            window_end = xmid + window_half_size
            tolerance = 1e-6
            
            if detailed:
                positioning_issues.append(f"\nWindow Xmid = {xmid:.1f}m ({window_start:.1f}m to {window_end:.1f}m):")
            
            # Test all shots, not just the ones in subsets
            for shot_idx, shot_pos in enumerate(self.shot_positions):
                total_shots_tested += 1
                
                # Calculate shot offset from window edges
                if shot_pos < (window_start - tolerance):
                    # Shot is to the left of window
                    shot_offset = window_start - shot_pos
                    shot_side = 'left'
                    is_outside = True
                elif shot_pos > (window_end + tolerance):
                    # Shot is to the right of window  
                    shot_offset = shot_pos - window_end
                    shot_side = 'right'
                    is_outside = True
                else:
                    # Shot is at window edge or inside the window
                    left_distance = abs(shot_pos - window_start)
                    right_distance = abs(shot_pos - window_end)
                    
                    if left_distance <= tolerance:
                        shot_offset = 0.0
                        shot_side = 'left_edge'
                        is_outside = True
                    elif right_distance <= tolerance:
                        shot_offset = 0.0
                        shot_side = 'right_edge'
                        is_outside = True
                    else:
                        # Shot is truly inside the window
                        shot_offset = -1.0
                        shot_side = 'inside'
                        is_outside = False
                
                # Check all positioning criteria
                criteria_met = True
                reasons = []
                
                # 1. Check if shot is outside window
                if not is_outside:
                    criteria_met = False
                    reasons.append("inside window")
                
                # 2. Check side constraint
                if selected_side == 'left' and shot_pos >= xmid:
                    criteria_met = False
                    reasons.append(f"on right side (selected: {selected_side})")
                elif selected_side == 'right' and shot_pos <= xmid:
                    criteria_met = False
                    reasons.append(f"on left side (selected: {selected_side})")
                
                # 3. Check offset range
                if is_outside and (shot_offset < min_shot_offset or shot_offset > max_shot_offset):
                    criteria_met = False
                    reasons.append(f"offset {shot_offset:.1f}m outside range [{min_shot_offset:.1f}, {max_shot_offset:.1f}]")
                
                # Track results
                if criteria_met:
                    valid_shots += 1
                    if detailed:
                        positioning_issues.append(f"  ✓ Shot {shot_idx+1} ({shot_pos:.1f}m): {shot_side}, offset={shot_offset:.1f}m")
                else:
                    if detailed:
                        positioning_issues.append(f"  ✗ Shot {shot_idx+1} ({shot_pos:.1f}m): {', '.join(reasons)}")
                    else:
                        positioning_issues.append(f"Window {xmid:.1f}m, Shot {shot_idx+1}: {', '.join(reasons)}")
        
        if positioning_issues and not detailed:
            issue_summary = f"{len(positioning_issues)} positioning issues found"
            return False, issue_summary + ":\n" + "\n".join(positioning_issues[:10]) + ("\n..." if len(positioning_issues) > 10 else "")
        elif detailed:
            summary = f"\nSummary: {valid_shots}/{total_shots_tested} shot-window combinations meet positioning criteria"
            return len(positioning_issues) == 0, "\n".join(positioning_issues) + summary
        else:
            return True, f"All {total_shots_tested} shot-window combinations meet positioning criteria"

    def validateTraceCountConsistency(self):
        """Validate that all subsets have consistent trace counts"""
        if not hasattr(self, 'window_subsets') or not self.window_subsets:
            return True, "No window subsets to validate"
        
        if not hasattr(self, 'window_num_traces') or self.window_num_traces is None:
            return True, "No target trace count defined"
        
        issues = []
        total_subsets = 0
        valid_subsets = 0
        
        for xmid, subsets in self.window_subsets.items():
            for subset_idx, subset in enumerate(subsets):
                total_subsets += 1
                trace_count = len(subset['traces'])
                shot_idx = subset['shot_index']
                
                if trace_count < 2:
                    issues.append(f"Window {xmid:.1f}m, Shot {shot_idx+1}: insufficient traces ({trace_count})")
                elif trace_count != self.window_num_traces:
                    issues.append(f"Window {xmid:.1f}m, Shot {shot_idx+1}: unexpected trace count ({trace_count}, expected {self.window_num_traces})")
                else:
                    valid_subsets += 1
        
        if issues:
            issue_summary = f"{len(issues)} trace count issues found out of {total_subsets} subsets"
            return False, issue_summary + ":\n" + "\n".join(issues[:5]) + ("\n..." if len(issues) > 5 else "")
        else:
            return True, f"All {total_subsets} subsets have correct trace count ({self.window_num_traces})"

    def diagnoseProfiling(self):
        """Comprehensive diagnostic for surface wave profiling setup"""
        if not self.streams or not self.shot_positions:
            QMessageBox.warning(self, "No Data", "No seismic data loaded for diagnosis.")
            return
        
        # Calculate windows if not done yet
        if not hasattr(self, 'window_subsets') or not self.window_subsets:
            self.calculateWindows()
        
        # Collect diagnostic information
        diagnostics = []
        diagnostics.append("=== SURFACE WAVE PROFILING DIAGNOSTICS ===\n")
        
        # Basic data info
        diagnostics.append(f"Total shots loaded: {len(self.streams)}")
        total_traces = sum(len(stream) for stream in self.streams)
        diagnostics.append(f"Total traces: {total_traces}")
        
        # Window configuration
        diagnostics.append(f"\nWindow Configuration:")
        diagnostics.append(f"- Requested window size: {self.window_size:.1f}m")
        diagnostics.append(f"- Window step: {self.window_step:.1f}m")
        diagnostics.append(f"- Shot offset range: {self.min_shot_offset_edit.value():.1f}m - {self.max_shot_offset_edit.value():.1f}m")
        diagnostics.append(f"- Selected side: {self.side_combo.currentText()}")
        
        if hasattr(self, 'actual_window_size') and self.actual_window_size:
            diagnostics.append(f"- Actual window size: {self.actual_window_size:.1f}m")
            diagnostics.append(f"- Target traces per subset: {self.window_num_traces}")
        
        # Window analysis
        diagnostics.append(f"\nWindow Analysis:")
        diagnostics.append(f"- Available windows (Xmids): {len(self.available_windows)}")
        
        if not self.window_subsets:
            diagnostics.append("⚠️  No valid windows found! Check your configuration.")
        else:
            # Analyze each window
            total_subsets = 0
            trace_count_issues = []
            
            for xmid, subsets in self.window_subsets.items():
                total_subsets += len(subsets)
                diagnostics.append(f"\nWindow Xmid = {xmid:.1f}m:")
                diagnostics.append(f"  - Available subsets: {len(subsets)}")
                
                for subset_idx, subset in enumerate(subsets):
                    shot_idx = subset['shot_index']
                    trace_count = len(subset['traces'])
                    shot_pos = subset['shot_position']
                    shot_offset = subset['shot_offset']
                    
                    status = "✓" if trace_count >= 2 else "⚠️"
                    diagnostics.append(f"  - Subset {subset_idx}: Shot {shot_idx+1} ({shot_pos:.1f}m, offset={shot_offset:.1f}m) → {trace_count} traces {status}")
                    
                    # Check for insufficient traces
                    if trace_count < 2:
                        trace_count_issues.append(f"Window {xmid:.1f}m, Shot {shot_idx+1}: only {trace_count} traces")
                    elif hasattr(self, 'window_num_traces') and trace_count != self.window_num_traces:
                        trace_count_issues.append(f"Window {xmid:.1f}m, Shot {shot_idx+1}: {trace_count} traces (expected {self.window_num_traces})")
            
            diagnostics.append(f"\nSummary:")
            diagnostics.append(f"- Total subsets across all windows: {total_subsets}")
            
            if trace_count_issues:
                diagnostics.append(f"\n⚠️  TRACE COUNT ISSUES ({len(trace_count_issues)} found):")
                for issue in trace_count_issues[:10]:  # Show first 10 issues
                    diagnostics.append(f"  - {issue}")
                if len(trace_count_issues) > 10:
                    diagnostics.append(f"  - ... and {len(trace_count_issues) - 10} more issues")
            else:
                diagnostics.append("✓ All subsets have appropriate trace counts")
        
        # Shot positioning validation
        diagnostics.append(f"\nShot Positioning Validation:")
        diagnostics.append(f"- Side selection: {self.side_combo.currentText()}")
        diagnostics.append(f"- Offset range: {self.min_shot_offset_edit.value():.1f}m - {self.max_shot_offset_edit.value():.1f}m")
        
        positioning_valid, positioning_details = self.validateShotPositioning(detailed=True)
        diagnostics.append(positioning_details)
        
        # Window subset logic validation
        diagnostics.append(f"\nWindow Subset Logic Validation:")
        logic_valid, logic_details = self.validateWindowSubsetLogic()
        diagnostics.append(logic_details)
        
        # Shot position analysis
        diagnostics.append(f"\nShot Position Analysis:")
        if self.shot_positions:
            min_shot = min(self.shot_positions)
            max_shot = max(self.shot_positions)
            shot_extent = max_shot - min_shot
            diagnostics.append(f"- Shot positions range: {min_shot:.1f}m to {max_shot:.1f}m")
            diagnostics.append(f"- Shot survey extent: {shot_extent:.1f}m")
            
            # Analyze shot spacing
            shot_spacings = []
            for i in range(len(self.shot_positions) - 1):
                spacing = abs(self.shot_positions[i+1] - self.shot_positions[i])
                shot_spacings.append(spacing)
            
            if shot_spacings:
                avg_shot_spacing = sum(shot_spacings) / len(shot_spacings)
                min_shot_spacing = min(shot_spacings)
                max_shot_spacing = max(shot_spacings)
                diagnostics.append(f"- Shot spacing: avg={avg_shot_spacing:.1f}m, min={min_shot_spacing:.1f}m, max={max_shot_spacing:.1f}m")
        
        # Trace position analysis for first few shots
        diagnostics.append(f"\nTrace Position Analysis (first 3 shots):")
        for shot_idx in range(min(3, len(self.streams))):
            stream = self.streams[shot_idx]
            shot_pos = self.shot_positions[shot_idx]
            diagnostics.append(f"  Shot {shot_idx+1} ({shot_pos:.1f}m): {len(stream)} traces")
            
            if len(stream) > 0:
                trace_positions = []
                for trace_idx, trace in enumerate(stream):
                    try:
                        # Get trace position
                        if hasattr(trace.stats, 'segy') and hasattr(trace.stats.segy, 'trace_header'):
                            group_coord_x = trace.stats.segy.trace_header.group_coordinate_x
                            scalar = trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                        elif hasattr(trace.stats, 'su') and hasattr(trace.stats.su, 'trace_header'):
                            group_coord_x = trace.stats.su.trace_header.group_coordinate_x
                            scalar = trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                        else:
                            group_coord_x = shot_pos + trace_idx * 2.0  # Fallback
                            scalar = 1
                        
                        if scalar != 0:
                            if scalar < 0:
                                trace_pos = group_coord_x / abs(scalar)
                            else:
                                trace_pos = group_coord_x * scalar
                        else:
                            trace_pos = group_coord_x
                        
                        trace_positions.append(trace_pos)
                    except Exception:
                        trace_positions.append(shot_pos + trace_idx * 2.0)  # Fallback
                
                if len(trace_positions) >= 2:
                    trace_extent = max(trace_positions) - min(trace_positions)
                    trace_spacings = [trace_positions[i+1] - trace_positions[i] for i in range(len(trace_positions)-1)]
                    avg_trace_spacing = sum(abs(s) for s in trace_spacings) / len(trace_spacings) if trace_spacings else 0
                    diagnostics.append(f"    - Trace extent: {trace_extent:.1f}m, avg spacing: {avg_trace_spacing:.1f}m")
                    diagnostics.append(f"    - Trace positions: {min(trace_positions):.1f}m to {max(trace_positions):.1f}m")
        
        # Show diagnostics in a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Surface Wave Profiling Diagnostics")
        dialog.setModal(True)
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setFont(QFont("Courier", 9))  # Monospace font
        text_edit.setPlainText('\n'.join(diagnostics))
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        button_layout = QHBoxLayout()
        
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText('\n'.join(diagnostics)))
        button_layout.addWidget(copy_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()

    def resetAnalysisButton(self):
        """Reset the analysis button to its normal state"""
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("Run Analysis")
    
    def populateSubsetImageList(self, window_key):
        """Populate subset image list for the current window"""
        self.subset_image_list.clear()
        
        if window_key not in self.analysis_results:
            self.subset_image_list.setEnabled(False)
            self.select_all_subsets_button.setEnabled(False)
            self.select_none_subsets_button.setEnabled(False)
            self.stack_subsets_button.setEnabled(False)
            self.preview_subset_button.setEnabled(False)
            self.subset_info_text.clear()
            return
        
        result = self.analysis_results[window_key]
        subset_dispersions = result.get('subset_dispersions', {})
        
        if not subset_dispersions:
            self.subset_image_list.setEnabled(False)
            self.select_all_subsets_button.setEnabled(False)
            self.select_none_subsets_button.setEnabled(False)
            self.stack_subsets_button.setEnabled(False)
            self.preview_subset_button.setEnabled(False)
            self.subset_info_text.clear()
            return
        
        # Enable controls
        self.subset_image_list.setEnabled(True)
        self.select_all_subsets_button.setEnabled(True)
        self.select_none_subsets_button.setEnabled(True)
        self.stack_subsets_button.setEnabled(True)
        self.preview_subset_button.setEnabled(True)
        
        # Populate list with subsets
        for subset_key, subset_data in subset_dispersions.items():
            shot_idx = subset_data['shot_index']
            subset_idx = subset_data['subset_index']
            shot_pos = subset_data['shot_position']
            shot_offset = subset_data['shot_offset']
            trace_count = subset_data['trace_count']
            ffid = subset_data.get('ffid', f'Shot_{shot_idx+1}')
            
            item_text = f"{ffid} (subset {subset_idx}): pos={shot_pos:.1f}m, offset={shot_offset:.1f}m, {trace_count} traces"
            item = QListWidgetItem(item_text)
            item.setCheckState(Qt.Checked if subset_data.get('selected', False) else Qt.Unchecked)
            item.setData(Qt.UserRole, subset_key)  # Store subset_key
            self.subset_image_list.addItem(item)
        
        # Update info display
        self.updateSubsetImageInfo(subset_dispersions)
    
    def populateStackedResultsList(self, window_key):
        """Populate stacked results list for the current window"""
        self.stacked_results_list.clear()
        
        if window_key not in self.stacked_results:
            self.show_stacked_button.setEnabled(False)
            self.delete_stacked_button.setEnabled(False)
            return
        
        stacked_data = self.stacked_results[window_key]
        
        # Enable controls if we have stacked results
        if stacked_data:
            self.show_stacked_button.setEnabled(True)
            self.delete_stacked_button.setEnabled(True)
            
            # Add single stacked result to list
            num_stacked = stacked_data['num_stacked']
            timestamp = stacked_data.get('timestamp', 'Unknown')
            selected_subsets = stacked_data.get('selected_subsets', [])
            stack_id = stacked_data.get('stack_id', 'Unknown')
            auto_generated = stacked_data.get('auto_generated', False)
            
            # Add indicator for auto vs manual stacking
            stack_type = " [AUTO]" if auto_generated else " [MANUAL]"
            item_text = f"Stacked: {num_stacked} images{stack_type} ({timestamp})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, stack_id)
            item.setToolTip(f"Stacked subsets: {', '.join(selected_subsets)}\nType: {'Auto-generated' if auto_generated else 'Manual selection'}")
            self.stacked_results_list.addItem(item)
            
            # Auto-select the single item
            self.stacked_results_list.setCurrentItem(item)
    
    def updateSubsetImageInfo(self, subset_dispersions):
        """Update subset image information display"""
        total_subsets = len(subset_dispersions)
        selected_subsets = sum(1 for data in subset_dispersions.values() if data.get('selected', False))
        
        info_text = f"Total subsets: {total_subsets}, Selected: {selected_subsets}"
        if selected_subsets > 0:
            info_text += f"\nReady to stack {selected_subsets} images"
        
        self.subset_info_text.setText(info_text)
    
    def onSubsetImageSelectionChanged(self, item):
        """Handle subset image selection change (checkbox)"""
        current_window_item = self.window_list.currentItem()
        if not current_window_item:
            return
        
        window_xmid = current_window_item.data(Qt.UserRole)
        window_key = f'window_{window_xmid:.1f}'
        subset_key = item.data(Qt.UserRole)
        
        if window_key in self.analysis_results:
            subset_dispersions = self.analysis_results[window_key].get('subset_dispersions', {})
            if subset_key in subset_dispersions:
                subset_dispersions[subset_key]['selected'] = (item.checkState() == Qt.Checked)
                self.updateSubsetImageInfo(subset_dispersions)
    
    def onSubsetImageClicked(self, item):
        """Handle subset image click (show preview)"""
        if item is not None:
            self.previewSubsetImage(item.data(Qt.UserRole))
    
    def previewSubsetImage(self, subset_key):
        """Preview individual subset dispersion image"""
        current_window_item = self.window_list.currentItem()
        if not current_window_item:
            return
        
        window_xmid = current_window_item.data(Qt.UserRole)
        window_key = f'window_{window_xmid:.1f}'
        
        if window_key not in self.analysis_results:
            return
        
        result = self.analysis_results[window_key]
        subset_dispersions = result.get('subset_dispersions', {})
        
        if subset_key not in subset_dispersions:
            return
        
        subset_data = subset_dispersions[subset_key]
        
        # Clear and plot the individual subset image
        self.dispersion_plot.clear()
        
        # Get dispersion data
        frequencies = result['frequencies']
        velocities = result['velocities']
        dispersion_image = subset_data['dispersion_image']
        
        # Create and plot image
        from .pyqtgraph_utils import createImageItem
        
        # Get current colormap selection
        colormap = self.disp_colormap_combo.currentText() if hasattr(self, 'disp_colormap_combo') else 'gray'
        
        img_item = createImageItem(dispersion_image.T, frequencies, velocities, colormap)
        self.dispersion_plot.addItem(img_item)
        
        # Set labels and title
        self.dispersion_plot.setLabel('bottom', 'Frequency (Hz)')
        self.dispersion_plot.setLabel('left', 'Phase Velocity (m/s)')
        
        ffid = subset_data.get('ffid', f"Shot_{subset_data['shot_index']+1}")
        subset_idx = subset_data['subset_index']
        trace_count = subset_data['trace_count']
        shot_offset = subset_data['shot_offset']
        
        title = f'SINGLE IMAGE: {ffid} (subset {subset_idx}) - {trace_count} traces, offset: {shot_offset:.1f}m'
        self.dispersion_plot.setTitle(title)
        
        # Add colorbar
        self._addDispersionColorbar(img_item, dispersion_image.T)
        
        # Store for potential picking (though picking should be on stacked results)
        self.current_dispersion_data = {
            'frequencies': frequencies,
            'velocities': velocities,
            'dispersion_image': dispersion_image
        }
        
        # Load any saved window curve on top of the subset preview
        self.loadWindowCurve()
        
        # Update subset info to indicate this is a preview
        self.subset_info_text.setPlainText(f"Displaying single dispersion image for subset {subset_idx}\n"
                                          f"Shot: {ffid}, Traces: {trace_count}, Offset: {shot_offset:.1f}m\n"
                                          f"Click 'Show Stacked' to return to stacked view")
        
        # Update spatial layout to show this subset
        self.updateSpatialLayoutForSubset(subset_data)
    
    def updateSpatialLayoutForSubset(self, subset_data):
        """Update spatial layout to highlight the selected subset"""
        try:
            # Extract spatial information from subset data
            traces = subset_data['traces']
            shot_position = subset_data['shot_position']
            
            # Get receiver coordinates from traces
            receiver_coords_x = []
            receiver_coords_y = []
            
            for trace in traces:
                try:
                    # Get geophone position
                    if hasattr(trace.stats, 'segy') and hasattr(trace.stats.segy, 'trace_header'):
                        group_coord_x = trace.stats.segy.trace_header.group_coordinate_x
                        scalar = trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                    elif hasattr(trace.stats, 'su') and hasattr(trace.stats.su, 'trace_header'):
                        group_coord_x = trace.stats.su.trace_header.group_coordinate_x
                        scalar = trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                    else:
                        if hasattr(trace.stats, 'distance'):
                            group_coord_x = trace.stats.distance
                            scalar = 1
                        else:
                            continue
                    
                    # Apply coordinate scalar
                    if scalar != 0:
                        if scalar < 0:
                            geophone_pos = group_coord_x / abs(scalar)
                        else:
                            geophone_pos = group_coord_x * scalar
                    else:
                        geophone_pos = group_coord_x
                        
                    receiver_coords_x.append(geophone_pos)
                    receiver_coords_y.append(0.0)  # Assume linear array at y=0
                        
                except (AttributeError, KeyError):
                    continue
            
            # Create result structure for spatial plotting
            spatial_result = {
                'receiver_coords_x': np.array(receiver_coords_x),
                'receiver_coords_y': np.array(receiver_coords_y),
                'source_position_x': shot_position,
                'source_position_y': 0.0  # Assume shot at y=0
            }
            
            # Update spatial plot
            self.plotSpatialLayout(spatial_result)
            
        except Exception as e:
            print(f"Error updating spatial layout for subset: {e}")
            # Fall back to clearing spatial plot
            self.spatial_plot.clear()
    
    def updateSpatialLayoutForTraceSubset(self):
        """Update spatial layout to highlight the currently selected trace subset (before analysis)"""
        try:
            current_window_item = self.window_list.currentItem()
            if not current_window_item:
                return
            
            window_xmid = current_window_item.data(Qt.UserRole)
            
            # Get the subset data from window_subsets
            if (not hasattr(self, 'window_subsets') or 
                window_xmid not in self.window_subsets or
                self.current_subset_index is None):
                return
            
            subsets = self.window_subsets[window_xmid]
            if self.current_subset_index >= len(subsets):
                return
            
            subset = subsets[self.current_subset_index]
            traces = subset['traces']
            shot_index = subset['shot_index']
            
            # Get shot position
            if shot_index < len(self.shot_positions):
                shot_position = self.shot_positions[shot_index]
            else:
                shot_position = 0.0
            
            # Get receiver coordinates from traces
            receiver_coords_x = []
            receiver_coords_y = []
            
            for trace_info in traces:
                trace_index = trace_info['trace_index']
                
                # Get the actual trace object from streams
                if (shot_index < len(self.streams) and 
                    trace_index < len(self.streams[shot_index])):
                    trace = self.streams[shot_index][trace_index]
                    
                    try:
                        # Get geophone position
                        if hasattr(trace.stats, 'segy') and hasattr(trace.stats.segy, 'trace_header'):
                            group_coord_x = trace.stats.segy.trace_header.group_coordinate_x
                            scalar = trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                        elif hasattr(trace.stats, 'su') and hasattr(trace.stats.su, 'trace_header'):
                            group_coord_x = trace.stats.su.trace_header.group_coordinate_x
                            scalar = trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                        else:
                            if hasattr(trace.stats, 'distance'):
                                group_coord_x = trace.stats.distance
                                scalar = 1
                            else:
                                # Fall back to position from trace_info
                                receiver_coords_x.append(trace_info['position'])
                                receiver_coords_y.append(0.0)
                                continue
                        
                        # Apply coordinate scalar
                        if scalar != 0:
                            if scalar < 0:
                                geophone_pos = group_coord_x / abs(scalar)
                            else:
                                geophone_pos = group_coord_x * scalar
                        else:
                            geophone_pos = group_coord_x
                            
                        receiver_coords_x.append(geophone_pos)
                        receiver_coords_y.append(0.0)  # Assume linear array at y=0
                            
                    except (AttributeError, KeyError):
                        # Fall back to position from trace_info
                        receiver_coords_x.append(trace_info['position'])
                        receiver_coords_y.append(0.0)
                else:
                    # Fall back to position from trace_info if trace not found
                    receiver_coords_x.append(trace_info['position'])
                    receiver_coords_y.append(0.0)
            
            # Create result structure for spatial plotting
            spatial_result = {
                'receiver_coords_x': np.array(receiver_coords_x),
                'receiver_coords_y': np.array(receiver_coords_y),
                'source_position_x': shot_position,
                'source_position_y': 0.0  # Assume shot at y=0
            }
            
            # Update spatial plot
            self.plotSpatialLayout(spatial_result)
            
        except Exception as e:
            print(f"Error updating spatial layout for trace subset: {e}")
            # Fall back to clearing spatial plot
            self.spatial_plot.clear()
    
    def previewSelectedSubset(self):
        """Preview the currently selected subset image"""
        current_item = self.subset_image_list.currentItem()
        if current_item:
            subset_key = current_item.data(Qt.UserRole)
            self.previewSubsetImage(subset_key)
    
    def onSubsetImageCurrentChanged(self, current, previous):
        """Handle subset image selection change via keyboard navigation"""
        if current is not None:
            subset_key = current.data(Qt.UserRole)
            self.previewSubsetImage(subset_key)
    
    def selectAllSubsets(self):
        """Select all subset images for stacking"""
        for i in range(self.subset_image_list.count()):
            item = self.subset_image_list.item(i)
            item.setCheckState(Qt.Checked)
    
    def selectNoSubsets(self):
        """Deselect all subset images"""
        for i in range(self.subset_image_list.count()):
            item = self.subset_image_list.item(i)
            item.setCheckState(Qt.Unchecked)
    
    def stackSelectedSubsets(self):
        """Stack selected subset dispersion images and add to stacked results"""
        current_window_item = self.window_list.currentItem()
        if not current_window_item:
            return
        
        window_xmid = current_window_item.data(Qt.UserRole)
        window_key = f'window_{window_xmid:.1f}'
        
        if window_key not in self.analysis_results:
            return
        
        result = self.analysis_results[window_key]
        subset_dispersions = result.get('subset_dispersions', {})
        
        # Get selected subsets
        selected_subsets = {subset_key: subset_data for subset_key, subset_data in subset_dispersions.items() 
                           if subset_data.get('selected', False)}
        
        if not selected_subsets:
            QMessageBox.warning(self, "No Selection", "No subsets selected for stacking.")
            return
        
        try:
            # Stack dispersion images
            frequencies = result['frequencies']
            velocities = result['velocities']
            
            # Initialize stacked image
            stacked_image = np.zeros((len(frequencies), len(velocities)))
            
            # Add selected dispersion images
            for subset_data in selected_subsets.values():
                stacked_image += subset_data['dispersion_image']
            
            # Normalize by number of stacked images
            stacked_image /= len(selected_subsets)
            
            # Generate unique stack ID
            import time
            stack_id = f"stack_{int(time.time() * 1000) % 100000}"  # Last 5 digits of timestamp
            timestamp = time.strftime("%H:%M:%S")
            
            # Store stacked result (replace any existing result for this window)
            self.stacked_results[window_key] = {
                'frequencies': frequencies,
                'velocities': velocities,
                'dispersion_image': stacked_image,
                'selected_subsets': list(selected_subsets.keys()),
                'num_stacked': len(selected_subsets),
                'timestamp': timestamp,
                'stack_id': stack_id,
                'auto_generated': False  # Manual stack
            }
            
            # Update stacked results list (will show only the current one)
            self.populateStackedResultsList(window_key)
            
            # Automatically show the new stacked result
            self.showStackedResult(window_key)
            
            QMessageBox.information(self, "Stacking Complete", 
                                  f"Stacked {len(selected_subsets)} dispersion images successfully.\n"
                                  f"Stack ID: {stack_id}")
            
        except Exception as e:
            QMessageBox.critical(self, "Stacking Error", f"Error during stacking:\n{e}")
    
    def onStackedResultClicked(self, item):
        """Handle stacked result selection"""
        current_window_item = self.window_list.currentItem()
        if not current_window_item or not item:
            return
        
        window_xmid = current_window_item.data(Qt.UserRole)
        window_key = f'window_{window_xmid:.1f}'
        
        self.showStackedResult(window_key)
    
    def showSelectedStackedResult(self):
        """Show the currently selected stacked result"""
        current_window_item = self.window_list.currentItem()
        if not current_window_item:
            return
        
        window_xmid = current_window_item.data(Qt.UserRole)
        window_key = f'window_{window_xmid:.1f}'
        
        self.showStackedResult(window_key)
    
    def showStackedResult(self, window_key):
        """Display the stacked dispersion result for the given window"""
        if window_key not in self.stacked_results:
            return
        
        stack_data = self.stacked_results[window_key]
        
        # Clear and plot the stacked image
        self.dispersion_plot.clear()
        
        frequencies = stack_data['frequencies']
        velocities = stack_data['velocities']
        stacked_image = stack_data['dispersion_image']
        num_stacked = stack_data['num_stacked']
        timestamp = stack_data['timestamp']
        stack_id = stack_data['stack_id']
        
        # Create and plot image
        from .pyqtgraph_utils import createImageItem
        
        # Get current colormap selection
        colormap = self.disp_colormap_combo.currentText() if hasattr(self, 'disp_colormap_combo') else 'gray'
        
        img_item = createImageItem(stacked_image.T, frequencies, velocities, colormap)
        self.dispersion_plot.addItem(img_item)
        
        # Set labels and title
        self.dispersion_plot.setLabel('bottom', 'Frequency (Hz)')
        self.dispersion_plot.setLabel('left', 'Phase Velocity (m/s)')
        
        title = f'Stacked Dispersion ({stack_id}): {num_stacked} images - {timestamp}'
        self.dispersion_plot.setTitle(title)
        
        # Add colorbar
        self._addDispersionColorbar(img_item, stacked_image.T)
        
        # Store for picking
        self.current_dispersion_data = {
            'frequencies': frequencies,
            'velocities': velocities,
            'dispersion_image': stacked_image
        }
        
        self.current_stacked_id = stack_id
        
        # Enable picking controls
        self.picking_button.setEnabled(True)
        self.removal_button.setEnabled(True)
        self.clear_picking_button.setEnabled(True)
        self.interpolate_button.setEnabled(True)
        self.export_curves_button.setEnabled(True)
        
        # Load any saved window curve on top of the stacked result
        self.loadWindowCurve()
    
    def deleteSelectedStackedResult(self):
        """Delete the currently selected stacked result"""
        current_window_item = self.window_list.currentItem()
        if not current_window_item:
            return
        
        window_xmid = current_window_item.data(Qt.UserRole)
        window_key = f'window_{window_xmid:.1f}'
        
        if window_key not in self.stacked_results:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(self, "Delete Stacked Result", 
                                   f"Are you sure you want to delete the stacked result for this window?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Remove from stored results
            del self.stacked_results[window_key]
            
            # Clear the plot and reset state
            self.dispersion_plot.clear()
            self.current_stacked_id = None
            self.current_dispersion_data = None
            
            # Disable picking controls
            self.picking_button.setEnabled(False)
            self.removal_button.setEnabled(False)
            self.clear_picking_button.setEnabled(False)
            self.interpolate_button.setEnabled(False)
            self.export_curves_button.setEnabled(False)
            
            # Update the list
            self.populateStackedResultsList(window_key)

    # Legacy methods - kept for compatibility but redirected to new workflow
    
    def stackSelectedShots(self):
        """Legacy method - redirects to new stacking workflow"""
        self.stackSelectedSubsets()
    
    def plotStackedDispersion(self, frequencies, velocities, stacked_image, num_stacked):
        """Plot the stacked dispersion image"""
        self.dispersion_plot.clear()
        
        # Create and plot image
        # Get current colormap selection
        colormap = self.disp_colormap_combo.currentText() if hasattr(self, 'disp_colormap_combo') else 'gray'
        
        img_item = createImageItem(stacked_image.T, frequencies, velocities, colormap)
        
        self.dispersion_plot.addItem(img_item)
        self.dispersion_plot.setLabel('bottom', 'Frequency (Hz)')
        self.dispersion_plot.setLabel('left', 'Phase Velocity (m/s)')
        self.dispersion_plot.setTitle(f'Stacked Dispersion Image ({num_stacked} subsets)')
        
        # Store stacked result for picking
        self.current_dispersion_data = {
            'frequencies': frequencies,
            'velocities': velocities,
            'dispersion_image': stacked_image
        }
        
        # Set proper zoom limits and default view for stacked dispersion
        f_min, f_max = frequencies.min(), frequencies.max()
        v_min, v_max = velocities.min(), velocities.max()
        f_margin = (f_max - f_min) * 0.05
        v_margin = (v_max - v_min) * 0.05
        
        # Set view range to show full data
        self.dispersion_plot.setXRange(f_min, f_max, padding=0)
        self.dispersion_plot.setYRange(v_min, v_max, padding=0)
        
        # Set limits to prevent zooming out beyond data range
        self.dispersion_plot.getViewBox().setLimits(
            xMin=f_min - f_margin, xMax=f_max + f_margin,
            yMin=v_min - v_margin, yMax=v_max + v_margin
        )
    
    def plotDispersionImage(self, result):
        """Plot dispersion image using pyqtgraph"""
        # Remove any existing colorbar before clearing plot
        self._removeDispersionColorbar()
        self.dispersion_plot.clear()
        
        # Store current dispersion data for picking
        self.current_dispersion_data = result
        
        # Get data
        frequencies = result['frequencies']
        velocities = result['velocities']
        FV = result['dispersion_image']
        
        # Apply normalization
        FV_plot = np.copy(FV)
        norm = self.current_params['normalization']
        
        if norm == "Frequencies":
            for i, f in enumerate(frequencies):
                if np.nanmax(FV_plot[i, :]) > 0:
                    FV_plot[i, :] = FV_plot[i, :] / np.nanmax(FV_plot[i, :])
        elif norm == "Velocities":
            for i, v in enumerate(velocities):
                if np.nanmax(FV_plot[:, i]) > 0:
                    FV_plot[:, i] = FV_plot[:, i] / np.nanmax(FV_plot[:, i])
        elif norm == 'Global':
            if np.nanmax(FV_plot) > 0:
                FV_plot /= np.nanmax(FV_plot)
        
        # FV has shape (frequencies, velocities), but pyqtgraph ImageItem expects (x, y) format
        # where x corresponds to the bottom axis and y to the left axis
        # So we need to transpose: frequencies (bottom) x velocities (left)
        
        # Get current colormap selection
        colormap = self.disp_colormap_combo.currentText() if hasattr(self, 'disp_colormap_combo') else 'gray'
        
        img_item = createImageItem(FV_plot**2, frequencies, velocities, colormap)
        self.dispersion_plot.addItem(img_item)
        
        # Add colorbar
        self._addDispersionColorbar(img_item, FV_plot**2)
        
        # Set labels and title
        self.dispersion_plot.setLabel('left', 'Phase Velocity [m/s]')
        self.dispersion_plot.setLabel('bottom', 'Frequency [Hz]')
        
        # Set axis ranges and limits
        if len(frequencies) > 1:
            f_min, f_max = frequencies[0], frequencies[-1]
            self.dispersion_plot.setXRange(f_min, f_max)
            # Set limits to prevent zooming beyond data extent
            self.dispersion_plot.getViewBox().setLimits(xMin=f_min, xMax=f_max)
        if len(velocities) > 1:
            v_min, v_max = velocities[0], velocities[-1]
            # Add small margin for better visualization
            v_range = v_max - v_min
            margin = v_range * 0.02  # 2% margin
            self.dispersion_plot.setYRange(v_min - margin, v_max + margin)
            # Set limits to prevent zooming beyond data extent (with margin)
            self.dispersion_plot.getViewBox().setLimits(yMin=v_min - margin, yMax=v_max + margin)
        
        # Enable picking controls now that dispersion data is available
        self.picking_button.setEnabled(True)
        self.removal_button.setEnabled(True)
        
        # Check if there's an extracted curve for current analysis and display it
        if hasattr(self, 'current_stacked_id') and self.current_stacked_id:
            curve_key = f'stacked_{self.current_stacked_id}'
        else:
            curve_key = 'current_analysis'
            
        if curve_key in self.extracted_curves:
            curve_data = self.extracted_curves[curve_key]
            
            # Plot the curve
            curve_item = pg.PlotDataItem(
                x=curve_data['frequencies'], y=curve_data['velocities'],
                pen=pg.mkPen(color='blue', width=3)
            )
            self.dispersion_plot.addItem(curve_item)
            
            # If we have picked points, show them too
            if 'picked_points' in curve_data:
                picked_points = curve_data['picked_points']
                for freq, vel in picked_points:
                        point_item = pg.ScatterPlotItem(
                            x=[freq], y=[vel],
                            pen=pg.mkPen(color='red', width=2),
                            brush=pg.mkBrush(color='red'),
                            size=10, symbol='o'
                        )
                        self.dispersion_plot.addItem(point_item)
            self.dispersion_plot.getViewBox().setLimits(yMin=v_min, yMax=v_max)
    
    def plotSpatialLayout(self, result, window_xmid=None):
        """Plot spatial layout showing all sources and receivers with current selection highlighted"""
        self.spatial_plot.clear()
        
        if not self.streams or not self.shot_positions:
            return
        
        # First, collect ALL geophone and shot positions
        all_geophone_positions = []
        all_shot_positions = self.shot_positions.copy()
        
        # Collect all geophone positions from all shots
        for i, stream in enumerate(self.streams):
            for j, trace in enumerate(stream):
                try:
                    # Get geophone position
                    if hasattr(trace.stats, 'segy') and hasattr(trace.stats.segy, 'trace_header'):
                        group_coord_x = trace.stats.segy.trace_header.group_coordinate_x
                        scalar = trace.stats.segy.trace_header.scalar_to_be_applied_to_all_coordinates
                    elif hasattr(trace.stats, 'su') and hasattr(trace.stats.su, 'trace_header'):
                        group_coord_x = trace.stats.su.trace_header.group_coordinate_x
                        scalar = trace.stats.su.trace_header.scalar_to_be_applied_to_all_coordinates
                    else:
                        if hasattr(trace.stats, 'distance'):
                            group_coord_x = trace.stats.distance
                            scalar = 1
                        else:
                            continue
                    
                    # Apply coordinate scalar
                    if scalar != 0:
                        if scalar < 0:
                            geophone_pos = group_coord_x / abs(scalar)
                        else:
                            geophone_pos = group_coord_x * scalar
                    else:
                        geophone_pos = group_coord_x
                        
                    all_geophone_positions.append(geophone_pos)
                        
                except (AttributeError, KeyError):
                    continue
        
        # Remove duplicates and prepare coordinates
        unique_geophones = sorted(list(set(all_geophone_positions)))
        geophone_x = np.array(unique_geophones)
        geophone_y = np.zeros(len(geophone_x))  # Assume linear array at y=0
        
        shot_x = np.array(all_shot_positions)
        shot_y = np.zeros(len(shot_x))  # Assume shots at y=0
        
        # Draw window extent if available
        if hasattr(self, 'current_window_index') and self.available_windows:
            current_xmid = self.available_windows[self.current_window_index]
            if hasattr(self, 'actual_window_size') and self.actual_window_size:
                window_half_size = self.actual_window_size / 2
                window_left = current_xmid - window_half_size
                window_right = current_xmid + window_half_size
                
                # Calculate window height based on geophone spacing
                geophone_spacing = self._calculateDefaultWindowStep()
                window_height = geophone_spacing  # Use geophone spacing for +/- around y=0
                
                # Draw shaded red window extent as a non-interactive filled area
                x_coords = [window_left, window_right, window_right, window_left, window_left]
                y1_coords = [-window_height/2, -window_height/2, window_height/2, window_height/2, -window_height/2]
                y2_coords = [0, 0, 0, 0, 0]  # Fill from y1 to y2=0
                
                window_fill = pg.FillBetweenItem(
                    pg.PlotDataItem(x_coords, y1_coords),
                    pg.PlotDataItem(x_coords, y2_coords),
                    brush=pg.mkBrush(255, 200, 200, 100)  # Light red with transparency
                )
                self.spatial_plot.addItem(window_fill)
                
                # Add border outline
                window_outline = pg.PlotDataItem(
                    x_coords, y1_coords,
                    pen=pg.mkPen(color='red', width=2, style=QtCore.Qt.DashLine)
                )
                self.spatial_plot.addItem(window_outline)
                
                # Add window center marker as vertical line spanning the full rectangle height
                if window_xmid is not None:
                    # Create vertical line from bottom to top of window rectangle
                    center_line_coords = [current_xmid, current_xmid]
                    center_line_y_coords = [-window_height/2, window_height/2]
                    center_line = pg.PlotDataItem(
                        center_line_coords, center_line_y_coords,
                        pen=pg.mkPen(color='red', width=3)
                    )
                    self.spatial_plot.addItem(center_line)
        
        # Plot ALL geophones with base color (gray triangles)
        if len(geophone_x) > 0:
            all_geophones_scatter = pg.ScatterPlotItem(
                x=geophone_x, 
                y=geophone_y,
                pen=pg.mkPen(color='gray', width=1),
                brush=pg.mkBrush(color='lightgray'),
                size=8,
                symbol='t'  # Triangle
            )
            self.spatial_plot.addItem(all_geophones_scatter)
        
        # Plot ALL shots with base color (gray stars)
        if len(shot_x) > 0:
            all_shots_scatter = pg.ScatterPlotItem(
                x=shot_x, 
                y=shot_y,
                pen=pg.mkPen(color='gray', width=1),
                brush=pg.mkBrush(color='lightgray'),
                size=10,
                symbol='star'  # Star
            )
            self.spatial_plot.addItem(all_shots_scatter)
        
        # Highlight current selection if available
        if result and 'receiver_coords_x' in result:
            # Highlight current geophones (blue triangles)
            current_geophones_scatter = pg.ScatterPlotItem(
                x=result['receiver_coords_x'], 
                y=result['receiver_coords_y'],
                pen=pg.mkPen(color='blue', width=2),
                brush=pg.mkBrush(color='blue'),
                size=10,
                symbol='t'  # Triangle
            )
            self.spatial_plot.addItem(current_geophones_scatter)
            
            # Highlight current shot (red star)
            current_shot_scatter = pg.ScatterPlotItem(
                x=[result['source_position_x']], 
                y=[result['source_position_y']],
                pen=pg.mkPen(color='red', width=3),
                brush=pg.mkBrush(color='red'),
                size=16,
                symbol='star'  # Star
            )
            self.spatial_plot.addItem(current_shot_scatter)
        
        # Set equal aspect ratio for proper spatial representation
        self.spatial_plot.setAspectLocked(True)
        
        # Calculate bounds using min/max of geo/source positions +/- mean spacing
        all_x = np.concatenate([geophone_x, shot_x])
        all_y = np.concatenate([geophone_y, shot_y])
        
        if len(all_x) > 1:
            # Calculate mean spacing for geophones and sources separately
            geo_spacing = 0
            if len(geophone_x) > 1:
                geo_spacing = np.mean(np.diff(sorted(geophone_x)))
            
            source_spacing = 0  
            if len(shot_x) > 1:
                source_spacing = np.mean(np.diff(sorted(shot_x)))
            
            # Use mean of geophone and source spacing
            mean_spacing = np.mean([s for s in [geo_spacing, source_spacing] if s > 0])
            if mean_spacing == 0:
                mean_spacing = 10.0  # Fallback value
            
            # Set bounds to min/max +/- mean spacing
            x_min = np.min(all_x) - mean_spacing
            x_max = np.max(all_x) + mean_spacing
            
            # For linear arrays, set Y range based on X range to show full layout
            x_range = x_max - x_min
            y_center = 0.0
            y_range = max(x_range * 0.3, mean_spacing * 4)  # At least 30% of X range or 4x spacing
            
            self.spatial_plot.setXRange(x_min, x_max)
            self.spatial_plot.setYRange(y_center - y_range/2, y_center + y_range/2)
            
            # Set zoom limits to same bounds
            self.spatial_plot.getViewBox().setLimits(
                xMin=x_min, xMax=x_max,
                yMin=y_center - y_range, yMax=y_center + y_range
            )

    def plotSpectrum(self, result):
        """Plot frequency spectrum - freq vs geophone with amplitude in color"""
        # Remove any existing colorbar before clearing plot
        self._removeSpectrumColorbar()
        self.spectrum_plot.clear()
        
        # Get data (already sorted by offset in worker)
        XT = result['data_matrix']
        receiver_coords_x = result['receiver_coords_x']
        receiver_coords_y = result['receiver_coords_y']
        si = result['sampling_interval']
        
        # Calculate frequency spectrum
        from scipy.fft import rfft, rfftfreq
        
        Nt = XT.shape[1]
        XF = rfft(XT, axis=1, n=Nt)
        XF = np.abs(XF)
        fs = rfftfreq(Nt, si)
        
        # Limit to max frequency from current UI parameters
        try:
            fmax = float(self.fmax_edit.text()) if hasattr(self, 'fmax_edit') else 100
        except (ValueError, AttributeError):
            fmax = 100  # Default fallback
            
        f_indices = fs <= fmax
        fs = fs[f_indices]
        XF = XF[:, f_indices]
        
        # Normalize traces for better color visualization
        for i in range(XF.shape[0]):
            if np.nanmax(XF[i, :]) > 0:
                XF[i, :] = XF[i, :] / np.nanmax(XF[i, :])
        
        # For frequency spectrum: frequency (X) vs geophone position (Y)
        # XF has shape (geophones, frequencies)
        # We want to display with freq on X-axis and geophone positions on Y-axis
        # So we need XF as-is (no transpose needed)
        XF_display = XF  # Shape: (geophones, frequencies) = (Y, X)
        
        # Create image item with proper axes: frequencies=X, geophones=Y
        img_item = createImageItem(XF_display, fs, receiver_coords_x, 'gray')
        self.spectrum_plot.addItem(img_item)
        
        # Set proper labels for frequency spectrum (remove duplicates)
        self.spectrum_plot.setLabel('left', 'Geophone Position [m]')
        self.spectrum_plot.setLabel('bottom', 'Frequency [Hz]')
        
        # Add colorbar
        self._addSpectrumColorbar(img_item, XF_display)
        
        # Set axis ranges and limits like surface wave analysis
        if len(fs) > 1:
            f_min, f_max = fs[0], fs[-1]
            self.spectrum_plot.setXRange(f_min, f_max)
            # Set limits to prevent zooming beyond data extent
            self.spectrum_plot.getViewBox().setLimits(xMin=f_min, xMax=f_max)
        if len(receiver_coords_x) > 1:
            x_min, x_max = receiver_coords_x[0], receiver_coords_x[-1]  # Already sorted
            # Add small margin for better visualization
            x_range = x_max - x_min
            margin = x_range * 0.02  # 2% margin
            self.spectrum_plot.setYRange(x_min - margin, x_max + margin)
            # Set limits to prevent zooming beyond data extent (with margin)
            self.spectrum_plot.getViewBox().setLimits(yMin=x_min - margin, yMax=x_max + margin)
    
    def plotSeismogram(self, result):
        """Plot seismogram traces using wiggle or image display"""
        self.current_result = result  # Store for refresh
        self._plotSeismogramInternal(result)
    
    def refreshSeismogram(self):
        """Refresh seismogram plot with current parameters"""
        # Always update control visibility based on display mode, even if no data
        self.updateControlsForDisplayMode()
        
        if self.current_result is not None:
            self._plotSeismogramInternal(self.current_result)
    
    def refreshDispersionColormap(self):
        """Refresh dispersion image with current colormap"""
        if hasattr(self, 'current_dispersion_data') and self.current_dispersion_data is not None:
            # Re-plot the current dispersion image with new colormap
            dispersion_image = self.current_dispersion_data['dispersion_image']
            frequencies = self.current_dispersion_data['frequencies']
            velocities = self.current_dispersion_data['velocities']
            
            # Clear and re-plot with new colormap
            self.dispersion_plot.clear()
            
            # Get current colormap selection
            colormap = self.disp_colormap_combo.currentText()
            
            # Create new image item with selected colormap
            from .pyqtgraph_utils import createImageItem
            img_item = createImageItem(dispersion_image.T, frequencies, velocities, colormap)
            self.dispersion_plot.addItem(img_item)
            
            # Restore any picked points and curve that were displayed
            self.updateDispersionDisplay()
    
    def refreshSpectrumColormap(self):
        """Refresh spectrum image with current colormap"""
        if hasattr(self, 'current_spectrum_data') and self.current_spectrum_data is not None:
            # Re-plot the current spectrum with new colormap
            shot_indices = self.current_spectrum_data['shot_indices']
            trace_numbers = self.current_spectrum_data['trace_numbers']
            
            # Re-compute and plot spectrum with new colormap
            self.updateSpectrumPlot(shot_indices, trace_numbers)
    
    def _plotSeismogramInternal(self, result):
        """Plot seismogram traces using wiggle or image display - mimicking sw_analysis module"""
        self.wiggle_plot.clear()
        
        # Always remove any existing colorbar first
        self._removeSeismogramColorbar()
        
        # Reset view box limits to ensure clean state (but don't auto-range yet)
        self.wiggle_plot.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)
        
        # Get data (already sorted by offset in worker)
        XT = result['data_matrix']
        receiver_coords_x = result['receiver_coords_x']
        distances = result['distances']
        trace_positions = result['trace_positions']
        si = result['sampling_interval']
        
        # Check if we have data
        if XT.size == 0 or len(distances) == 0:
            # Set labels to match sw_analysis module
            self.wiggle_plot.setLabel('left', 'Time [s]')
            self.wiggle_plot.setLabel('bottom', 'Distance [m]')
            return
        
        # Create time axis
        Nt = XT.shape[1]
        time = np.arange(Nt) * si
        
        # Determine display mode and trace positioning like sw_analysis
        display_mode = "Wiggle"
        if hasattr(self, 'display_mode_combo'):
            display_mode = self.display_mode_combo.currentText()
        
        trace_by_position = True
        if hasattr(self, 'trace_by_combo'):
            trace_by_position = self.trace_by_combo.currentText() == "Position"
        
        # Use positions like sw_analysis module
        if trace_by_position:
            plot_positions = trace_positions
            xlabel = 'Distance [m]'
        else:
            plot_positions = np.arange(len(trace_positions))
            xlabel = 'Trace Number'
        
        # Set labels like sw_analysis module
        self.wiggle_plot.setLabel('left', 'Time [s]')
        self.wiggle_plot.setLabel('bottom', xlabel)
        
        if display_mode == "Image":
            # Plot as image
            self._plotSeismogramImage(XT, time, plot_positions)
        else:
            # Plot as wiggle traces
            self._plotSeismogramWiggle(XT, time, plot_positions)
        
        # Set axis ranges AFTER plotting to avoid interference
        # Apply X-axis padding - use only 1 geophone spacing on each side
        x_range = max(plot_positions) - min(plot_positions)
        if x_range > 0 and len(plot_positions) > 1:
            # Calculate geophone spacing
            spacing = np.mean(np.diff(sorted(plot_positions)))
            padding = spacing  # Use exactly 1 geophone spacing on each side
            self.wiggle_plot.setXRange(min(plot_positions) - padding, 
                                     max(plot_positions) + padding, padding=0)
            # Set limits to prevent zooming beyond this range
            self.wiggle_plot.getViewBox().setLimits(
                xMin=min(plot_positions) - padding, 
                xMax=max(plot_positions) + padding
            )
        elif x_range > 0:
            # Fallback for single trace
            padding = x_range * 0.1
            self.wiggle_plot.setXRange(min(plot_positions) - padding, 
                                     max(plot_positions) + padding, padding=0)
        
        # Set time axis range based on fix_max_time setting
        if len(time) > 0:
            if hasattr(self, 'fix_max_time_check') and self.fix_max_time_check.isChecked():
                if hasattr(self, 'max_time_spinbox'):
                    max_y = self.max_time_spinbox.value()
                else:
                    max_y = time[-1]
            else:
                max_y = time[-1]
            
            self.wiggle_plot.setYRange(time[0], max_y)
            # Always set limits to data extent to prevent zooming beyond data
            self.wiggle_plot.getViewBox().setLimits(yMin=time[0], yMax=time[-1])
    
    def updateControlsForDisplayMode(self):
        """Show/hide controls based on current display mode (wiggle vs image)"""
        if hasattr(self, 'display_mode_combo'):
            is_wiggle_mode = (self.display_mode_combo.currentText() == "Wiggle")
            is_image_mode = not is_wiggle_mode
            
            # Controls that only work in wiggle mode - hide in image mode
            if hasattr(self, 'gain_label'):
                self.gain_label.setVisible(is_wiggle_mode)
            if hasattr(self, 'gain_spinbox'):
                self.gain_spinbox.setVisible(is_wiggle_mode)
            if hasattr(self, 'fill_label'):
                self.fill_label.setVisible(is_wiggle_mode)
            if hasattr(self, 'fill_combo'):
                self.fill_combo.setVisible(is_wiggle_mode)
            if hasattr(self, 'clip_check'):
                self.clip_check.setVisible(is_wiggle_mode)
            
            # Controls that only work in image mode - hide in wiggle mode
            if hasattr(self, 'colormap_label'):
                self.colormap_label.setVisible(is_image_mode)
            if hasattr(self, 'colormap_combo'):
                self.colormap_combo.setVisible(is_image_mode)
            
        # Controls that work in both modes remain visible
        # (Display mode, Trace by, Normalize, Max time, Fix max time)
    
    def enableSeismogramControls(self, enabled=True):
        """Enable or disable seismogram controls"""
        # Basic display controls
        if hasattr(self, 'display_mode_combo'):
            self.display_mode_combo.setEnabled(enabled)
        if hasattr(self, 'trace_by_combo'):
            self.trace_by_combo.setEnabled(enabled)
        if hasattr(self, 'normalize_check'):
            self.normalize_check.setEnabled(enabled)
            
        # Wiggle mode controls
        if hasattr(self, 'gain_spinbox'):
            self.gain_spinbox.setEnabled(enabled)
        if hasattr(self, 'fill_combo'):
            self.fill_combo.setEnabled(enabled)
        if hasattr(self, 'clip_check'):
            self.clip_check.setEnabled(enabled)
            
        # Image mode controls
        if hasattr(self, 'colormap_combo'):
            self.colormap_combo.setEnabled(enabled)
            
        # Time controls
        if hasattr(self, 'max_time_spinbox'):
            self.max_time_spinbox.setEnabled(enabled)
        if hasattr(self, 'fix_max_time_check'):
            self.fix_max_time_check.setEnabled(enabled)
    
    def _plotSeismogramImage(self, XT, time, plot_positions):
        """Plot seismogram as an image"""
        # Apply parameters
        normalize = self.normalize_check.isChecked() if hasattr(self, 'normalize_check') else True
        gain = self.gain_spinbox.value() if hasattr(self, 'gain_spinbox') else 1.0
        colormap = self.colormap_combo.currentText() if hasattr(self, 'colormap_combo') else 'gray'
        
        # Process data
        XT_plot = XT.copy()
        
        if normalize:
            # Normalize each trace
            for i in range(XT_plot.shape[0]):
                if np.nanmax(np.abs(XT_plot[i, :])) > 0:
                    XT_plot[i, :] = XT_plot[i, :] / np.nanmax(np.abs(XT_plot[i, :]))
        
        # Apply gain
        XT_plot *= gain
        
        # For seismogram: we want Distance on X-axis, Time on Y-axis (downward)
        # XT has shape (traces, time_samples)
        # PyQtGraph ImageItem: data[x,y] where x=horizontal, y=vertical
        # We want horizontal=distance/traces, vertical=time
        # So we need data shape (traces, time_samples) which XT already has!
        # NO transpose needed - use XT_plot directly
        XT_display = XT_plot  # Shape: (traces, time_samples)
        
        # Create image item: positions=X, time=Y
        from .pyqtgraph_utils import createImageItem
        img_item = createImageItem(XT_display, plot_positions, time, colormap)
        self.wiggle_plot.addItem(img_item)
        
        # Add colorbar for image mode
        self._addSeismogramColorbar(img_item, XT_display)
    
    def _plotSeismogramWiggle(self, XT, time, plot_positions):
        """Plot seismogram as wiggle traces"""
        
        # Calculate trace spacing
        if len(plot_positions) > 1:
            sorted_positions = np.sort(plot_positions)
            mean_spacing = np.mean(np.diff(sorted_positions))
        else:
            mean_spacing = 1.0
        
        # Ensure minimum spacing
        if mean_spacing <= 0:
            mean_spacing = 1.0
        
        # Wiggle plotting parameters (get from controls)
        normalize = self.normalize_check.isChecked() if hasattr(self, 'normalize_check') else True
        gain = self.gain_spinbox.value() if hasattr(self, 'gain_spinbox') else 1.0
        clip = self.clip_check.isChecked() if hasattr(self, 'clip_check') else False
        fill_text = self.fill_combo.currentText() if hasattr(self, 'fill_combo') else 'Positive'
        fill = fill_text.lower()  # Convert to lowercase for consistency
        # Plot each trace as a wiggle using core's approach
        for i, trace_data in enumerate(XT):
            # Skip empty traces
            if len(trace_data) == 0:
                continue
            
            # Get wiggle info using core's approach
            x, x_filled, t_interpolated, fillLevel, mask = self.getWiggleInfo(
                trace_data, time, plot_positions[i], mean_spacing, 
                normalize, gain, clip, fill
            )
            
            # Plot the original curve (no time samples option)
            self.wiggle_plot.plot(x, time, pen=pg.mkPen(color='black', width=1))
            
            # Plot the filled part
            if mask is not None and len(t_interpolated) > 0:
                # Create brush for fill (consistent with core module - both positive and negative use black)
                if fill == 'positive':
                    fill_brush = pg.mkBrush(color='black', alpha=100)
                elif fill == 'negative':
                    fill_brush = pg.mkBrush(color='black', alpha=100)
                else:  # fill == 'none'
                    fill_brush = None
                
                if fill_brush is not None:
                    self.wiggle_plot.plot(x_filled, t_interpolated, pen=None,
                                        fillLevel=fillLevel, brush=fill_brush)
    
    def getWiggleInfo(self, trace_data, time, offset, mean_spacing, normalize, gain, clip, fill):
        """Get wiggle plot info using core module's approach"""
        
        # Ensure trace_data is a NumPy array of floats
        trace_data = np.array(trace_data, dtype=float)
        
        if normalize:
            if np.all(trace_data == 0):
                normalized_trace_data = trace_data
            else:
                # Normalize to max value of 1 and scale by mean_spacing/2
                normalized_trace_data = (trace_data / np.max(np.abs(trace_data))) * (mean_spacing/2) * gain
        else:
            normalized_trace_data = trace_data * gain
        
        # Clip the trace data
        if clip:
            normalized_trace_data = np.clip(normalized_trace_data, -(mean_spacing/2), (mean_spacing/2))
        
        # Add the offset to the normalized trace data
        x = normalized_trace_data + offset
        
        # Get the fill level
        fillLevel = np.array(offset, dtype=float)
        
        # Create a mask for positive or negative amplitudes
        if fill == 'positive':
            mask = x >= fillLevel
        elif fill == 'negative':
            mask = x <= fillLevel
        else:  # fill == 'none'
            mask = None
        
        # Interpolate points to ensure smooth transition (from core module)
        x_interpolated = []
        t_interpolated = []
        for j in range(len(x) - 1):
            x_interpolated.append(x[j])
            t_interpolated.append(time[j])
            if mask is not None and j < len(mask) - 1 and mask[j] != mask[j + 1]:
                # Linear interpolation
                if (x[j + 1] - x[j]) != 0:  # Avoid division by zero
                    t_interp = time[j] + (time[j + 1] - time[j]) * (fillLevel - x[j]) / (x[j + 1] - x[j])
                    x_interpolated.append(fillLevel)
                    t_interpolated.append(t_interp)
        
        if len(x) > 0:
            x_interpolated.append(x[-1])
            t_interpolated.append(time[-1])
        
        x_interpolated = np.array(x_interpolated)
        t_interpolated = np.array(t_interpolated)
        
        # Create arrays for the filled parts
        if fill == 'positive':
            x_filled = np.where(x_interpolated >= fillLevel, x_interpolated, fillLevel)
        elif fill == 'negative':
            x_filled = np.where(x_interpolated <= fillLevel, x_interpolated, fillLevel)
        else:  # fill == 'none'
            x_filled = x_interpolated
        
        return x, x_filled, t_interpolated, fillLevel, mask
    
    def clearResults(self):
        """Clear analysis results"""
        # Stop any running worker thread
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        # Clear results and plots
        self.analysis_results = {}
        
        # Remove colorbars before clearing plots
        self._removeDispersionColorbar()
        self._removeSpectrumColorbar()
        self._removeSeismogramColorbar()
        
        self.dispersion_plot.clear()
        self.spectrum_plot.clear()
        self.wiggle_plot.clear()
        self.spatial_plot.clear()
        
        # Keep reasonable default limits to prevent excessive zoom-out
        # These will be updated with proper data ranges when data is loaded
        self.dispersion_plot.getViewBox().setLimits(xMin=0, xMax=500, yMin=0, yMax=2000)
        self.spectrum_plot.getViewBox().setLimits(xMin=0, xMax=200, yMin=0, yMax=1000)
        self.wiggle_plot.getViewBox().setLimits(xMin=-1000, xMax=1000, yMin=0, yMax=10)
        self.spatial_plot.getViewBox().setLimits(xMin=-1000, xMax=1000, yMin=-1000, yMax=1000)
        
        # Clear selections in relevant lists
        if hasattr(self, 'subset_list'):
            self.subset_list.clearSelection()
        if hasattr(self, 'window_list'):
            self.window_list.clearSelection()
        if hasattr(self, 'stacked_results_list'):
            self.stacked_results_list.clearSelection()
        
        QMessageBox.information(self, "Results Cleared", "Analysis results have been cleared.")
    
    def togglePicking(self):
        """Toggle picking mode on/off"""
        if not self.picking_mode:
            # Start picking mode
            self.picking_mode = True
            self.removal_mode = False  # Ensure removal mode is off
            self.picking_button.setText("Stop Picking")
            self.removal_button.setText("Remove Points")
            
            # Disconnect any existing connections first
            try:
                self.dispersion_plot.scene().sigMouseClicked.disconnect(self.onDispersionClick)
            except TypeError:
                pass  # No connection to disconnect
                
            # Connect mouse click event to dispersion plot
            self.dispersion_plot.scene().sigMouseClicked.connect(self.onDispersionClick)
            
            # Show instructions
            picking_mode_text = "Manual" if self.picking_mode_combo.currentIndex() == 0 else "Auto (find maximum)"
            QMessageBox.information(self, "Picking Mode", 
                                   f"Click on the dispersion image to pick points.\n"
                                   f"Current mode: {picking_mode_text}\n"
                                   "Use 'Interpolate Curve' to create a smooth curve between points.")
        else:
            # Stop picking mode
            self.picking_mode = False
            self.picking_button.setText("Start Picking")
            
            # Disconnect mouse click event
            try:
                self.dispersion_plot.scene().sigMouseClicked.disconnect(self.onDispersionClick)
            except TypeError:
                pass  # Already disconnected
                self.dispersion_plot.scene().sigMouseClicked.disconnect(self.onDispersionClick)
            except TypeError:
                pass  # Already disconnected
    
    def toggleRemoval(self):
        """Toggle point removal mode on/off"""
        if not self.removal_mode:
            # Start removal mode
            self.removal_mode = True
            self.picking_mode = False  # Ensure picking mode is off
            self.removal_button.setText("Stop Removal")
            self.picking_button.setText("Start Picking")
            
            # Disconnect any existing connections first
            try:
                self.dispersion_plot.scene().sigMouseClicked.disconnect(self.onDispersionClick)
            except TypeError:
                pass  # No connection to disconnect
                
            # Connect mouse click event to dispersion plot
            self.dispersion_plot.scene().sigMouseClicked.connect(self.onDispersionClick)
            
            # Show instructions
            QMessageBox.information(self, "Removal Mode", 
                                   "Click near existing points to remove them.\n"
                                   "The closest point to your click will be removed.")
        else:
            # Stop removal mode
            self.removal_mode = False
            self.removal_button.setText("Remove Points")
            
            # Disconnect mouse click event
            try:
                self.dispersion_plot.scene().sigMouseClicked.disconnect(self.onDispersionClick)
            except TypeError:
                pass  # Already disconnected
    
    def onDispersionClick(self, event):
        """Handle mouse clicks on dispersion plot"""
        if not (self.picking_mode or self.removal_mode):
            return
            
        # Only handle left mouse button clicks
        if event.button() != 1:  # 1 = left mouse button
            return
            
        # Get click position in plot coordinates
        pos = event.scenePos()
        if self.dispersion_plot.sceneBoundingRect().contains(pos):
            mouse_point = self.dispersion_plot.plotItem.vb.mapSceneToView(pos)
            clicked_freq = mouse_point.x()
            clicked_velocity = mouse_point.y()
            
            if self.picking_mode:
                self.pickPointAtFrequency(clicked_freq, clicked_velocity)
            elif self.removal_mode:
                self.removeNearestPoint(clicked_freq, clicked_velocity)
    
    def calculatePickErrors(self, frequencies, velocities):
        """Calculate Lorentzian errors for picked points"""
        try:
            # Get current subset information for error calculation
            current_window_item = self.window_list.currentItem()
            current_subset_item = self.subset_list.currentItem()
            
            if current_window_item is None or current_subset_item is None:
                print("Warning: No current window/subset for error calculation, using default values")
                # Use default values if no subset available
                dx = 1.0  # 1m spacing
                Nx = 10   # 10 traces
            else:
                # Get subset data to calculate spacing parameters
                window_xmid = current_window_item.data(Qt.UserRole)
                subset_index = current_subset_item.data(Qt.UserRole)
                
                if (window_xmid in self.window_subsets and 
                    subset_index < len(self.window_subsets[window_xmid])):
                    
                    selected_subset = self.window_subsets[window_xmid][subset_index]
                    
                    # Extract geophone positions
                    geophone_positions = [trace_info['position'] for trace_info in selected_subset['traces']]
                    
                    if len(geophone_positions) > 1:
                        # Calculate average spacing
                        sorted_positions = sorted(geophone_positions)
                        spacings = [sorted_positions[i+1] - sorted_positions[i] 
                                  for i in range(len(sorted_positions)-1)]
                        dx = np.mean(spacings) if spacings else 1.0
                        Nx = len(geophone_positions)
                    else:
                        dx = 1.0
                        Nx = 1
                else:
                    print("Warning: Current subset not found, using default values")
                    dx = 1.0
                    Nx = 10
            
            # Calculate errors using Lorentzian function
            v_array = np.array(velocities)
            f_array = np.array(frequencies)
            
            print(f"Calculating errors with dx={dx:.2f}m, Nx={Nx} traces")
            errors = lorentzian_error(v_array, f_array, dx, Nx, a=0.5)
            
            return errors.tolist()
            
        except Exception as e:
            print(f"Error calculating pick errors: {e}")
            import traceback
            traceback.print_exc()
            # Return default errors (10% of velocity or 5 m/s minimum)
            return [max(0.1 * v, 5.0) for v in velocities]
    
    def pickPointAtFrequency(self, clicked_freq, clicked_velocity):
        """Pick point either manually or automatically by finding maximum at frequency"""
        print(f"DEBUG: pickPointAtFrequency called with freq={clicked_freq:.2f}, vel={clicked_velocity:.2f}")
        
        if self.current_dispersion_data is None:
            print("DEBUG: current_dispersion_data is None, cannot pick")
            return
        
        result = self.current_dispersion_data
        FV = result['dispersion_image']
        frequencies = result['frequencies']
        velocities = result['velocities']
        
        # Check picking mode
        is_auto_mode = self.picking_mode_combo.currentIndex() == 1
        
        if is_auto_mode:
            # Auto mode: find maximum at the clicked frequency
            print(f"DEBUG: Auto mode - finding maximum at freq={clicked_freq:.2f}")
            print(f"DEBUG: Frequencies shape: {frequencies.shape}, range: {frequencies.min():.2f} to {frequencies.max():.2f}")
            print(f"DEBUG: Velocities shape: {velocities.shape}, range: {velocities.min():.2f} to {velocities.max():.2f}")
            print(f"DEBUG: Dispersion image shape: {FV.shape}")
            
            # Find the closest frequency index
            freq_idx = np.argmin(np.abs(frequencies - clicked_freq))
            actual_freq = frequencies[freq_idx]
            print(f"DEBUG: Closest freq_idx={freq_idx}, actual_freq={actual_freq:.2f}")
            
            # Get the dispersion values at this frequency (correct indexing: FV[freq_idx, :])
            dispersion_slice = FV[freq_idx, :]
            print(f"DEBUG: Dispersion slice shape: {dispersion_slice.shape}")
            print(f"DEBUG: Dispersion slice range: {dispersion_slice.min():.6f} to {dispersion_slice.max():.6f}")
            print(f"DEBUG: Non-zero values in slice: {np.count_nonzero(dispersion_slice)}")
            
            # Find the maximum velocity at this frequency, but exclude very low velocities
            # Use max of 50 m/s or 2*dv as minimum threshold to avoid numerical artifacts
            dv = self.current_params.get('dv', 10)
            min_velocity_threshold = max(50.0, 2 * dv)  # Minimum reasonable velocity for surface waves
            valid_velocity_mask = velocities >= min_velocity_threshold
            
            if np.any(valid_velocity_mask):
                # Only consider velocities above the threshold
                masked_dispersion = np.where(valid_velocity_mask, dispersion_slice, -np.inf)
                max_vel_idx = np.argmax(masked_dispersion)
                picked_velocity = velocities[max_vel_idx]
                print(f"DEBUG: Using velocity threshold {min_velocity_threshold} m/s")
                print(f"DEBUG: Valid velocities range: {velocities[valid_velocity_mask].min():.1f} to {velocities[valid_velocity_mask].max():.1f} m/s")
            else:
                # Fallback to original method if no valid velocities
                max_vel_idx = np.argmax(dispersion_slice)
                picked_velocity = velocities[max_vel_idx]
                print(f"WARNING: No velocities above {min_velocity_threshold} m/s threshold, using unconstrained pick")
            
            picked_freq = actual_freq
            print(f"DEBUG: Max vel_idx={max_vel_idx}, picked_velocity={picked_velocity:.2f}")
            print(f"DEBUG: velocities[0:5] = {velocities[0:5]}")
            print(f"DEBUG: dispersion_slice[0:5] = {dispersion_slice[0:5]}")
            print(f"DEBUG: dispersion_slice max value = {dispersion_slice.max():.6f} at index {max_vel_idx}")
            
            # Check if the maximum value is significant
            if dispersion_slice.max() < 1e-10:
                print("WARNING: Very low maximum value in dispersion slice - may be picking noise")
                
            # Additional validation for picked velocity
            if picked_velocity < min_velocity_threshold:
                print(f"WARNING: Picked velocity {picked_velocity:.1f} m/s is below recommended threshold {min_velocity_threshold} m/s")
            
            # Also check if clicked frequency is too low/high
            if clicked_freq < frequencies.min() or clicked_freq > frequencies.max():
                print(f"WARNING: Clicked frequency {clicked_freq:.2f} is outside data range [{frequencies.min():.2f}, {frequencies.max():.2f}]")
        else:
            # Manual mode: use clicked coordinates directly
            picked_freq = clicked_freq
            picked_velocity = clicked_velocity
        
        # Check if we already have a point at this frequency (replace if so)
        existing_idx = None
        for i, point_data in enumerate(self.picked_points):
            # Handle both old format (freq, vel) and new format {'freq': x, 'vel': y, 'mode': m}
            if isinstance(point_data, dict):
                f = point_data['frequency']
            else:
                f = point_data[0]  # Old format compatibility
            
            if abs(f - picked_freq) < (frequencies[1] - frequencies[0]) * 0.5:  # Within half frequency step
                existing_idx = i
                break
        
        # Create point data with mode information
        point_data = {
            'frequency': picked_freq,
            'velocity': picked_velocity,
            'mode': self.current_mode
        }
        
        print(f"DEBUG: Creating point with mode {self.current_mode} - freq={picked_freq:.2f}, vel={picked_velocity:.2f}")
        
        if existing_idx is not None:
            # Replace existing point
            self.picked_points[existing_idx] = point_data
            # Remove old plot item
            self.dispersion_plot.removeItem(self.picked_point_items[existing_idx])
            self.picked_point_items[existing_idx] = None
        else:
            # Add new point
            self.picked_points.append(point_data)
            self.picked_point_items.append(None)
            existing_idx = len(self.picked_points) - 1
        
        # Get color for current mode
        current_color = self.mode_colors.get(self.current_mode, 'red')
        
        # Create new plot item with mode-specific color
        point_item = pg.ScatterPlotItem(
            x=[picked_freq], y=[picked_velocity],
            pen=pg.mkPen(color=current_color, width=2),
            brush=pg.mkBrush(color=current_color),
            size=5, symbol='o'
        )
        self.dispersion_plot.addItem(point_item)
        self.picked_point_items[existing_idx] = point_item
        
        # Sort points by frequency (handle both old and new data formats)
        def get_frequency(point_data):
            if isinstance(point_data, dict):
                return point_data['frequency']
            else:
                return point_data[0]  # Old format compatibility
        
        sorted_data = sorted(zip(self.picked_points, self.picked_point_items), 
                           key=lambda x: get_frequency(x[0]))
        self.picked_points = [item[0] for item in sorted_data]
        self.picked_point_items = [item[1] for item in sorted_data]
        
        # Enable interpolation if we have at least 2 points
        if len(self.picked_points) >= 2:
            self.interpolate_button.setEnabled(True)
        
        # Enable clearing if we have points
        if len(self.picked_points) > 0:
            self.clear_picking_button.setEnabled(True)
            self.show_errors_button.setEnabled(True)
        
        # Update error bars if they are currently shown
        if self.show_error_bars:
            self.showErrorBars()
        
        # Auto-save picked points to window memory with errors
        if self.current_window_key:
            if self.current_window_key not in self.window_curves:
                self.window_curves[self.current_window_key] = {}
            
            # Calculate errors for all picked points
            if self.picked_points:
                # Extract frequencies and velocities (handle both old and new formats)
                frequencies = []
                velocities = []
                for point_data in self.picked_points:
                    if isinstance(point_data, dict):
                        frequencies.append(point_data['frequency'])
                        velocities.append(point_data['velocity'])
                    else:
                        frequencies.append(point_data[0])  # Old format compatibility
                        velocities.append(point_data[1])
                
                errors = self.calculatePickErrors(frequencies, velocities)
                
                # Store as list of dictionaries with error and mode information
                picked_points_with_errors = []
                for i, point_data in enumerate(self.picked_points):
                    if isinstance(point_data, dict):
                        picked_points_with_errors.append({
                            'frequency': point_data['frequency'],
                            'velocity': point_data['velocity'],
                            'mode': point_data['mode'],
                            'error': errors[i] if i < len(errors) else 5.0
                        })
                    else:
                        # Old format compatibility
                        picked_points_with_errors.append({
                            'frequency': point_data[0],
                            'velocity': point_data[1],
                            'mode': 0,  # Default to fundamental mode
                            'error': errors[i] if i < len(errors) else 5.0
                        })
                
                self.window_curves[self.current_window_key]['picked_points'] = self.picked_points.copy()
                self.window_curves[self.current_window_key]['picked_points_with_errors'] = picked_points_with_errors
            else:
                self.window_curves[self.current_window_key]['picked_points'] = []
                self.window_curves[self.current_window_key]['picked_points_with_errors'] = []
        
        # Update pseudo-section plot with new picks
        self.updatePseudoSection()
        
        # Update window curves status
        self.updateWindowCurvesStatus()
    
    def removeNearestPoint(self, clicked_freq, clicked_velocity):
        """Remove the nearest picked point to the click location"""
        if not self.picked_points:
            return
        
        # Find the nearest point using a simple distance metric
        min_distance = float('inf')
        nearest_idx = -1
        
        # Get current plot ranges for normalization
        freq_range = self.dispersion_plot.getAxis('bottom').range
        vel_range = self.dispersion_plot.getAxis('left').range
        freq_scale = freq_range[1] - freq_range[0]
        vel_scale = vel_range[1] - vel_range[0]
        
        for i, point_data in enumerate(self.picked_points):
            # Handle both old format (freq, vel) and new format {'frequency': x, 'velocity': y, 'mode': m}
            if isinstance(point_data, dict):
                freq = point_data['frequency']
                vel = point_data['velocity']
            else:
                # Old format compatibility
                freq, vel = point_data
            
            # Normalize coordinates using plot ranges
            norm_freq_diff = (clicked_freq - freq) / freq_scale if freq_scale > 0 else 0
            norm_vel_diff = (clicked_velocity - vel) / vel_scale if vel_scale > 0 else 0
                
            distance = np.sqrt(norm_freq_diff**2 + norm_vel_diff**2)
            
            if distance < min_distance:
                min_distance = distance
                nearest_idx = i
        
        if nearest_idx >= 0:
            # Remove the specific point and its plot item
            if self.picked_point_items[nearest_idx] is not None:
                self.dispersion_plot.removeItem(self.picked_point_items[nearest_idx])
            
            # Remove from data structures
            del self.picked_points[nearest_idx]
            del self.picked_point_items[nearest_idx]
            
            # Update interpolated curve if it exists (re-interpolate with remaining points)
            if self.curve_line is not None:
                self.dispersion_plot.removeItem(self.curve_line)
                self.curve_line = None
                
                # Re-interpolate if we still have enough points
                if len(self.picked_points) >= 2:
                    self.interpolateCurve()
            
            # Update button states
            if len(self.picked_points) < 2:
                self.interpolate_button.setEnabled(False)
            
            if len(self.picked_points) == 0:
                self.clear_picking_button.setEnabled(False)
                self.show_errors_button.setEnabled(False)
                self.hideErrorBars()
            else:
                # Update error bars if they are currently shown
                if self.show_error_bars:
                    self.showErrorBars()
            
            # Update pseudo-section plot after point removal
            self.updatePseudoSection()
            
            # Update window curves status
            self.updateWindowCurvesStatus()
    
    def interpolateCurve(self):
        """Interpolate a smooth curve between picked points"""
        if len(self.picked_points) < 2:
            QMessageBox.warning(self, "Insufficient Points", 
                               "Please pick at least 2 points to interpolate a curve.")
            return
        
        try:
            # Extract frequencies and velocities (handle both old and new formats)
            frequencies = []
            velocities = []
            for point_data in self.picked_points:
                if isinstance(point_data, dict):
                    frequencies.append(point_data['frequency'])
                    velocities.append(point_data['velocity'])
                else:
                    frequencies.append(point_data[0])  # Old format compatibility
                    velocities.append(point_data[1])
            
            # Sort points by frequency
            sorted_indices = np.argsort(frequencies)
            frequencies = np.array([frequencies[i] for i in sorted_indices])
            velocities = np.array([velocities[i] for i in sorted_indices])
            
            # Create interpolated curve from min to max frequency
            freq_min, freq_max = frequencies[0], frequencies[-1]
            
            # Get frequency resolution from dispersion data
            result = self.current_dispersion_data
            orig_frequencies = result['frequencies']
            freq_step = orig_frequencies[1] - orig_frequencies[0]
            
            # Create dense frequency array for smooth curve
            interp_frequencies = np.arange(freq_min, freq_max + freq_step/2, freq_step/2)
            
            # Interpolate velocities
            from scipy.interpolate import interp1d
            interp_func = interp1d(frequencies, velocities, kind='cubic', 
                                 bounds_error=False, fill_value='extrapolate')
            interp_velocities = interp_func(interp_frequencies)
            
            # Remove old curve if it exists
            if self.curve_line is not None:
                self.dispersion_plot.removeItem(self.curve_line)
            
            # Get color for current mode
            current_color = self.mode_colors.get(self.current_mode, 'red')
            
            # Plot interpolated curve with mode-specific color
            self.curve_line = pg.PlotDataItem(
                x=interp_frequencies, y=interp_velocities,
                pen=pg.mkPen(color=current_color, width=3)
            )
            self.dispersion_plot.addItem(self.curve_line)
            
            # Store curve for current window in memory with error information
            if self.current_window_key:
                # Calculate errors for picked points (handle both old and new formats)
                picked_frequencies = []
                picked_velocities = []
                for point_data in self.picked_points:
                    if isinstance(point_data, dict):
                        picked_frequencies.append(point_data['frequency'])
                        picked_velocities.append(point_data['velocity'])
                    else:
                        picked_frequencies.append(point_data[0])  # Old format compatibility
                        picked_velocities.append(point_data[1])
                
                picked_errors = self.calculatePickErrors(picked_frequencies, picked_velocities)
                
                # Store picked points with errors
                picked_points_with_errors = []
                for i, point_data in enumerate(self.picked_points):
                    if isinstance(point_data, dict):
                        picked_points_with_errors.append({
                            'frequency': point_data['frequency'],
                            'velocity': point_data['velocity'],
                            'mode': point_data.get('mode', 0),
                            'error': picked_errors[i] if i < len(picked_errors) else 5.0
                        })
                    else:
                        # Old format compatibility
                        picked_points_with_errors.append({
                            'frequency': point_data[0],
                            'velocity': point_data[1],
                            'mode': 0,  # Default to fundamental mode
                            'error': picked_errors[i] if i < len(picked_errors) else 5.0
                        })
                
                self.window_curves[self.current_window_key] = {
                    'picked_points': self.picked_points.copy(),
                    'picked_points_with_errors': picked_points_with_errors,
                    'frequencies': interp_frequencies,
                    'velocities': interp_velocities,
                    'interpolated': True
                }
                print(f"Saved interpolated curve for {self.current_window_key}")
                self.updateWindowCurvesStatus()
            
            # Store curve for current analysis (use current stacked ID or subset)
            if hasattr(self, 'current_stacked_id') and self.current_stacked_id:
                curve_key = f'stacked_{self.current_stacked_id}'
            else:
                # Fallback to a generic key if no specific analysis is selected
                curve_key = 'current_analysis'
                
            self.extracted_curves[curve_key] = {
                'frequencies': interp_frequencies,
                'velocities': interp_velocities,
                'picked_points': self.picked_points.copy(),
                'interpolated': True
            }
            
            # Enable export if we have curves (either extracted or window curves)
            if self.extracted_curves or self.window_curves:
                self.export_curves_button.setEnabled(True)
            
            QMessageBox.information(self, "Curve Interpolated", 
                                   f"Interpolated curve created with {len(interp_frequencies)} points.\n"
                                   f"Frequency range: {freq_min:.1f} - {freq_max:.1f} Hz\n"
                                   f"Based on {len(self.picked_points)} picked points.")
            
            # Update pseudo-section plot with new interpolated curve
            self.updatePseudoSection()
            
        except Exception as e:
            QMessageBox.critical(self, "Interpolation Error", f"Error interpolating curve:\n{e}")
    
    def updatePseudoSection(self):
        """Update the pseudo-section plot with phase velocity picks from all windows"""
        try:
            # Clear existing plot and colorbar
            self.pseudosection_plot.clear()
            self._removePseudoSectionColorbar()
            
            # Get the selected display mode from pseudo-section dropdown
            display_mode = self.mode_display_selector.currentIndex() if hasattr(self, 'mode_display_selector') else 0
            print(f"DEBUG: Updating pseudo-section for display mode M{display_mode}")
            
            # Collect all window data with picks
            window_data = []
            all_frequencies = []
            all_wavelengths = []
            
            for window_key, curve_data in self.window_curves.items():
                if not curve_data:
                    continue
                    
                # Extract window x_mid from window_key (e.g., "window_10.0")
                try:
                    # Parse x_mid directly from key
                    x_mid_str = window_key.split('_')[1]
                    x_mid = float(x_mid_str)
                    
                    # Prefer interpolated curve data if available, otherwise use picked points
                    if ('frequencies' in curve_data and 'velocities' in curve_data and 
                        'interpolated' in curve_data and curve_data['interpolated']):
                        # Use interpolated curve data for smoother pseudo-section
                        frequencies = curve_data['frequencies']
                        velocities = curve_data['velocities']
                        
                        for freq, velocity in zip(frequencies, velocities):
                            if freq > 0:  # Avoid division by zero
                                wavelength = velocity / freq
                                window_data.append({
                                    'x_mid': x_mid,
                                    'frequency': freq,
                                    'velocity': velocity,
                                    'wavelength': wavelength
                                })
                                all_frequencies.append(freq)
                                all_wavelengths.append(wavelength)
                                
                    elif 'picked_points' in curve_data and curve_data['picked_points']:
                        # Fall back to individual picked points if no interpolated curve
                        picked_points = curve_data['picked_points']
                        
                        for point_data in picked_points:
                            # Handle both old format (freq, vel) and new format {'frequency': x, 'velocity': y, 'mode': m}
                            if isinstance(point_data, dict):
                                freq = point_data['frequency']
                                velocity = point_data['velocity']
                                mode = point_data.get('mode', 0)
                            else:
                                # Old format compatibility
                                freq, velocity = point_data
                                mode = 0
                            
                            # Filter by display mode - only show points of the selected mode
                            if mode != display_mode:
                                continue
                            
                            # Calculate wavelength = velocity / frequency
                            if freq > 0:  # Avoid division by zero
                                wavelength = velocity / freq
                                window_data.append({
                                    'x_mid': x_mid,
                                    'frequency': freq,
                                    'velocity': velocity,
                                    'wavelength': wavelength,
                                    'mode': mode
                                })
                                all_frequencies.append(freq)
                                all_wavelengths.append(wavelength)
                except (ValueError, IndexError):
                    print(f"Warning: Could not parse window key: {window_key}")
                    continue
            
            if not window_data:
                # No data to plot
                self._removePseudoSectionColorbar()
                return
            
            # Group data by window for plotting curves
            windows_dict = {}
            all_velocities = [d['velocity'] for d in window_data]
            
            for d in window_data:
                x_mid = d['x_mid']
                if x_mid not in windows_dict:
                    windows_dict[x_mid] = {'wavelengths': [], 'velocities': [], 'frequencies': []}
                windows_dict[x_mid]['wavelengths'].append(d['wavelength'])
                windows_dict[x_mid]['velocities'].append(d['velocity'])
                windows_dict[x_mid]['frequencies'].append(d['frequency'])
            
            # Create color map based on velocity range across all windows
            min_vel = min(all_velocities)
            max_vel = max(all_velocities)
            vel_range = max_vel - min_vel if max_vel > min_vel else 1
            
            # Import colormap
            import matplotlib.cm as cm
            colormap = cm.get_cmap('viridis')
            
            # Plot each window's dispersion curve
            for x_mid, data in windows_dict.items():
                wavelengths = np.array(data['wavelengths'])
                velocities = np.array(data['velocities'])
                frequencies = np.array(data['frequencies'])
                
                # Sort by wavelength for proper curve plotting
                sort_idx = np.argsort(wavelengths)
                wavelengths_sorted = wavelengths[sort_idx]
                velocities_sorted = velocities[sort_idx]
                
                # Create x coordinates (all same x_mid for this window)
                x_coords = np.full_like(wavelengths_sorted, x_mid)
                
                # Plot as scatter points colored by velocity
                for i, (x, wl, vel) in enumerate(zip(x_coords, wavelengths_sorted, velocities_sorted)):
                    # Normalize velocity for color
                    norm_vel = (vel - min_vel) / vel_range
                    color = colormap(norm_vel)
                    r, g, b, a = [int(c * 255) for c in color]
                    
                    scatter = pg.ScatterPlotItem(
                        x=[x], y=[wl],
                        brush=(r, g, b, a),
                        pen=pg.mkPen(color='black', width=1),
                        size=8,
                        symbol='o'
                    )
                    self.pseudosection_plot.addItem(scatter)
                
                # If we have enough points, also draw a line connecting them
                if len(wavelengths_sorted) > 1:
                    # Calculate average velocity for line color
                    avg_vel = np.mean(velocities_sorted)
                    norm_avg_vel = (avg_vel - min_vel) / vel_range
                    line_color = colormap(norm_avg_vel)
                    r, g, b, a = [int(c * 255) for c in line_color]
                    
                    line = pg.PlotDataItem(
                        x=x_coords, y=wavelengths_sorted,
                        pen=pg.mkPen(color=(r, g, b, int(0.7*255)), width=2),
                        connect='all'
                    )
                    self.pseudosection_plot.addItem(line)
            
            # Set plot title and labels  
            num_windows = len(windows_dict)
            total_points = len(window_data)
            
            # Add colorbar for velocity scale
            if min_vel != max_vel:
                self._addPseudoSectionColorbar(min_vel, max_vel)
            else:
                self._removePseudoSectionColorbar()
            
            # Auto-range to fit data
            self.pseudosection_plot.autoRange()
            
            # Set zoom limits to prevent excessive zoom-out
            if window_data:
                all_x_positions = [d['x_mid'] for d in window_data]
                min_x, max_x = min(all_x_positions), max(all_x_positions)
                min_wl, max_wl = min(all_wavelengths), max(all_wavelengths)
                
                x_range = max_x - min_x if max_x > min_x else 100
                wl_range = max_wl - min_wl if max_wl > min_wl else 10
                
                x_margin = max(x_range * 0.2, 10)
                wl_margin = max(wl_range * 0.2, 1)
                
                self.pseudosection_plot.getViewBox().setLimits(
                    xMin=min_x - x_margin, xMax=max_x + x_margin,
                    yMin=min_wl - wl_margin, yMax=max_wl + wl_margin
                )
            
        except Exception as e:
            print(f"Error updating pseudo-section: {e}")
    
    def clearPicking(self):
        """Clear all picked points and curves"""
        # Remove all point items from plot
        for item in self.picked_point_items:
            if item is not None:
                self.dispersion_plot.removeItem(item)
        
        # Remove curve if it exists
        if self.curve_line is not None:
            self.dispersion_plot.removeItem(self.curve_line)
            self.curve_line = None
        
        # Clear data
        self.picked_points = []
        self.picked_point_items = []
        
        # Hide and disable error bars
        self.hideErrorBars()
        self.show_errors_button.setEnabled(False)
        self.show_errors_button.setChecked(False)
        self.show_errors_button.setText("Show Error Bars")
        self.show_error_bars = False
        
        # Disable buttons
        self.interpolate_button.setEnabled(False)
        self.clear_picking_button.setEnabled(False)
        
        # Remove curve from current window memory
        if self.current_window_key and self.current_window_key in self.window_curves:
            del self.window_curves[self.current_window_key]
            print(f"Cleared saved curve for {self.current_window_key}")
            self.updateWindowCurvesStatus()
        
        # Remove curve from extracted curves for current analysis
        if hasattr(self, 'current_stacked_id') and self.current_stacked_id:
            curve_key = f'stacked_{self.current_stacked_id}'
            if curve_key in self.extracted_curves:
                del self.extracted_curves[curve_key]
        else:
            # Fallback to generic key
            curve_key = 'current_analysis'
            if curve_key in self.extracted_curves:
                del self.extracted_curves[curve_key]
        
        # Disable export if no curves left
        if not self.extracted_curves and not self.window_curves:
            self.export_curves_button.setEnabled(False)
        
        # Update pseudo-section plot after clearing
        self.updatePseudoSection()
    
    def toggleErrorBars(self):
        """Toggle display of error bars on picked points"""
        self.show_error_bars = self.show_errors_button.isChecked()
        
        if self.show_error_bars:
            self.show_errors_button.setText("Hide Error Bars")
            self.showErrorBars()
        else:
            self.show_errors_button.setText("Show Error Bars")
            self.hideErrorBars()
    
    def showErrorBars(self):
        """Display error bars for current picked points"""
        # Clear existing error bars
        self.hideErrorBars()
        
        if not self.picked_points:
            return
            
        try:
            # Extract frequencies, velocities, and modes (handle both old and new formats)
            frequencies = []
            velocities = []
            modes = []
            for point_data in self.picked_points:
                if isinstance(point_data, dict):
                    frequencies.append(point_data['frequency'])
                    velocities.append(point_data['velocity'])
                    modes.append(point_data.get('mode', 0))  # Default to mode 0 if not specified
                else:
                    frequencies.append(point_data[0])  # Old format compatibility
                    velocities.append(point_data[1])
                    modes.append(0)  # Default to mode 0 for old format
            
            # Calculate errors for current picks
            errors = self.calculatePickErrors(frequencies, velocities)
            
            # Create error bar items
            for i, (freq, vel, error, mode) in enumerate(zip(frequencies, velocities, errors, modes)):
                # Get color for this mode
                error_color = self.mode_colors.get(mode, 'red')
                
                # Create vertical error bar using PlotDataItem
                error_bar = pg.PlotDataItem(
                    x=[freq, freq], 
                    y=[vel - error, vel + error],
                    pen=pg.mkPen(color=error_color, width=2),
                    connect='all'
                )
                self.dispersion_plot.addItem(error_bar)
                self.error_bar_items.append(error_bar)
                
                # Add horizontal caps at the ends of error bars
                cap_width = (max(frequencies) - min(frequencies)) * 0.01 if len(frequencies) > 1 else 1.0
                
                # Bottom cap
                bottom_cap = pg.PlotDataItem(
                    x=[freq - cap_width, freq + cap_width], 
                    y=[vel - error, vel - error],
                    pen=pg.mkPen(color=error_color, width=2),
                    connect='all'
                )
                self.dispersion_plot.addItem(bottom_cap)
                self.error_bar_items.append(bottom_cap)
                
                # Top cap
                top_cap = pg.PlotDataItem(
                    x=[freq - cap_width, freq + cap_width], 
                    y=[vel + error, vel + error],
                    pen=pg.mkPen(color=error_color, width=2),
                    connect='all'
                )
                self.dispersion_plot.addItem(top_cap)
                self.error_bar_items.append(top_cap)
                
        except Exception as e:
            print(f"Error displaying error bars: {e}")
    
    def hideErrorBars(self):
        """Hide all error bar items"""
        for item in self.error_bar_items:
            if item is not None:
                self.dispersion_plot.removeItem(item)
        self.error_bar_items = []
    
    def exportCurves(self):
        """Export extracted dispersion curves to mode-specific .pvc files"""
        if not self.extracted_curves and not self.window_curves:
            QMessageBox.warning(self, "No Curves", "No dispersion curves have been extracted yet.")
            return
        
        # Get save directory
        from PyQt5.QtWidgets import QFileDialog
        save_dir = QFileDialog.getExistingDirectory(
            self, "Select Directory to Save .pvc Files", 
            ""
        )
        
        if not save_dir:
            return
        
        try:
            import csv
            import os
            
            files_saved = []
            
            # Export window curves (picked curves for each window) grouped by mode
            for window_key, curve_data in self.window_curves.items():
                # Extract xmid from window key (e.g., 'window_2.4' -> '2.4')
                try:
                    xmid_str = window_key.replace('window_', '')
                    xmid = float(xmid_str)
                except (ValueError, AttributeError):
                    print(f"Warning: Could not extract xmid from window key {window_key}")
                    continue
                
                # Group points by mode
                mode_data = {}  # mode_number -> list of points
                
                # Check for picked points with error and mode information
                if 'picked_points_with_errors' in curve_data:
                    for point_data in curve_data['picked_points_with_errors']:
                        mode = point_data.get('mode', 0)
                        if mode not in mode_data:
                            mode_data[mode] = []
                        mode_data[mode].append({
                            'frequency': point_data['frequency'],
                            'velocity': point_data['velocity'],
                            'error': point_data.get('error', 5.0)
                        })
                
                # Fallback: check for regular picked points
                elif 'picked_points' in curve_data:
                    # Handle both old and new data formats
                    frequencies = []
                    velocities = []
                    
                    for point_data in curve_data['picked_points']:
                        if isinstance(point_data, dict):
                            frequencies.append(point_data['frequency'])
                            velocities.append(point_data['velocity'])
                            mode = point_data.get('mode', 0)
                        else:
                            frequencies.append(point_data[0])  # Old format
                            velocities.append(point_data[1])
                            mode = 0  # Default to fundamental mode
                        
                        if mode not in mode_data:
                            mode_data[mode] = []
                        mode_data[mode].append({
                            'frequency': frequencies[-1],
                            'velocity': velocities[-1],
                            'error': 5.0  # Default error
                        })
                    
                    # Calculate errors for all points
                    if frequencies:
                        errors = self.calculatePickErrors(frequencies, velocities)
                        for mode_points in mode_data.values():
                            for i, point in enumerate(mode_points):
                                if i < len(errors):
                                    point['error'] = errors[i]
                
                # Save separate file for each mode
                for mode, points in mode_data.items():
                    if not points:
                        continue
                    
                    # Create filename: {xmid}.M{mode}.pvc
                    filename = f"{xmid:.1f}.M{mode}.pvc"
                    file_path = os.path.join(save_dir, filename)
                    
                    # Sort points by frequency
                    points.sort(key=lambda p: p['frequency'])
                    
                    # Write CSV file (no headers)
                    with open(file_path, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        
                        # Write data points only (no header)
                        for point in points:
                            writer.writerow([point['frequency'], point['velocity'], point['error']])
                    
                    files_saved.append(filename)
                    print(f"Saved {len(points)} points for mode M{mode} at xmid={xmid:.1f} to {filename}")
            
            # Show success message
            if files_saved:
                files_list = '\n'.join(files_saved)
                QMessageBox.information(self, "Export Successful", 
                                       f"Exported {len(files_saved)} .pvc files to:\n{save_dir}\n\n"
                                       f"Files saved:\n{files_list}")
            else:
                QMessageBox.warning(self, "No Files Exported", 
                                   "No valid curve data found to export.")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting curves:\n{e}")
    
    def _addDispersionColorbar(self, img_item, data):
        """Add colorbar to dispersion plot"""
        # Remove existing colorbar if present
        self._removeDispersionColorbar()
        
        # Create new colorbar
        try:
            # Get data range for colorbar
            data_min, data_max = np.nanmin(data), np.nanmax(data)
            if np.isfinite(data_min) and np.isfinite(data_max) and data_max > data_min:
                # Create ColorBarItem and add to plot layout (like core module)
                self.dispersion_colorbar = pg.ColorBarItem(
                    colorMap=img_item.getColorMap(),
                    values=(data_min, data_max),
                    label='',  # Remove default label
                    interactive=False
                )
                
                # Create separate title label positioned to the right
                self.dispersion_title_label = pg.LabelItem('Amplitude')
                self.dispersion_title_label.setAngle(90)  # Rotate 90° clockwise
                
                # Add to the plot's layout grid (like core module)
                self.dispersion_plot.plotItem.layout.setColumnFixedWidth(4, 5)  # space between plot and colorbar
                self.dispersion_plot.plotItem.layout.addItem(self.dispersion_colorbar, 2, 5)
                # Add title label to separate column (close to colorbar)
                self.dispersion_plot.plotItem.layout.setColumnFixedWidth(6, 10)  # Very small width for title
                self.dispersion_plot.plotItem.layout.addItem(self.dispersion_title_label, 2, 6)
        except Exception as e:
            print(f"Warning: Could not create dispersion colorbar: {e}")
            self.dispersion_colorbar = None
    
    def _addSpectrumColorbar(self, img_item, data):
        """Add colorbar to spectrum plot"""
        # Remove existing colorbar if present
        self._removeSpectrumColorbar()
        
        # Create new colorbar
        try:
            # Get data range for colorbar
            data_min, data_max = np.nanmin(data), np.nanmax(data)
            if np.isfinite(data_min) and np.isfinite(data_max) and data_max > data_min:
                # Create ColorBarItem and add to plot layout (like core module)
                self.spectrum_colorbar = pg.ColorBarItem(
                    colorMap=img_item.getColorMap(),
                    values=(data_min, data_max),
                    label='',  # Remove default label
                    interactive=False
                )
                
                # Create separate title label positioned to the right
                self.spectrum_title_label = pg.LabelItem('Spectrum Amplitude')
                self.spectrum_title_label.setAngle(90)  # Rotate 90° clockwise
                
                # Add to the plot's layout grid (like core module)
                self.spectrum_plot.plotItem.layout.setColumnFixedWidth(4, 5)  # space between plot and colorbar
                self.spectrum_plot.plotItem.layout.addItem(self.spectrum_colorbar, 2, 5)
                # Add title label to separate column (close to colorbar)
                self.spectrum_plot.plotItem.layout.setColumnFixedWidth(6, 10)  # Very small width for title
                self.spectrum_plot.plotItem.layout.addItem(self.spectrum_title_label, 2, 6)
        except Exception as e:
            print(f"Warning: Could not create spectrum colorbar: {e}")
            self.spectrum_colorbar = None
    
    def _addSeismogramColorbar(self, img_item, data):
        """Add colorbar to seismogram plot (only in image mode)"""
        # Remove existing colorbar if present
        self._removeSeismogramColorbar()
        
        # Only add colorbar in image mode
        if hasattr(self, 'display_mode_combo') and self.display_mode_combo.currentText() == "Image":
            try:
                # Get data range for colorbar
                data_min, data_max = np.nanmin(data), np.nanmax(data)
                if np.isfinite(data_min) and np.isfinite(data_max) and data_max > data_min:
                    # Create ColorBarItem and add to plot layout (like core module)
                    self.seismogram_colorbar = pg.ColorBarItem(
                        colorMap=img_item.getColorMap(),
                        values=(data_min, data_max),
                        label='',  # Remove default label
                        interactive=False
                    )
                    
                    # Create separate title label positioned to the right
                    self.seismogram_title_label = pg.LabelItem('Amplitude')
                    self.seismogram_title_label.setAngle(90)  # Rotate 90° clockwise
                    
                    # Add to the plot's layout grid (like core module)
                    self.wiggle_plot.plotItem.layout.setColumnFixedWidth(4, 5)  # space between plot and colorbar
                    self.wiggle_plot.plotItem.layout.addItem(self.seismogram_colorbar, 2, 5)
                    # Add title label to separate column (close to colorbar)
                    self.wiggle_plot.plotItem.layout.setColumnFixedWidth(6, 10)  # Very small width for title
                    self.wiggle_plot.plotItem.layout.addItem(self.seismogram_title_label, 2, 6)
            except Exception as e:
                print(f"Warning: Could not create seismogram colorbar: {e}")
                self.seismogram_colorbar = None

    def _removeSeismogramColorbar(self):
        """Remove seismogram colorbar (used when switching to wiggle mode)"""
        if self.seismogram_colorbar is not None:
            # Remove from plot layout (like core module)
            try:
                self.wiggle_plot.plotItem.layout.removeItem(self.seismogram_colorbar)
            except:
                pass  # Item might not be in layout
            self.seismogram_colorbar = None
        
        # Also remove title label if it exists
        if hasattr(self, 'seismogram_title_label') and self.seismogram_title_label is not None:
            try:
                self.wiggle_plot.plotItem.layout.removeItem(self.seismogram_title_label)
            except:
                pass  # Item might not be in layout
            self.seismogram_title_label = None

    def _removeDispersionColorbar(self):
        """Remove dispersion colorbar"""
        if self.dispersion_colorbar is not None:
            # Remove from plot layout (like core module)
            try:
                self.dispersion_plot.plotItem.layout.removeItem(self.dispersion_colorbar)
            except:
                pass  # Item might not be in layout
            self.dispersion_colorbar = None
        
        # Also remove title label if it exists
        if hasattr(self, 'dispersion_title_label') and self.dispersion_title_label is not None:
            try:
                self.dispersion_plot.plotItem.layout.removeItem(self.dispersion_title_label)
            except:
                pass  # Item might not be in layout
            self.dispersion_title_label = None

    def _removeSpectrumColorbar(self):
        """Remove spectrum colorbar"""
        if self.spectrum_colorbar is not None:
            # Remove from plot layout (like core module)
            try:
                self.spectrum_plot.plotItem.layout.removeItem(self.spectrum_colorbar)
            except:
                pass  # Item might not be in layout
            self.spectrum_colorbar = None
        
        # Also remove title label if it exists
        if hasattr(self, 'spectrum_title_label') and self.spectrum_title_label is not None:
            try:
                self.spectrum_plot.plotItem.layout.removeItem(self.spectrum_title_label)
            except:
                pass  # Item might not be in layout
            self.spectrum_title_label = None

    def _addPseudoSectionColorbar(self, min_vel, max_vel):
        """Add colorbar to pseudo-section plot"""
        # Remove existing colorbar if present
        self._removePseudoSectionColorbar()
        
        # Create new colorbar
        try:
            if np.isfinite(min_vel) and np.isfinite(max_vel) and max_vel > min_vel:
                # Get the viridis colormap
                colormap = pg.colormap.get('viridis', source='matplotlib')
                
                # Create ColorBarItem and add to plot layout
                self.pseudosection_colorbar = pg.ColorBarItem(
                    colorMap=colormap,
                    values=(min_vel, max_vel),
                    label='',  # Remove default label
                    interactive=False
                )
                
                # Create separate title label positioned to the right
                self.pseudosection_title_label = pg.LabelItem('Phase Velocity (m/s)')
                self.pseudosection_title_label.setAngle(90)  # Rotate 90° clockwise
                
                # Add to the plot's layout grid
                self.pseudosection_plot.plotItem.layout.setColumnFixedWidth(4, 5)  # space between plot and colorbar
                self.pseudosection_plot.plotItem.layout.addItem(self.pseudosection_colorbar, 2, 5)
                # Add title label to separate column (close to colorbar)
                self.pseudosection_plot.plotItem.layout.setColumnFixedWidth(6, 10)  # Very small width for title
                self.pseudosection_plot.plotItem.layout.addItem(self.pseudosection_title_label, 2, 6)
        except Exception as e:
            print(f"Warning: Could not create pseudo-section colorbar: {e}")
            self.pseudosection_colorbar = None

    def _removePseudoSectionColorbar(self):
        """Remove pseudo-section colorbar"""
        if self.pseudosection_colorbar is not None:
            # Remove from plot layout
            try:
                self.pseudosection_plot.plotItem.layout.removeItem(self.pseudosection_colorbar)
            except:
                pass  # Item might not be in layout
            self.pseudosection_colorbar = None
        
        # Also remove title label if it exists
        if hasattr(self, 'pseudosection_title_label') and self.pseudosection_title_label is not None:
            try:
                self.pseudosection_plot.plotItem.layout.removeItem(self.pseudosection_title_label)
            except:
                pass  # Item might not be in layout
            self.pseudosection_title_label = None

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop worker thread if running
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        event.accept()
