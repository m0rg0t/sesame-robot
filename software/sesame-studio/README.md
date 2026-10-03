# Sesame Studio

Sesame Studio is a animation composer tool for the Sesame Robot. Use it to set servo angles and frames, generate C++ code, and sequence frames into animations.

<img src="assets/sesamestudio-preview.png" alt="sesamestudio-preview" width="50%">

## Features

- **Interface**: Black theme with schematic overlays.
- **Views**: Top-down view and lateral angle guide for positioning.
- **Color-Coding**: Servos (S0-S7) are color-coded in inputs and code for identification.
- **Help Overlay**: Guide window accessible via button.
- **Code Generation**: Formats `setServoAngle()` commands for `sesame-firmware.ino`.
- **Timing**: Set delays for frames to create movements.

## Prerequisites

- **Python 3.10+**: Download from [python.org](https://python.org).
- **Pillow**: Used for scaling schematics.
  ```bash
  python -m pip install -r requirements.txt
  ```
- **Tkinter**: If missing, install `python3-tk`.

## How to Use

1.  **Launch**:
    ```bash
    python sesame_studio.py
    ```

2.  **Set Pose**:
    - The section displays the robot schematic with boxes over joints.
    - R1/L2: 45–180 degrees; R2/L1: 0–135 degrees; R3/R4/L3/L4: 0–180 degrees.
    - Use the **Help (?)** button for the guide.

3.  **Set Timing**:
    - Adjust the `Delay (ms)` field using a non-negative integer.
    - Click **+ ADD FRAME**. Code appears in the editor.

4.  **Export**:
    - Click **Copy to Clipboard** and paste into Arduino IDE.
    - Use **Clear Code** to start a sequence.

## Troubleshooting

- **"Module not found: tkinter"**: On some Linux distributions, you may need to install it separately (`sudo apt-get install python3-tk`).
- **High DPI Scaling**: If the interface looks tiny or huge on your screen, try changing the "High DPI scaling override" in the `python.exe` compatibility settings properties on Windows.

## Validation and development

All eight angles and the delay are validated before the editor changes. Invalid input leaves existing code intact. Command order, servo symbols and firmware angle limits are preserved. Schematics are resolved relative to this script, so launching it from another working directory is supported. Pillow 12.3.0 is optional; Tkinter's image fallback remains available.

From the repository root:

```bash
python -m unittest discover -s software/sesame-studio/tests -v
python -m compileall -q software/sesame-studio
xvfb-run -a python software/sesame-studio/tests/gui_smoke.py
```

The final command needs a display or Xvfb, Tkinter and the committed diagram files. CI checks Python 3.10 and 3.14 with the pinned Pillow release. These tests generate synthetic commands only: they do not open a serial port, connect to a robot, flash firmware or validate physical movement.
