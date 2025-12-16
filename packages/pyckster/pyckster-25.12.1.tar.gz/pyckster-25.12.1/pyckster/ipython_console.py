"""
In-process IPython console for PyCKSTER.

Provides an embedded IPython console that runs directly in the main application,
giving full access to the application's objects and methods for debugging,
custom plotting, and data exports.
"""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt
import sys


def show_ipython_console(parent_window):
    """
    Open an in-process IPython console in a separate window.
    
    This console runs directly in the main application thread, giving full
    access to the parent_window (app) and all its attributes and methods.
    
    Args:
        parent_window: The main PyCKSTER window (InversionApp instance)
    """
    try:
        from IPython.terminal.embed import InteractiveShellEmbed
        from IPython.terminal.ipapp import load_default_config
    except ImportError:
        QMessageBox.warning(parent_window, "Missing Dependencies", 
                          "IPython console requires 'ipython' package.\n\n"
                          "Install it with: pip install ipython")
        return
    
    # Create console window
    console_window = QMainWindow()
    console_window.setWindowTitle("IPython Console - PyCKSTER (In-Process)")
    console_window.setGeometry(100, 100, 900, 700)
    
    # Track in parent for cleanup
    if not hasattr(parent_window, 'ipython_console_windows'):
        parent_window.ipython_console_windows = []
    parent_window.ipython_console_windows.append(console_window)
    
    def on_console_closed():
        """Remove from tracking list when closed"""
        try:
            parent_window.ipython_console_windows.remove(console_window)
        except (ValueError, AttributeError):
            pass
    
    console_window.destroyed.connect(on_console_closed)
    
    # Create central widget with layout
    central_widget = QWidget()
    layout = QVBoxLayout()
    central_widget.setLayout(layout)
    console_window.setCentralWidget(central_widget)
    
    # Create a simple widget to hold the console
    # We'll use a text area that displays IPython output
    from PyQt5.QtWidgets import QTextEdit
    from PyQt5.QtCore import QTimer
    
    # Create output display (text)
    output_display = QTextEdit()
    output_display.setReadOnly(True)
    output_display.setStyleSheet("""
        QTextEdit {
            background-color: #1e1e1e;
            color: #d4d4d4;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
    """)
    
    layout.addWidget(output_display)
    
    # Create IPython shell with custom config
    try:
        import numpy as np
        import matplotlib
        matplotlib.use('Qt5Agg')  # Use Qt5 interactive backend for new windows
        import matplotlib.pyplot as plt
        
        # Configure matplotlib
        plt.ion()  # Turn on interactive mode for window display
        
        config = load_default_config()
        config.TerminalInteractiveShell.confirm_exit = False
        
        # Pre-populate user namespace with common libraries
        user_ns = {
            'app': parent_window,
            'self': parent_window,
            'np': np,
            'plt': plt,
        }
        
        ipshell = InteractiveShellEmbed(
            config=config,
            user_ns=user_ns,
            user_module=None
        )
        
    except Exception as e:
        QMessageBox.critical(parent_window, "Console Error", 
                           f"Failed to create IPython shell:\n{e}")
        return
    
    # Inject custom banner
    ipshell.banner1 = """
╔══════════════════════════════════════════════════════════╗
║           PyCKSTER In-Process IPython Console            ║
║                                                          ║
║  Full access to the main application:                    ║
║  • app/self      - Main application window               ║
║  • app.trace_position, app.inversion_manager, etc.       ║
║                                                          ║
║  Pre-imported libraries:                                 ║
║  • np (numpy)    - Numerical computing                   ║
║  • plt (matplotlib) - Plotting (opens new windows)       ║
║                                                          ║
║  Examples:                                               ║
║    plt.plot([1, 2, 3], [1, 4, 9])                       ║
║    plt.show()          # Opens plot in new window        ║
║                                                          ║
║    data = np.array([1, 2, 3, 4, 5])                     ║
║    print(data.mean())                                    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    
    # Input line for commands
    from PyQt5.QtWidgets import QLineEdit
    
    input_line = QLineEdit()
    input_line.setStyleSheet("""
        QLineEdit {
            background-color: #2d2d2d;
            color: #d4d4d4;
            border: 1px solid #3d3d3d;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            padding: 5px;
        }
    """)
    input_line.setPlaceholderText("Enter Python command... (type 'help()' for help, 'exit' to close)")
    layout.addWidget(input_line)
    
    # Command history
    command_history = []
    history_index = -1
    
    def execute_command(cmd):
        """Execute a command in the IPython shell"""
        nonlocal history_index
        
        if not cmd.strip():
            return
        
        # Add to history
        command_history.append(cmd)
        history_index = len(command_history)
        
        # Display command
        output_display.append(f">>> {cmd}")
        
        # Check for exit command
        if cmd.strip().lower() in ['exit', 'quit', 'exit()', 'quit()']:
            console_window.close()
            return
        
        try:
            import io
            import sys as sys_module
            
            # Capture stdout and stderr
            old_stdout = sys_module.stdout
            old_stderr = sys_module.stderr
            captured_output = io.StringIO()
            
            try:
                sys_module.stdout = captured_output
                sys_module.stderr = captured_output
                
                # Execute in IPython shell's namespace
                result = ipshell.run_cell(cmd, silent=False, store_history=True)
                
                # Get captured output
                output = captured_output.getvalue()
                if output:
                    output_display.append(output.rstrip())
                
                # Display result if not None
                if result.result is not None:
                    output_display.append(f"{repr(result.result)}")
            finally:
                sys_module.stdout = old_stdout
                sys_module.stderr = old_stderr
        except Exception as e:
            output_display.append(f"Error: {type(e).__name__}: {e}")
        
        # Scroll to bottom
        output_display.verticalScrollBar().setValue(
            output_display.verticalScrollBar().maximum()
        )
        
        input_line.clear()
    
    def on_input_return():
        """Handle return key in input line"""
        cmd = input_line.text()
        execute_command(cmd)
    
    def on_input_key_press(event):
        """Handle arrow keys for command history"""
        nonlocal history_index
        
        if event.key() == Qt.Key_Up and command_history:
            if history_index > 0:
                history_index -= 1
                input_line.setText(command_history[history_index])
            elif history_index == len(command_history):
                history_index -= 1
                input_line.setText(command_history[history_index])
            return True
        
        elif event.key() == Qt.Key_Down and command_history:
            if history_index < len(command_history) - 1:
                history_index += 1
                input_line.setText(command_history[history_index])
            else:
                history_index = len(command_history)
                input_line.clear()
            return True
        
        return False
    
    # Connect input line
    input_line.returnPressed.connect(on_input_return)
    
    # Override key press for history navigation
    original_keyPressEvent = input_line.keyPressEvent
    
    def custom_keyPressEvent(event):
        if not on_input_key_press(event):
            original_keyPressEvent(event)
    
    input_line.keyPressEvent = custom_keyPressEvent
    
    # Display welcome message
    output_display.setText(ipshell.banner1)
    
    try:
        import IPython
        output_display.append(f"\nIPython version: {IPython.__version__}")
    except Exception:
        output_display.append("\nIPython console ready")
    input_line.setFocus()
    
    # Show window
    console_window.show()
