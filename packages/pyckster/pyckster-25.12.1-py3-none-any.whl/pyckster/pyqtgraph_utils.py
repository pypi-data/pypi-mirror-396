import pyqtgraph as pqg
from PyQt5 import QtGui

#######################################
# Monkey patching the _getFillPath in PlotCurveItem to allow for filling when plotting traces vertically
# This is a temporary fix until the issue is resolved in pyqtgraph
#######################################
def _getFillPath(self):
    if self.fillPath is not None:
        return self.fillPath

    path = QtGui.QPainterPath(self.getPath())
    self.fillPath = path
    if self.opts['fillLevel'] == 'enclosed':
        return path

    baseline = self.opts['fillLevel']
    x, y = self.getData()
    lx, rx = x[[0, -1]]
    ly, ry = y[[0, -1]]

    if ry != baseline:
        path.lineTo(rx, baseline) # Last point to baseline at same y
    # path.lineTo(lx, baseline) 
    if ly != baseline:
        path.lineTo(baseline, ly) # baseline at last point y to baseline at first point y (new line)
        path.lineTo(lx, ly) # baseline at first point y to first point

    return path

pqg.PlotCurveItem._getFillPath = _getFillPath

#######################################
# Helper functions for pyqtgraph
#######################################

def createImageItem(data, x_coords, y_coords, colormap='viridis', source='matplotlib'):
    """
    Create a pyqtgraph ImageItem with proper scaling and positioning
    
    Parameters:
    -----------
    data : 2D numpy array
        Image data to display with shape (x_size, y_size)
        where x_size corresponds to x_coords and y_size to y_coords
    x_coords : 1D numpy array
        X coordinates for the image (bottom axis)
    y_coords : 1D numpy array  
        Y coordinates for the image (left axis)
    colormap : str
        Name of the matplotlib colormap to use (default: 'viridis')
        Available options include: 'viridis', 'plasma', 'inferno', 'hot', 
        'cool', 'seismic', 'jet', 'Blues', 'Reds', etc.
    source : str
        Source for the colormap (default: 'matplotlib')
        
    Returns:
    --------
    ImageItem : pyqtgraph ImageItem
        Configured image item with matplotlib colormap applied
    """
    import numpy as np
    
    # Create the image item
    img_item = pqg.ImageItem()
    
    # PyQtGraph ImageItem expects data with shape (width, height)
    # where width corresponds to x-axis and height to y-axis
    # We need to transpose if data is in (y, x) format
    if data.shape[0] == len(y_coords) and data.shape[1] == len(x_coords):
        # Data is in (y, x) format, transpose it
        data_oriented = data.T
    elif data.shape[0] == len(x_coords) and data.shape[1] == len(y_coords):
        # Data is already in (x, y) format
        data_oriented = data
    else:
        # Data shape doesn't match coordinates, use as-is
        data_oriented = data
    
    # Set the image data
    img_item.setImage(data_oriented)
    
    # Calculate the transform to map pixel coordinates to real coordinates
    if len(x_coords) > 1:
        x_scale = (x_coords[-1] - x_coords[0]) / (len(x_coords) - 1)
    else:
        x_scale = 1.0
    
    # Prevent zero scale that would cause division by zero
    if x_scale == 0:
        x_scale = 1.0
        
    if len(y_coords) > 1:
        y_scale = (y_coords[-1] - y_coords[0]) / (len(y_coords) - 1)
    else:
        y_scale = 1.0
    
    # Prevent zero scale that would cause division by zero
    if y_scale == 0:
        y_scale = 1.0
    
    # Set the transform
    # Note: We subtract 0.5 from the translation to center pixels on their coordinate values
    # In PyQtGraph, pixel (0,0) is at the top-left corner of the first pixel,
    # but we want it to be at the center of the pixel, which is at (0.5, 0.5) in pixel coordinates
    transform = QtGui.QTransform()
    transform.scale(x_scale, y_scale)
    transform.translate(x_coords[0]/x_scale - 0.5, y_coords[0]/y_scale - 0.5)
    img_item.setTransform(transform)
    
    # Set colormap
    try:
        colormap_obj = pqg.colormap.get(colormap, source=source)
        img_item.setColorMap(colormap_obj)
    except Exception as e:
        # Fallback if specified colormap is not available
        print(f"Warning: Colormap '{colormap}' not available ({e}), falling back to 'viridis'")
        try:
            fallback_colormap = pqg.colormap.get('viridis', source=source)
            img_item.setColorMap(fallback_colormap)
        except Exception as e2:
            # If viridis is also not available, continue without colormap
            print(f"Warning: Even fallback colormap 'viridis' not available ({e2})")
            pass
    
    return img_item


def createColorBar(image_item, orientation='vertical', label='', width=10, height=100):
    """
    Create a colorbar for a pyqtgraph ImageItem
    
    Parameters:
    -----------
    image_item : pyqtgraph.ImageItem
        The image item to create colorbar for
    orientation : str
        'vertical' or 'horizontal' (default: 'vertical')
    label : str
        Label for the colorbar (default: '')
    width : int
        Width of colorbar in pixels (for vertical orientation)
    height : int
        Height of colorbar in pixels (for horizontal orientation)
        
    Returns:
    --------
    colorbar_item : pyqtgraph.ImageItem
        Colorbar as an ImageItem
    """
    import numpy as np
    
    # Get the colormap from the image item
    colormap = image_item.getColorMap()
    if colormap is None:
        # Use default viridis if no colormap set
        colormap = pqg.colormap.get('viridis', source='matplotlib')
    
    # Create colorbar data
    if orientation == 'vertical':
        # Create vertical gradient
        cbar_data = np.linspace(0, 1, height).reshape(-1, 1)
        cbar_data = np.repeat(cbar_data, width, axis=1)
    else:
        # Create horizontal gradient  
        cbar_data = np.linspace(0, 1, width).reshape(1, -1)
        cbar_data = np.repeat(cbar_data, height, axis=0)
    
    # Create colorbar ImageItem
    cbar_item = pqg.ImageItem()
    cbar_item.setImage(cbar_data)
    cbar_item.setColorMap(colormap)
    
    return cbar_item