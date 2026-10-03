"""Pure validation and code generation; no GUI or robot access."""

SERVO_GROUPS = (('R1', 'L2', 'R2', 'L1'), ('R3', 'R4', 'L3', 'L4'))
SERVO_LIMITS = {
    'R1': (45, 180), 'L2': (45, 180),
    'R2': (0, 135), 'L1': (0, 135),
    'R3': (0, 180), 'R4': (0, 180), 'L3': (0, 180), 'L4': (0, 180),
}


def frame_segments(angles, delay):
    """Return (text, optional tag) pairs only after all inputs validate.

    Keep the firmware's existing servo symbols, command order and angle limits.
    Inputs are strings from the editor. Delays are non-negative integer ms.
    """
    try:
        delay_ms = int(delay)
        if delay_ms < 0:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError('Delay must be a non-negative integer') from None

    values = {}
    for servo, (minimum, maximum) in SERVO_LIMITS.items():
        try:
            value = int(angles[servo])
            if not minimum <= value <= maximum:
                raise ValueError
        except (ValueError, TypeError, KeyError):
            raise ValueError(
                f'Invalid angle for Servo {servo}, range is {minimum} - {maximum}'
            ) from None
        values[servo] = value

    segments = [('// Frame\n', None)]
    for group in SERVO_GROUPS:
        segments.extend((f'setServoAngle({servo}, {values[servo]}); ', f'servo_{servo}')
                        for servo in group)
        segments.append(('\n', None))
    segments.append((f'delay({delay_ms});\n\n', None))
    return segments
