import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

STUDIO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDIO))
import sesame_studio as studio

SERVO_IDS = ('R1', 'L2', 'R2', 'L1', 'R3', 'R4', 'L3', 'L4')


def app_for_frame(values=None, delay='200'):
    app = studio.SesameStudioApp.__new__(studio.SesameStudioApp)
    app.servo_vars = {key: Mock(get=Mock(return_value=(values or {}).get(key, '90')))
                      for key in SERVO_IDS}
    app.delay_var = Mock(get=Mock(return_value=delay))
    app.code_text = Mock()
    app.status_label = Mock()
    return app


class FrameIntegrationTests(unittest.TestCase):
    @patch.object(studio.messagebox, 'showerror')
    def test_invalid_last_servo_leaves_existing_editor_untouched(self, error):
        app = app_for_frame({'L4': '181'})
        app.add_frame()
        error.assert_called_once()
        app.code_text.insert.assert_not_called()
        app.code_text.see.assert_not_called()
        app.status_label.config.assert_not_called()

    @patch.object(studio.messagebox, 'showerror')
    def test_negative_delay_leaves_editor_untouched(self, error):
        app = app_for_frame(delay='-1')
        app.add_frame()
        error.assert_called_once()
        app.code_text.insert.assert_not_called()

    @patch.object(studio.messagebox, 'showerror')
    def test_valid_frame_keeps_command_order_and_tags(self, error):
        app = app_for_frame(delay='0')
        app.add_frame()
        error.assert_not_called()
        inserts = app.code_text.insert.call_args_list
        text = ''.join(call.args[1] for call in inserts)
        self.assertEqual(text, '// Frame\n' +
                         ''.join(f'setServoAngle({servo}, 90); ' for servo in SERVO_IDS[:4]) + '\n' +
                         ''.join(f'setServoAngle({servo}, 90); ' for servo in SERVO_IDS[4:]) +
                         '\ndelay(0);\n\n')
        self.assertEqual([call.args[2] for call in inserts if len(call.args) == 3],
                         [f'servo_{servo}' for servo in SERVO_IDS])


class PureFrameTests(unittest.TestCase):
    def test_every_boundary_is_accepted(self):
        from frame import frame_segments, SERVO_LIMITS
        for servo, limits in SERVO_LIMITS.items():
            for value in limits:
                with self.subTest(servo=servo, value=value):
                    angles = dict.fromkeys(SERVO_IDS, '90')
                    angles[servo] = str(value)
                    self.assertIn((f'setServoAngle({servo}, {value}); ', f'servo_{servo}'),
                                  frame_segments(angles, '200'))

    def test_every_out_of_bounds_angle_is_rejected(self):
        from frame import frame_segments, SERVO_LIMITS
        for servo, (minimum, maximum) in SERVO_LIMITS.items():
            for value in (minimum - 1, maximum + 1, '', 'NaN', '90.5', None):
                with self.subTest(servo=servo, value=value):
                    angles = dict.fromkeys(SERVO_IDS, '90')
                    angles[servo] = value
                    with self.assertRaisesRegex(ValueError, servo):
                        frame_segments(angles, '200')

    def test_missing_servo_is_rejected(self):
        from frame import frame_segments
        for servo in SERVO_IDS:
            angles = dict.fromkeys(SERVO_IDS, '90')
            del angles[servo]
            with self.assertRaisesRegex(ValueError, servo):
                frame_segments(angles, '200')

    def test_invalid_delays(self):
        from frame import frame_segments
        for delay in ('-1', '', '1.5', 'NaN', None):
            with self.subTest(delay=delay), self.assertRaisesRegex(ValueError, 'Delay'):
                frame_segments(dict.fromkeys(SERVO_IDS, '90'), delay)


class AssetTests(unittest.TestCase):
    def test_asset_path_is_independent_of_working_directory(self):
        previous = Path.cwd()
        try:
            with tempfile.TemporaryDirectory() as elsewhere:
                os.chdir(elsewhere)
                self.assertEqual(studio.asset_path('sesame-topdown.png'), STUDIO / 'sesame-topdown.png')
        finally:
            os.chdir(previous)

    def test_missing_pillow_uses_tk_fallback_with_absolute_paths(self):
        app = studio.SesameStudioApp.__new__(studio.SesameStudioApp)
        app.canvas = Mock()
        image = Mock()
        image.subsample.return_value = image
        image.height.return_value = 100
        with patch.dict(sys.modules, {'PIL': None}), patch.object(Path, 'is_file', return_value=True), \
                patch.object(studio.tk, 'PhotoImage', return_value=image) as photo:
            app.draw_robot_schematic()
        self.assertEqual([call.kwargs['file'] for call in photo.call_args_list],
                         [STUDIO / 'sesame-topdown.png', STUDIO / 'sesame-angle-guide.png'])
        app.canvas.config.assert_called_once_with(height=200)

    def test_missing_images_are_safe(self):
        app = studio.SesameStudioApp.__new__(studio.SesameStudioApp)
        app.canvas = Mock()
        with patch.dict(sys.modules, {'PIL': None}), patch.object(Path, 'is_file', return_value=False):
            app.draw_robot_schematic()
        app.canvas.create_image.assert_not_called()
        app.canvas.config.assert_called_once_with(height=0)


if __name__ == '__main__':
    unittest.main()
