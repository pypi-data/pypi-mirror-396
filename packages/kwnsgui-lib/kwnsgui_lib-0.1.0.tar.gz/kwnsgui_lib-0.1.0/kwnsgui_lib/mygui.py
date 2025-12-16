"""
mygui.py - Python wrapper for the native Windows GUI extension.
Provides Window, Label, Button classes with animations.
"""

from . import mygui as _cgui

class Widget:
    """Base class for Labels and Buttons."""

    def __init__(self, widget):
        self._widget = widget

    def config(self, *, fg=None, bg=None, font_size=None, text=None):
        """
        Configure the widget.

        Args:
            fg (tuple[int,int,int], optional): Text color RGB.
            bg (tuple[int,int,int], optional): Background color RGB.
            font_size (int, optional): Font size.
            text (str, optional): Text to display.
        """
        self._widget.config(fg=fg, bg=bg, font_size=font_size, text=text)

    def show(self):
        """Show the widget."""
        self._widget.show()

    def hide(self):
        """Hide the widget."""
        self._widget.hide()

    def lock(self):
        """Disable the widget (buttons only)."""
        self._widget.lock()

    def unlock(self):
        """Enable the widget (buttons only)."""
        self._widget.unlock()

    def anim(self, start_x, start_y, end_x, end_y, duration_ms):
        """Animate widget from (start_x, start_y) to (end_x, end_y) in duration_ms."""
        self._widget.anim(start_x, start_y, end_x, end_y, duration_ms)

class Window:
    """Top-level window."""

    def __init__(self, title, width, height, r=255, g=255, b=255):
        self._win = _cgui.create_window(title, width, height, r, g, b)

    def Label(self, text, x, y):
        """Create a label at (x, y)."""
        w = self._win.Label(text, x, y)
        return Widget(w)

    def Button(self, text, x, y, command=None, args=None):
        """
        Create a button at (x, y).

        Args:
            command (callable, optional): Function to call on click.
            args (tuple, optional): Arguments for the command.
        """
        w = self._win.Button(text, x, y, command=command, args=args)
        return Widget(w)

    def run(self):
        """Start the window event loop."""
        self._win.run()

# Convenience function
def create_window(title, width, height, r=255, g=255, b=255):
    """Create and return a Window object."""
    return Window(title, width, height, r, g, b)
