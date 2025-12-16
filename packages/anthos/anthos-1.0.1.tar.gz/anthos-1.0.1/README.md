# **Anthos**

A Tkinter-based waveform visualization widget using `Canvas` and `librosa`.

A fork of ostcrom’s *python-tkinter-waveform-widget*, with a easier API and cleaner, simpler configuration options.

---

## **Usage**

```python
import tkwavewidget as anthos
import tkinter as tk

main_window = tk.Tk()

# Standard Tkinter Canvas options:
cnf = {
    "height": 100,
    "width": 500,
    "bg": "green"
}

# Waveform display options:
wave_cnf = {
    "x_scale": 1,
    "y_scale": 5
}

path_to_audio = "test.mp3"

# Create waveform widget
anthos = anthos.WaveWidget(
    main_window,
    path_to_audio,
    cnf,
    wave_cnf
)

# Draw the waveform
anthos.draw()

# The class inherits from tkinter.Canvas
anthos.place()

# Update standard canvas configuration
anthos.config(cnf)
```
