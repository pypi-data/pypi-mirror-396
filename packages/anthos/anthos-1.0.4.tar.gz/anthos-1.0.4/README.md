# **Anthos**

A Tkinter-based waveform visualization widget using `Canvas` and `librosa`.

A fork of ostcrom’s *python-tkinter-waveform-widget*, with a simpler API and customizable waveform display options.

---

## **Usage**

```python
import tkinter as tk
import anthos

# Create main Tkinter window
main_window = tk.Tk()

# Standard Tkinter Canvas options
cnf = {
    "height": 100,
    "width": 500,
    "bg": "green"
}

# Waveform display options
wave_cnf = {
    "x_scale": 1,
    "y_scale": 5
}

path_to_audio = "test.mp3"

# Create waveform widget
widget = anthosWidget(
    master=main_window,
    path(path_to_audio)
    cnf=cnf,
    wave_cnf=wave_cnf
)

# Draw the waveform
widget.draw()

# The widget inherits from tkinter.Canvas, so you can use standard geometry methods
widget.place(x=10, y=10)

# Update standard canvas configuration dynamically
widget.config({"bg": "black", "width": 600})
```

---