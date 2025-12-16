# kwnsgui_lib

Native Windows GUI library with animation support.

## Features

- Create Windows, Labels, Buttons
- Animations for widgets
- Easy configuration: colors, fonts, text
- Methods: `.show()`, `.hide()`, `.lock()`, `.unlock()`

## Installation

Copy `kwnsgui_lib` folder to your project.  
Requires Python 3.9+ on Windows.

## Usage

```python
from kwnsgui_lib import create_window

w = create_window("Test Window", 600, 400, 255, 255, 255)
lbl = w.Label("Hello World!", 50, 50)
lbl.config(fg=(0,0,255), font_size=18)
lbl.anim(50,50,400,200,2000)

def on_click(widget):
    widget.config(text="Clicked!", fg=(255,0,0))

btn = w.Button("Click Me", 50, 100, command=on_click, args=(lbl,))
w.run()
