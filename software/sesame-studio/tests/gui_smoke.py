"""Run with a display (or xvfb-run). Never connects to a robot."""
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

STUDIO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDIO))
import sesame_studio as studio

with tempfile.TemporaryDirectory() as elsewhere:
    os.chdir(elsewhere)
    root = studio.tk.Tk()
    root.withdraw()
    try:
        app = studio.SesameStudioApp(root)
        root.update_idletasks()
        assert hasattr(app, 'robot_image1') and hasattr(app, 'robot_image2')
        assert set(app.servo_colors) == set(app.servo_vars)
        for servo, color in app.servo_colors.items():
            assert app.code_text.tag_cget(f'servo_{servo}', 'foreground') == color
        app.add_frame()
        original = app.code_text.get('1.0', studio.tk.END)
        assert 'delay(200);' in original
        app.servo_vars['L4'].set('181')
        with patch.object(studio.messagebox, 'showerror') as error:
            app.add_frame()
            error.assert_called_once()
        assert app.code_text.get('1.0', studio.tk.END) == original
        # Exercise Tk's optional-Pillow fallback against the committed diagrams.
        with patch.dict(sys.modules, {'PIL': None}):
            app.draw_robot_schematic()
        assert app.robot_image1.height() > 0 and app.robot_image2.height() > 0
        print('Tk smoke passed from a different working directory; no hardware accessed')
    finally:
        root.destroy()
