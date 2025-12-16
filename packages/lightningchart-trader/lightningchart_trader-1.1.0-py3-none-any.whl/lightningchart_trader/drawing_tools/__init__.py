import uuid


class DrawingToolBase:
    """Base class for all Drawing Tools."""

    def __init__(self, trader):
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance = trader.instance

    def dispose(self):
        """Disposes the drawing tool."""
        self.instance.send(self.id, 'dispose', {})
        return self
    
    def get_position(self):
        """Gets the current position of the drawing tool.

        Note:
            This method should be used after the chart is opened with the open() method.
        
        Returns:
            list or dict: For most tools, returns list of points [{'x': x1, 'y': y1}, {'x': x2, 'y': y2}, ...].
                        For Horizontal/Vertical lines, returns single value {'x': x} or {'y': y}.
        """
        result = self.instance.get(self.id, 'getPosition', {})
        return result
    
    def on_pointer_down(self, callback):
        """Subscribe to pointer down events on the drawing tool.
    
        Args:
            callback: Function receiving event dict with keys:
                - x (float): Chart X coordinate (data/axis value, not pixels)
                - y (float): Chart Y coordinate (data/axis value, not pixels)
                - xClient (float): Screen X coordinate in pixels
                - yClient (float): Screen Y coordinate in pixels
                - button (int): Mouse button (0=left, 1=middle, 2=right)
                - isControlPoint (bool): True if clicked on control point (the draggable endpoints)
            
        Example:
            >>> trend = trader.add_trend_line(100, 200, 150, 250)
            >>> def handler(evt):
            ...     print('Pointer DOWN event:', evt)
            >>> trend.on_pointer_down(handler)
            >>> # Later: trend.off_pointer_down()
        """
        callback_id = f'{self.id}_onPointerDownDrawingTools'
        self.instance.event_handlers[callback_id] = callback
        self.instance.send(self.id, 'onPointerDownDrawingTools', {'callbackId': callback_id})
        return self
        
    def off_pointer_down(self):
        """Unsubscribe from pointer down events.
        """
        callback_id = f'{self.id}_onPointerDownDrawingTools'
        if callback_id in self.instance.event_handlers:
            del self.instance.event_handlers[callback_id]
        self.instance.send(self.id, 'offPointerDownDrawingTools', {'callbackId': callback_id})
        return self

    def on_pointer_up(self, callback):
        """Subscribe to pointer up events on the drawing tool.
        
        Args:
            callback: Function receiving event dict with keys:
                - x (float): Chart X coordinate (data/axis value, not pixels)
                - y (float): Chart Y coordinate (data/axis value, not pixels)
                - xClient (float): Screen X coordinate in pixels
                - yClient (float): Screen Y coordinate in pixels
                - button (int): Mouse button (0=left, 1=middle, 2=right)
                - isControlPoint (bool): True if clicked on control point (the draggable endpoints)
            
        Example:
            >>> trend = trader.add_trend_line(100, 200, 150, 250)
            >>> def handler(evt):
            ...     print('Pointer UP event:', evt)
            >>> trend.on_pointer_up(handler)
            >>> # Later: trend.off_pointer_up()
        """
        callback_id = f'{self.id}_onPointerUpDrawingTools'
        self.instance.event_handlers[callback_id] = callback
        self.instance.send(self.id, 'onPointerUpDrawingTools', {'callbackId': callback_id})
        return self

    def off_pointer_up(self):
        """Unsubscribe from pointer up events.
        """
        callback_id = f'{self.id}_onPointerUpDrawingTools'
        if callback_id in self.instance.event_handlers:
            del self.instance.event_handlers[callback_id]
        self.instance.send(self.id, 'offPointerUpDrawingTools', {'callbackId': callback_id})
        return self
    
    def on_pointer_enter(self, callback):
        """Subscribe to pointer enter events (mouse enters drawing tool area).
        
        Args:
            callback: Function receiving event dict with keys:
                - x (float): Chart X coordinate (data/axis value, not pixels)
                - y (float): Chart Y coordinate (data/axis value, not pixels)
                - xClient (float): Screen X coordinate in pixels
                - yClient (float): Screen Y coordinate in pixels
                - button (int): Mouse button (0=left, 1=middle, 2=right)
                - isControlPoint (bool): True if clicked on control point (the draggable endpoints)
            
        Example:
            >>> trend = trader.add_trend_line(100, 200, 150, 250)
            >>> def handler(evt):
            ...     print('Pointer ENTER event:', evt)
            >>> trend.on_pointer_enter(handler)
            >>> # Later: trend.off_pointer_enter()
        """
        callback_id = f'{self.id}_onPointerEnterDrawingTools'
        self.instance.event_handlers[callback_id] = callback
        self.instance.send(self.id, 'onPointerEnterDrawingTools', {'callbackId': callback_id})
        return self

    def off_pointer_enter(self):
        """Unsubscribe from pointer enter events.
        """
        callback_id = f'{self.id}_onPointerEnterDrawingTools'
        if callback_id in self.instance.event_handlers:
            del self.instance.event_handlers[callback_id]
        self.instance.send(self.id, 'offPointerEnterDrawingTools', {'callbackId': callback_id})
        return self
    
    def on_pointer_leave(self, callback):
        """Subscribe to pointer leave events (mouse leaves drawing tool area).
        
        Args:
            callback: Function receiving event dict with keys:
                - x (float): Chart X coordinate (data/axis value, not pixels)
                - y (float): Chart Y coordinate (data/axis value, not pixels)
                - xClient (float): Screen X coordinate in pixels
                - yClient (float): Screen Y coordinate in pixels
                - button (int): Mouse button (0=left, 1=middle, 2=right)
                - isControlPoint (bool): True if clicked on control point (the draggable endpoints)
            
        Example:
            >>> trend = trader.add_trend_line(100, 200, 150, 250)
            >>> def handler(evt):
            ...     print('Pointer LEAVE event:', evt)
            >>> trend.on_pointer_leave(handler)
            >>> # Later: trend.off_pointer_leave()
        """
        callback_id = f'{self.id}_onPointerLeaveDrawingTools'
        self.instance.event_handlers[callback_id] = callback
        self.instance.send(self.id, 'onPointerLeaveDrawingTools', {'callbackId': callback_id})
        return self

    def off_pointer_leave(self):
        """Unsubscribe from pointer leave events.
        """
        callback_id = f'{self.id}_onPointerLeaveDrawingTools'
        if callback_id in self.instance.event_handlers:
            del self.instance.event_handlers[callback_id]
        self.instance.send(self.id, 'offPointerLeaveDrawingTools', {'callbackId': callback_id})
        return self
    
    def on_drawing_tool_moved(self, callback):
        """Subscribe to drawing tool moved events (triggered when position changes).
        
        Args:
            callback: Function receiving event dict with keys:
                - xPosition (float): New X coordinate (data/axis value, not pixels)
                - yPosition (float): New Y coordinate (data/axis value, not pixels)
                - drawingTool (dict): Reference with 'id' and 'type' of the drawing tool
        """
        callback_id = f'{self.id}_onDrawingToolMoved'
        self.instance.event_handlers[callback_id] = callback
        self.instance.send(self.id, 'onDrawingToolMoved', {'callbackId': callback_id, 'toolType': self.__class__.__name__  })
        return self  


    def off_drawing_tool_moved(self):
        """Unsubscribe from drawing tool moved events.
        """
        callback_id = f'{self.id}_onDrawingToolMoved'
        if callback_id in self.instance.event_handlers:
            del self.instance.event_handlers[callback_id]
        self.instance.send(self.id, 'offDrawingToolMoved', {'callbackId': callback_id})
        return self


# ruff: noqa: E402, F401
from .vertical_line import VerticalLine
from .arrow import Arrow
from .cross_line import CrossLine
from .date_range import DateRange
from .elliot_wave import ElliotWave
from .ellipse import Ellipse
from .extended_line import ExtendedLine
from .fibonacci_arc import FibonacciArc
from .fibonacci_extension import FibonacciExtension
from .fibonacci_fan import FibonacciFan
from .fibonacci_retracements import FibonacciRetracements
from .fibonacci_time_zones import FibonacciTimeZones
from .flat_top_bottom import FlatTopBottom
from .head_and_shoulders import HeadAndShoulders
from .horizontal_line import HorizontalLine
from .horizontal_ray import HorizontalRay
from .linear_regression_channel import LinearRegressionChannel
from .parallel_channel import ParallelChannel
from .pitchfork import Pitchfork
from .price_range import PriceRange
from .rectangle import Rectangle
from .text_box import TextBox
from .plain_text import PlainText
from .trend_line import TrendLine
from .triangle import Triangle
from .xabcd_pattern import XABCDpattern
from .cycle_lines import CycleLines
from .sine_wave import SineWave
from .gannbox import GannBox
from .gannfan import GannFan
