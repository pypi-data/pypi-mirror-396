#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Surface Wave Analysis Module for PyCKSTER

This module provides a dedicated interface for surface wave analysis, including:
- Dispersion curve analysis using phase shift method
- Frequency spectrum visualization
- Interactive picking and analysis tools

Copyright (C) 2025 Sylvain Pasquet
Email: sylvain.pasquet@sorbonne-universite.fr

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import sys
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QListWidget, QListWidgetItem, QLabel, QPushButton, QGroupBox,
    QFormLayout, QLineEdit, QCheckBox, QComboBox, QMessageBox,
    QProgressDialog, QDialog, QDialogButtonBox, QTextEdit, QTabWidget,
    QDoubleSpinBox, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

# Import surface wave analysis functions
from .obspy_utils import check_format
from .sw_utils import phase_shift
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
        
        # Velocity range parameters
        self.vmin_edit = QLineEdit("0")
        self.vmax_edit = QLineEdit("1500")
        self.dv_edit = QLineEdit("5")
        form_layout.addRow("Min velocity (m/s):", self.vmin_edit)
        form_layout.addRow("Max velocity (m/s):", self.vmax_edit)
        form_layout.addRow("Velocity step (m/s):", self.dv_edit)
        
        # Frequency parameters
        self.fmax_edit = QLineEdit("150")
        form_layout.addRow("Max frequency (Hz):", self.fmax_edit)
        
        # Normalization options
        self.norm_combo = QComboBox()
        self.norm_combo.addItems(["Frequencies", "Velocities", "Global", "None"])
        self.norm_combo.setCurrentText("Frequencies")
        form_layout.addRow("Normalization:", self.norm_combo)
        
        # Include elevation checkbox
        self.include_elevation_check = QCheckBox()
        self.include_elevation_check.setChecked(False)
        self.include_elevation_check.setToolTip("Include elevation (Z coordinate) in 3D distance calculation for phase shift")
        form_layout.addRow("Include elevation:", self.include_elevation_check)
        
        # Windowing parameters
        windowing_label = QLabel("Trace Windowing Parameters:")
        windowing_label.setFont(QFont("Arial", 9, QFont.Bold))
        form_layout.addRow(windowing_label)
        
        self.num_traces_edit = QLineEdit("0")
        self.num_traces_edit.setToolTip("Number of traces to use (0 = use all traces). Selected traces must all be on the same side of the shot.")
        form_layout.addRow("Number of traces (0=all):", self.num_traces_edit)
        
        self.trace_offset_edit = QLineEdit("0")
        self.trace_offset_edit.setToolTip("Offset from shot to first trace (negative = left of shot, positive = right of shot). Ensures all selected traces are on one side.")
        form_layout.addRow("Trace offset from shot:", self.trace_offset_edit)
        
        # Side preference options
        self.side_preference_combo = QComboBox()
        self.side_preference_combo.addItems(["Auto (based on offset)", "Prefer Left", "Prefer Right"])
        self.side_preference_combo.setCurrentText("Auto (based on offset)")
        self.side_preference_combo.setToolTip("Which side to prefer when selecting traces. Auto uses trace_offset sign to determine preference.")
        form_layout.addRow("Side preference:", self.side_preference_combo)
        
        self.side_restriction_combo = QComboBox()
        self.side_restriction_combo.addItems(["Use both sides", "Left side only", "Right side only"])
        self.side_restriction_combo.setCurrentText("Use both sides")
        self.side_restriction_combo.setToolTip("Restrict analysis to only one side of the shot. Shots without enough traces on the selected side will be skipped.")
        form_layout.addRow("Side restriction:", self.side_restriction_combo)
        
        # Add explanatory note
        note_label = QLabel("Note: Side restriction overrides side preference. When 'Use both sides' is selected, side preference determines which side to try first.")
        note_label.setWordWrap(True)
        note_label.setStyleSheet("QLabel { color: #666; font-size: 10px; margin: 5px 0px; }")
        form_layout.addRow(note_label)
        
        layout.addLayout(form_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def getParameters(self):
        """Return the analysis parameters"""
        try:
            num_traces = int(self.num_traces_edit.text())
            trace_offset = int(self.trace_offset_edit.text())
            
            # Validate parameters
            if num_traces < 0:
                raise ValueError("Number of traces must be >= 0")
                
            return {
                'vmin': float(self.vmin_edit.text()),
                'vmax': float(self.vmax_edit.text()),
                'dv': float(self.dv_edit.text()),
                'fmax': float(self.fmax_edit.text()),
                'normalization': self.norm_combo.currentText(),
                'include_elevation': self.include_elevation_check.isChecked(),
                'num_traces': num_traces,
                'trace_offset': trace_offset,
                'side_preference': self.side_preference_combo.currentText(),
                'side_restriction': self.side_restriction_combo.currentText()
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
                
                # Perform phase shift analysis using calculated distances
                fs, vs, FV = phase_shift(
                    XT_sorted, si, distances_sorted,
                    self.parameters['vmin'],
                    self.parameters['vmax'],
                    self.parameters['dv'],
                    self.parameters['fmax'],
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


class SurfaceWaveAnalysisWindow(QMainWindow):
    """Main window for surface wave analysis"""
    
    def __init__(self, parent, streams, shot_positions):
        super().__init__(parent)
        self.parent_window = parent
        self.streams = streams.copy()  # Keep reference to streams
        self.shot_positions = shot_positions.copy()  # Keep reference to shot positions
        self.analysis_results = {}
        self.current_result = None  # Store current displayed result for wiggle refresh
        
        # Initialize picking-related variables
        self.picking_mode = False
        self.removal_mode = False
        self.picked_points = []  # Store (freq, velocity) tuples for curve points
        self.picked_point_items = []  # Store plot items for picked points
        self.curve_line = None
        self.current_dispersion_data = None
        self.extracted_curves = {}  # Store extracted curves for each shot
        
        self.setWindowTitle("Surface Wave Analysis")
        self.setGeometry(100, 100, 1400, 900)
        
        # Setup UI
        self.setupUI()
        
        # Populate stream list
        self.populateStreamList()
        
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
        splitter.addWidget(left_panel)
        
        # Right panel - Analysis plots
        right_panel = self.createRightPanel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 1100])
    
    def createLeftPanel(self):
        """Create left panel with stream list and controls"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title_label = QLabel("Surface Wave Analysis")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Stream list
        streams_group = QGroupBox("Available Shots")
        streams_layout = QVBoxLayout(streams_group)
        
        self.stream_list = QListWidget()
        self.stream_list.itemSelectionChanged.connect(self.onStreamSelectionChanged)
        streams_layout.addWidget(self.stream_list)
        
        layout.addWidget(streams_group)
        
        # Analysis controls
        controls_group = QGroupBox("Analysis Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Parameters button
        self.params_button = QPushButton("Set Parameters")
        self.params_button.clicked.connect(self.showParametersDialog)
        controls_layout.addWidget(self.params_button)
        
        # Analyze button
        self.analyze_button = QPushButton("Run Analysis")
        self.analyze_button.clicked.connect(self.runAnalysis)
        self.analyze_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        controls_layout.addWidget(self.analyze_button)
        
        # Clear results button
        self.clear_button = QPushButton("Clear Results")
        self.clear_button.clicked.connect(self.clearResults)
        controls_layout.addWidget(self.clear_button)
        
        layout.addWidget(controls_group)
        
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
        
        # Export curves button
        self.export_curves_button = QPushButton("Export Curves")
        self.export_curves_button.clicked.connect(self.exportCurves)
        self.export_curves_button.setEnabled(False)
        picking_layout.addWidget(self.export_curves_button)
        
        layout.addWidget(picking_group)
        
        # Current parameters display
        params_group = QGroupBox("Current Parameters")
        params_layout = QVBoxLayout(params_group)
        
        self.params_text = QTextEdit()
        self.params_text.setMaximumHeight(120)
        self.params_text.setReadOnly(True)
        params_layout.addWidget(self.params_text)
        
        layout.addWidget(params_group)
        
        # Set default parameters
        self.current_parameters = {
            'vmin': 100, 'vmax': 800, 'dv': 5, 'fmax': 100,
            'normalization': 'Frequencies', 'include_elevation': False,
            'num_traces': 0, 'trace_offset': 0
        }
        self.updateParametersDisplay()
        
        # Add stretch
        layout.addStretch()
        
        return panel
    
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
        
        # Dispersion plot widget with colorbar layout
        dispersion_plot_widget = QWidget()
        dispersion_plot_layout = QHBoxLayout(dispersion_plot_widget)
        dispersion_plot_layout.setContentsMargins(0, 0, 0, 0)
        
        self.dispersion_plot = pg.PlotWidget()
        self.dispersion_plot.setBackground('w')
        
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
        
        # Spectrum plot widget with colorbar layout
        spectrum_plot_widget = QWidget()
        spectrum_plot_layout = QHBoxLayout(spectrum_plot_widget)
        spectrum_plot_layout.setContentsMargins(0, 0, 0, 0)
        
        self.spectrum_plot = pg.PlotWidget()
        self.spectrum_plot.setBackground('w')
        
        # Set margins to prevent axis labels from being cut off
        self.spectrum_plot.getPlotItem().setContentsMargins(10, 10, 10, 10)  # left, top, right, bottom margins
        
        # Show top and right axes without labels
        self.spectrum_plot.showAxis('top')
        self.spectrum_plot.showAxis('right')
        self.spectrum_plot.getAxis('top').setStyle(showValues=False)
        self.spectrum_plot.getAxis('right').setStyle(showValues=False)
        self.spectrum_plot.getAxis('top').setLabel('')
        self.spectrum_plot.getAxis('right').setLabel('')
        self.spectrum_plot.setLabel('left', 'X Coordinate', 'm')
        self.spectrum_plot.setLabel('bottom', 'Frequency', 'Hz')
        self.spectrum_plot.showAxis('top')
        spectrum_plot_layout.addWidget(self.spectrum_plot)
        
        # Initialize spectrum colorbar (will be added when plotting)
        self.spectrum_colorbar = None
        
        spectrum_tab_layout.addWidget(spectrum_plot_widget)
        
        self.data_tabs.addTab(spectrum_tab, "Frequency Spectrum")
        
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
        self.colormap_combo.setCurrentText("Greys")
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
        
        # Seismogram plot widget with colorbar layout
        seismogram_plot_widget = QWidget()
        seismogram_plot_layout = QHBoxLayout(seismogram_plot_widget)
        seismogram_plot_layout.setContentsMargins(0, 0, 0, 0)
        
        self.wiggle_plot = pg.PlotWidget()
        self.wiggle_plot.setBackground('w')
        
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
        self.wiggle_plot.setLabel('bottom', 'Distance', 'm')
        self.wiggle_plot.showAxis('top')
        # Set reverse Y axis for seismic convention (time increases downward)
        self.wiggle_plot.getViewBox().invertY(True)
        seismogram_plot_layout.addWidget(self.wiggle_plot)
        
        # Initialize seismogram colorbar (will be added when plotting in image mode)
        self.seismogram_colorbar = None
        
        wiggle_tab_layout.addWidget(seismogram_plot_widget)
        
        self.data_tabs.addTab(wiggle_tab, "Seismogram")
        
        # Spatial Layout tab
        spatial_tab = QWidget()
        spatial_tab_layout = QVBoxLayout(spatial_tab)
        
        # Spatial plot widget
        self.spatial_plot = pg.PlotWidget()
        self.spatial_plot.setBackground('w')
        
        # Set margins to prevent axis labels from being cut off
        self.spatial_plot.getPlotItem().setContentsMargins(10, 10, 10, 10)  # left, top, right, bottom margins
        
        # Show top and right axes without labels
        self.spatial_plot.showAxis('top')
        self.spatial_plot.showAxis('right')
        self.spatial_plot.getAxis('top').setStyle(showValues=False)
        self.spatial_plot.getAxis('right').setStyle(showValues=False)
        self.spatial_plot.getAxis('top').setLabel('')
        self.spatial_plot.getAxis('right').setLabel('')
        self.spatial_plot.setLabel('left', 'Y Coordinate', 'm')
        self.spatial_plot.setLabel('bottom', 'X Coordinate', 'm')
        spatial_tab_layout.addWidget(self.spatial_plot)
        
        self.data_tabs.addTab(spatial_tab, "Spatial Layout")
        
        v_splitter.addWidget(middle_widget)
        
        # Set splitter proportions (dispersion plot takes more space now)
        v_splitter.setSizes([700, 300])  # Dispersion: 70%, Tabs: 30%
        
        return panel
    
    def populateStreamList(self):
        """Populate the stream list with available shots"""
        self.stream_list.clear()
        
        for i, stream in enumerate(self.streams):
            # Create item text
            if i < len(self.shot_positions):
                item_text = f"Shot {i+1} (Pos: {self.shot_positions[i]:.1f} m) - {len(stream)} traces"
            else:
                item_text = f"Shot {i+1} - {len(stream)} traces"
            
            # Add item
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, i)  # Store shot index
            self.stream_list.addItem(item)
    
    def onStreamSelectionChanged(self):
        """Handle stream selection change"""
        current_item = self.stream_list.currentItem()
        if current_item is not None:
            shot_index = current_item.data(Qt.UserRole)
            self.displayShotAnalysis(shot_index)
    
    def showParametersDialog(self):
        """Show parameters dialog"""
        dialog = SurfaceWaveParametersDialog(self)
        
        # Set current parameters in dialog
        dialog.vmin_edit.setText(str(self.current_parameters['vmin']))
        dialog.vmax_edit.setText(str(self.current_parameters['vmax']))
        dialog.dv_edit.setText(str(self.current_parameters['dv']))
        dialog.fmax_edit.setText(str(self.current_parameters['fmax']))
        dialog.norm_combo.setCurrentText(self.current_parameters['normalization'])
        dialog.include_elevation_check.setChecked(self.current_parameters['include_elevation'])
        dialog.num_traces_edit.setText(str(self.current_parameters['num_traces']))
        dialog.trace_offset_edit.setText(str(self.current_parameters['trace_offset']))
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.current_parameters = dialog.getParameters()
                self.updateParametersDisplay()
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Parameters", str(e))
    
    def updateParametersDisplay(self):
        """Update the parameters display"""
        # Format windowing info
        windowing_info = ""
        if self.current_parameters['num_traces'] > 0:
            windowing_info = f"\nTrace windowing: {self.current_parameters['num_traces']} traces, offset: {self.current_parameters['trace_offset']}"
        else:
            windowing_info = "\nTrace windowing: Use all traces"
            
        params_text = f"""Velocity range: {self.current_parameters['vmin']}-{self.current_parameters['vmax']} m/s
Velocity step: {self.current_parameters['dv']} m/s
Max frequency: {self.current_parameters['fmax']} Hz
Normalization: {self.current_parameters['normalization']}
Include elevation: {self.current_parameters['include_elevation']}{windowing_info}"""
        
        self.params_text.setPlainText(params_text)
    
    def runAnalysis(self):
        """Run surface wave analysis on all shots"""
        if not self.streams:
            QMessageBox.warning(self, "No Data", "No seismic data available for analysis.")
            return
        
        # Disable analysis button during computation
        self.analyze_button.setEnabled(False)
        self.analyze_button.setText("Running...")
        
        # Stop any existing worker thread
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        # Clear previous results before starting new analysis
        self.analysis_results = {}
        
        # Remove colorbars before clearing plots
        self._removeDispersionColorbar()
        self._removeSpectrumColorbar()
        self._removeSeismogramColorbar()
        
        self.dispersion_plot.clear()
        self.spectrum_plot.clear()
        self.wiggle_plot.clear()
        
        # Reset view limits before new analysis
        self.dispersion_plot.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)
        self.spectrum_plot.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)
        
        # Show progress dialog
        progress = QProgressDialog("Running surface wave analysis...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        # Create and start worker thread
        self.worker = SurfaceWaveWorker(self.streams, self.shot_positions, self.current_parameters)
        self.worker.progress.connect(progress.setValue)
        self.worker.finished.connect(self.onAnalysisFinished)
        self.worker.error.connect(self.onAnalysisError)
        self.worker.finished.connect(progress.close)
        self.worker.error.connect(progress.close)
        
        # Re-enable button when finished
        self.worker.finished.connect(self.resetAnalysisButton)
        self.worker.error.connect(self.resetAnalysisButton)
        
        # Handle progress dialog cancellation
        def onProgressCanceled():
            if hasattr(self, 'worker') and self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait()
            self.resetAnalysisButton()
        
        progress.canceled.connect(onProgressCanceled)
        
        self.worker.start()
    
    def resetAnalysisButton(self):
        """Reset the analysis button to its normal state"""
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("Run Analysis")
    
    def onAnalysisFinished(self, results):
        """Handle analysis completion"""
        try:
            # Check for skipped shots information
            skipped_shots = results.pop('_skipped_shots', [])
            
            # Store new results
            self.analysis_results = results
            
            # Get currently selected shot index before showing message
            current_row = self.stream_list.currentRow()
            
            # Create completion message
            num_processed = len(results)
            num_skipped = len(skipped_shots)
            total_shots = num_processed + num_skipped
            
            message = f"Surface wave analysis completed for {num_processed} shots."
            if skipped_shots:
                message += f"\n\n{num_skipped} shots were skipped due to windowing constraints:"
                for shot_num, reason in skipped_shots:
                    message += f"\n- Shot {shot_num}: {reason}"
                message += f"\n\nConsider adjusting the trace windowing parameters if needed."
            
            QMessageBox.information(self, "Analysis Complete", message)
            
            # Refresh display with new results
            if results and self.stream_list.count() > 0:
                if current_row >= 0:
                    # If a shot was previously selected, display that shot with new results
                    self.stream_list.setCurrentRow(current_row)
                    self.displayShotAnalysis(current_row)
                else:
                    # Otherwise display first shot
                    self.stream_list.setCurrentRow(0)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error Processing Results", f"Error processing analysis results:\n{e}")
    
    def onAnalysisError(self, error_message):
        """Handle analysis error"""
        QMessageBox.critical(self, "Analysis Error", f"Error during analysis:\n{error_message}")
        # Clear any partial results
        self.analysis_results = {}
        
        # Remove colorbars before clearing plots
        self._removeDispersionColorbar()
        self._removeSpectrumColorbar()
        
        self.dispersion_plot.clear()
        self.spectrum_plot.clear()
        # Reset button state is handled by the signal connection in runAnalysis
    
    def displayShotAnalysis(self, shot_index):
        """Display analysis results for selected shot"""
        shot_key = f'shot_{shot_index}'
        
        if shot_key not in self.analysis_results:
            # Clear plots if no results
            self._removeDispersionColorbar()
            self._removeSpectrumColorbar()
            self.dispersion_plot.clear()
            self.spectrum_plot.clear()
            return
        
        result = self.analysis_results[shot_key]
        
        try:
            # Plot dispersion image
            self.plotDispersionImage(result)
            
            # Plot spectrum
            self.plotSpectrum(result)
            
            # Plot seismogram traces
            self.plotSeismogram(result)
            
            # Plot spatial layout
            self.plotSpatialLayout(result)
        except Exception as e:
            QMessageBox.warning(self, "Display Error", f"Error displaying analysis for shot {shot_index + 1}:\n{e}")
            # Clear plots on error
            self._removeDispersionColorbar()
            self._removeSpectrumColorbar()
            self._removeSeismogramColorbar()
            self.dispersion_plot.clear()
            self.spectrum_plot.clear()
            self.wiggle_plot.clear()
            self.spatial_plot.clear()
    
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
        norm = self.current_parameters['normalization']
        
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
        img_item = createImageItem(FV_plot**2, frequencies, velocities, 'viridis')
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
        
        # Check if there's an extracted curve for this shot and display it
        current_row = self.stream_list.currentRow()
        if current_row >= 0:
            shot_key = f'shot_{current_row}'
            if shot_key in self.extracted_curves:
                curve_data = self.extracted_curves[shot_key]
                
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
    
    def plotSpatialLayout(self, result):
        """Plot spatial layout of sources and receivers"""
        # This will be a scatter plot showing X,Y coordinates
        self.spatial_plot.clear()
        
        # Get coordinates
        receiver_coords_x = result['receiver_coords_x']
        receiver_coords_y = result['receiver_coords_y']
        source_x = result['source_position_x']
        source_y = result['source_position_y']
        distances = result['distances']
        distance_type = result['distance_type']
        include_elevation = result['include_elevation']
        
        # Plot receivers as blue circles
        receiver_scatter = pg.ScatterPlotItem(
            x=receiver_coords_x, 
            y=receiver_coords_y,
            pen=pg.mkPen(color='blue', width=2),
            brush=pg.mkBrush(color='lightblue'),
            size=8,
            symbol='o'
        )
        self.spatial_plot.addItem(receiver_scatter)
        
        # Plot source as red square
        source_scatter = pg.ScatterPlotItem(
            x=[source_x], 
            y=[source_y],
            pen=pg.mkPen(color='red', width=2),
            brush=pg.mkBrush(color='red'),
            size=15,
            symbol='s'
        )
        self.spatial_plot.addItem(source_scatter)
        
        # Draw lines from source to receivers to visualize distances
        for i, (rx, ry, dist) in enumerate(zip(receiver_coords_x, receiver_coords_y, distances)):
            # Draw line from source to receiver
            line = pg.PlotDataItem(
                x=[source_x, rx], 
                y=[source_y, ry],
                pen=pg.mkPen(color='gray', width=1, style=pg.QtCore.Qt.DashLine)
            )
            self.spatial_plot.addItem(line)
        
        # Set labels
        self.spatial_plot.setLabel('left', 'Y Coordinate [m]')
        self.spatial_plot.setLabel('bottom', 'X Coordinate [m]')
        
        # Set equal aspect ratio for proper spatial representation
        self.spatial_plot.setAspectLocked(True)
        
        # Auto-range to fit all points with margin and set zoom limits
        all_x = np.concatenate([receiver_coords_x, [source_x]])
        all_y = np.concatenate([receiver_coords_y, [source_y]])
        
        if len(all_x) > 1:
            x_range = np.max(all_x) - np.min(all_x)
            y_range = np.max(all_y) - np.min(all_y)
            margin_x = x_range * 0.1  # 10% margin
            
            # Handle Y-axis: if Y range is very small (linear array), use range based on profile length
            if y_range < 2.0:  # If Y range is less than 2 meters (linear array)
                y_center = (np.max(all_y) + np.min(all_y)) / 2
                # Use 5% of total profile length as Y display range, minimum 10m
                profile_length = x_range
                y_display_range = max(profile_length * 0.05, 10.0)
                y_min_display = y_center - y_display_range / 2
                y_max_display = y_center + y_display_range / 2
                # Set Y limits to prevent excessive panning (allow small movement but not beyond reasonable bounds)
                y_margin = y_display_range * 0.2  # Allow 20% extra movement
                y_min_limit = y_center - y_margin
                y_max_limit = y_center + y_margin
            else:
                margin_y = y_range * 0.1  # 10% margin
                y_min_display = np.min(all_y) - margin_y
                y_max_display = np.max(all_y) + margin_y
                y_min_limit = np.min(all_y)
                y_max_limit = np.max(all_y)
            
            self.spatial_plot.setXRange(np.min(all_x) - margin_x, np.max(all_x) + margin_x)
            self.spatial_plot.setYRange(y_min_display, y_max_display)
            
            # Set zoom limits - restrict to data extent for X, lock Y for linear arrays
            self.spatial_plot.getViewBox().setLimits(
                xMin=np.min(all_x),
                xMax=np.max(all_x),
                yMin=y_min_limit,
                yMax=y_max_limit
            )
        else:
            # Single point case - set tight limits around the point
            center_x = all_x[0] if len(all_x) > 0 else 0
            center_y = all_y[0] if len(all_y) > 0 else 0
            self.spatial_plot.setXRange(center_x - 10, center_x + 10)
            self.spatial_plot.setYRange(center_y - 10, center_y + 10)
            self.spatial_plot.getViewBox().setLimits(
                xMin=center_x - 10, xMax=center_x + 10,
                yMin=center_y - 10, yMax=center_y + 10
            )

    def plotSpectrum(self, result):
        """Plot frequency spectrum"""
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
        
        # Limit to max frequency
        fmax = self.current_parameters['fmax']
        f_indices = fs <= fmax
        fs = fs[f_indices]
        XF = XF[:, f_indices]
        
        # Normalize traces
        for i in range(XF.shape[0]):
            if np.nanmax(XF[i, :]) > 0:
                XF[i, :] = XF[i, :] / np.nanmax(XF[i, :])
        
        # XF has shape (traces/receivers, frequencies)
        # For display: frequencies (X-axis, bottom) vs X coordinates (Y-axis, left)
        # So we need to transpose the data
        XF_display = XF.T  # Now shape is (frequencies, X coordinates)
        
        # Create image item - frequencies on X, X coordinates on Y (data is already sorted)
        img_item = createImageItem(XF_display, fs, receiver_coords_x, 'viridis')
        self.spectrum_plot.addItem(img_item)
        
        # Add colorbar
        self._addSpectrumColorbar(img_item, XF_display)
        
        # Set labels - now frequencies are on X-axis, X coordinates on Y-axis
        self.spectrum_plot.setLabel('left', 'X Coordinate [m]')
        self.spectrum_plot.setLabel('bottom', 'Frequency [Hz]')
        
        # Set axis ranges and limits
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
        if self.current_result is not None:
            self._plotSeismogramInternal(self.current_result)
    
    def _plotSeismogramInternal(self, result):
        """Plot seismogram traces using wiggle or image display"""
        self.wiggle_plot.clear()
        
        # Always remove any existing colorbar first (will be re-added if needed in image mode)
        self._removeSeismogramColorbar()
        
        # Reset view box to ensure clean state when switching trace modes
        # This clears both the current view and any previous view limits
        self.wiggle_plot.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)
        self.wiggle_plot.getViewBox().autoRange()
        
        # Get data (already sorted by offset in worker)
        XT = result['data_matrix']
        receiver_coords_x = result['receiver_coords_x']
        distances = result['distances']
        trace_positions = result['trace_positions']  # Keep original trace positions
        si = result['sampling_interval']
        
        # Check if we have data
        if XT.size == 0 or len(distances) == 0:
            # No data to plot
            self.wiggle_plot.setLabel('left', 'Time [s]')
            self.wiggle_plot.setLabel('bottom', 'Distance [m]')
            return
        
        # Create time axis
        Nt = XT.shape[1]
        time = np.arange(Nt) * si
        
        # Don't filter data - keep all data intact like in core.py
        # The view range will be set later based on fix_max_time
        
        # Determine display mode
        display_mode = "Wiggle"  # Default
        if hasattr(self, 'display_mode_combo'):
            display_mode = self.display_mode_combo.currentText()
        
        # Determine trace positioning (by number or position)
        trace_by_position = True  # Default to position
        if hasattr(self, 'trace_by_combo'):
            trace_by_position = self.trace_by_combo.currentText() == "Position"
        
        # Use either trace_positions (receiver X coordinates) or trace numbers
        if trace_by_position:
            plot_positions = trace_positions  # Use original receiver X coordinates for display
            xlabel = 'Position [m]'
        else:
            plot_positions = np.arange(len(trace_positions))  # Trace numbers 0, 1, 2, ...
            xlabel = 'Trace Number'
        
        # Set labels
        self.wiggle_plot.setLabel('left', 'Time [s]')
        self.wiggle_plot.setLabel('bottom', xlabel)
        
        if display_mode == "Image":
            # Plot as image
            self._plotSeismogramImage(XT, time, plot_positions)
        else:
            # Plot as wiggle traces
            self._plotSeismogramWiggle(XT, time, plot_positions)
        
        # Update control availability based on display mode
        self.updateControlsForDisplayMode()
    
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
    
    def _plotSeismogramImage(self, XT, time, plot_positions):
        """Plot seismogram as an image"""
        # Apply parameters
        normalize = self.normalize_check.isChecked() if hasattr(self, 'normalize_check') else True
        gain = self.gain_spinbox.value() if hasattr(self, 'gain_spinbox') else 1.0
        colormap = self.colormap_combo.currentText() if hasattr(self, 'colormap_combo') else 'Greys'
        
        # Process data
        XT_plot = XT.copy()
        
        if normalize:
            # Normalize each trace
            for i in range(XT_plot.shape[0]):
                if np.nanmax(np.abs(XT_plot[i, :])) > 0:
                    XT_plot[i, :] = XT_plot[i, :] / np.nanmax(np.abs(XT_plot[i, :]))
        
        # Apply gain
        XT_plot *= gain
        
        # For image display: XT has shape (traces, time samples)
        # Pass as-is to createImageItem which will handle orientation
        XT_display = XT_plot
        
        # Create image item with selected colormap
        from .pyqtgraph_utils import createImageItem
        img_item = createImageItem(XT_display, plot_positions, time, colormap)
        self.wiggle_plot.addItem(img_item)
        
        # Add colorbar for image mode
        self._addSeismogramColorbar(img_item, XT_display)
        
        # Set ranges and zoom limits
        if len(time) > 0:
            # Set Y range based on fix_max_time toggle (like core.py)
            if hasattr(self, 'fix_max_time_check') and self.fix_max_time_check.isChecked():
                if hasattr(self, 'max_time_spinbox'):
                    max_y = self.max_time_spinbox.value()
                else:
                    max_y = time[-1]
            else:
                # Use full seismogram range
                max_y = time[-1]
            
            self.wiggle_plot.setYRange(time[0], max_y)
            self.wiggle_plot.getViewBox().setLimits(yMin=time[0], yMax=time[-1])
        
        if len(plot_positions) > 0:
            pos_min, pos_max = np.min(plot_positions), np.max(plot_positions)
            pos_range = pos_max - pos_min
            if pos_range > 0:
                margin = pos_range * 0.1
                self.wiggle_plot.setXRange(pos_min - margin, pos_max + margin)
                self.wiggle_plot.getViewBox().setLimits(xMin=pos_min, xMax=pos_max)
            else:
                self.wiggle_plot.setXRange(pos_min - 1, pos_max + 1)
                self.wiggle_plot.getViewBox().setLimits(xMin=pos_min - 1, xMax=pos_max + 1)
    
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
        
        # Set ranges and zoom limits
        if len(time) > 0:
            # Set Y range based on fix_max_time toggle (like core.py)
            if hasattr(self, 'fix_max_time_check') and self.fix_max_time_check.isChecked():
                if hasattr(self, 'max_time_spinbox'):
                    max_y = self.max_time_spinbox.value()
                else:
                    max_y = time[-1]
            else:
                # Use full seismogram range
                max_y = time[-1]
            
            self.wiggle_plot.setYRange(time[0], max_y)
            # Set time axis limits - restrict to data extent only (no zoom out beyond data)
            self.wiggle_plot.getViewBox().setLimits(
                yMin=time[0], 
                yMax=time[-1]
            )
        
        if len(plot_positions) > 0:
            pos_min, pos_max = np.min(plot_positions), np.max(plot_positions)
            pos_range = pos_max - pos_min
            margin = max(pos_range * 0.1, mean_spacing)  # 10% margin or one trace spacing
            self.wiggle_plot.setXRange(pos_min - margin, pos_max + margin)
            # Set position axis limits - restrict to data extent only (no zoom out beyond data)
            if pos_range > 0:
                self.wiggle_plot.getViewBox().setLimits(
                    xMin=pos_min, 
                    xMax=pos_max
                )
            else:
                # If all positions are the same, set tight limits around the single position
                self.wiggle_plot.getViewBox().setLimits(
                    xMin=pos_min - 1, 
                    xMax=pos_max + 1
                )
    
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
        
        # Reset view limits to allow free navigation when no data is loaded
        self.dispersion_plot.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)
        self.spectrum_plot.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)
        self.wiggle_plot.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)
        self.spatial_plot.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)
        
        # Clear selection in stream list to avoid displaying non-existent results
        self.stream_list.clearSelection()
        
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
    
    def pickPointAtFrequency(self, clicked_freq, clicked_velocity):
        """Pick point either manually or automatically by finding maximum at frequency"""
        if self.current_dispersion_data is None:
            return
        
        result = self.current_dispersion_data
        FV = result['dispersion_image']
        frequencies = result['frequencies']
        velocities = result['velocities']
        
        # Check picking mode
        is_auto_mode = self.picking_mode_combo.currentIndex() == 1
        
        if is_auto_mode:
            # Auto mode: find maximum at the clicked frequency
            # Find the closest frequency index
            freq_idx = np.argmin(np.abs(frequencies - clicked_freq))
            actual_freq = frequencies[freq_idx]
            
            # Get the dispersion values at this frequency (correct indexing: FV[freq_idx, :])
            dispersion_slice = FV[freq_idx, :]
            
            # Find the maximum velocity at this frequency
            max_vel_idx = np.argmax(dispersion_slice)
            picked_velocity = velocities[max_vel_idx]
            picked_freq = actual_freq
        else:
            # Manual mode: use clicked coordinates directly
            picked_freq = clicked_freq
            picked_velocity = clicked_velocity
        
        # Check if we already have a point at this frequency (replace if so)
        existing_idx = None
        for i, (f, v) in enumerate(self.picked_points):
            if abs(f - picked_freq) < (frequencies[1] - frequencies[0]) * 0.5:  # Within half frequency step
                existing_idx = i
                break
        
        if existing_idx is not None:
            # Replace existing point
            self.picked_points[existing_idx] = (picked_freq, picked_velocity)
            # Remove old plot item
            self.dispersion_plot.removeItem(self.picked_point_items[existing_idx])
            self.picked_point_items[existing_idx] = None
        else:
            # Add new point
            self.picked_points.append((picked_freq, picked_velocity))
            self.picked_point_items.append(None)
            existing_idx = len(self.picked_points) - 1
        
        # Create new plot item
        point_item = pg.ScatterPlotItem(
            x=[picked_freq], y=[picked_velocity],
            pen=pg.mkPen(color='red', width=2),
            brush=pg.mkBrush(color='red'),
            size=10, symbol='o'
        )
        self.dispersion_plot.addItem(point_item)
        self.picked_point_items[existing_idx] = point_item
        
        # Sort points by frequency
        sorted_data = sorted(zip(self.picked_points, self.picked_point_items))
        self.picked_points = [item[0] for item in sorted_data]
        self.picked_point_items = [item[1] for item in sorted_data]
        
        # Enable interpolation if we have at least 2 points
        if len(self.picked_points) >= 2:
            self.interpolate_button.setEnabled(True)
        
        # Enable clearing if we have points
        if len(self.picked_points) > 0:
            self.clear_picking_button.setEnabled(True)
    
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
        
        for i, (freq, vel) in enumerate(self.picked_points):
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
    
    def interpolateCurve(self):
        """Interpolate a smooth curve between picked points"""
        if len(self.picked_points) < 2:
            QMessageBox.warning(self, "Insufficient Points", 
                               "Please pick at least 2 points to interpolate a curve.")
            return
        
        try:
            # Sort points by frequency
            sorted_points = sorted(self.picked_points)
            frequencies = np.array([p[0] for p in sorted_points])
            velocities = np.array([p[1] for p in sorted_points])
            
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
            
            # Plot interpolated curve
            self.curve_line = pg.PlotDataItem(
                x=interp_frequencies, y=interp_velocities,
                pen=pg.mkPen(color='blue', width=3)
            )
            self.dispersion_plot.addItem(self.curve_line)
            
            # Store curve for current shot
            current_row = self.stream_list.currentRow()
            if current_row >= 0:
                shot_key = f'shot_{current_row}'
                self.extracted_curves[shot_key] = {
                    'frequencies': interp_frequencies,
                    'velocities': interp_velocities,
                    'picked_points': self.picked_points.copy(),
                    'interpolated': True
                }
                
                # Enable export if we have curves
                if self.extracted_curves:
                    self.export_curves_button.setEnabled(True)
            
            QMessageBox.information(self, "Curve Interpolated", 
                                   f"Interpolated curve created with {len(interp_frequencies)} points.\n"
                                   f"Frequency range: {freq_min:.1f} - {freq_max:.1f} Hz\n"
                                   f"Based on {len(self.picked_points)} picked points.")
            
        except Exception as e:
            QMessageBox.critical(self, "Interpolation Error", f"Error interpolating curve:\n{e}")
    
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
        
        # Disable buttons
        self.interpolate_button.setEnabled(False)
        self.clear_picking_button.setEnabled(False)
        
        # Remove curve from extracted curves for current shot
        current_row = self.stream_list.currentRow()
        if current_row >= 0:
            shot_key = f'shot_{current_row}'
            if shot_key in self.extracted_curves:
                del self.extracted_curves[shot_key]
                
                # Disable export if no curves left
                if not self.extracted_curves:
                    self.export_curves_button.setEnabled(False)
    
    def exportCurves(self):
        """Export extracted dispersion curves to CSV file"""
        if not self.extracted_curves:
            QMessageBox.warning(self, "No Curves", "No dispersion curves have been extracted yet.")
            return
        
        # Get save file path
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Dispersion Curves", 
            "dispersion_curves.csv", 
            "CSV files (*.csv);;All files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            import csv
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Shot', 'Frequency_Hz', 'Velocity_m_s', 'Interpolated', 'Num_Picked_Points'])
                
                # Write data for each shot
                for shot_key, curve_data in self.extracted_curves.items():
                    shot_number = shot_key.replace('shot_', '')
                    frequencies = curve_data['frequencies']
                    velocities = curve_data['velocities']
                    interpolated = curve_data.get('interpolated', False)
                    num_picked_points = len(curve_data.get('picked_points', []))
                    
                    for f, v in zip(frequencies, velocities):
                        writer.writerow([shot_number, f, v, interpolated, num_picked_points])
            
            QMessageBox.information(self, "Export Complete", 
                                   f"Dispersion curves exported to:\n{file_path}\n\n"
                                   f"Exported {len(self.extracted_curves)} curves with "
                                   f"{sum(len(c['frequencies']) for c in self.extracted_curves.values())} total points.")
            
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

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop worker thread if running
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        event.accept()
