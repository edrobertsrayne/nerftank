from machine import PWM, Pin
from utime import sleep_ms


class Servo:
    """
    A class to control standard hobby servo motors using MicroPython.
    Compatible with ESP32 and Raspberry Pi Pico boards.

    Standard servo specs:
    - Frequency: 50Hz (20ms period)
    - Pulse width range: 500µs (0°) to 2500µs (180°)
    - Neutral position: 1500µs (90°)
    """

    def __init__(self, pin, min_us=500, max_us=2500, freq=50):
        """
        Initialize servo on specified pin.

        Args:
            pin: Pin number where servo is connected
            min_us: Minimum pulse width in microseconds (default: 500)
            max_us: Maximum pulse width in microseconds (default: 2500)
            freq: PWM frequency in Hz (default: 50)
        """
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)

        self._min_us = min_us
        self._max_us = max_us
        self._freq = freq
        self._period = 1000000 // freq  # Period in microseconds

        # Calculate duty cycle range (12-bit resolution: 0-4095)
        self._min_duty = self._us_to_duty(min_us)
        self._max_duty = self._us_to_duty(max_us)

        # Current position tracking
        self._current_us = None
        self._current_angle = None

    def _us_to_duty(self, us):
        """Convert microseconds to duty cycle value."""
        return int((us * 4095) // self._period)

    def _duty_to_us(self, duty):
        """Convert duty cycle value to microseconds."""
        return (duty * self._period) // 4095

    def write_microseconds(self, us):
        """
        Set the servo position by specifying pulse width in microseconds.

        Args:
            us: Pulse width in microseconds (typically 500-2500)
        """
        if us < self._min_us:
            us = self._min_us
        elif us > self._max_us:
            us = self._max_us

        duty = self._us_to_duty(us)
        self.pwm.duty_u16(duty << 4)  # Convert 12-bit to 16-bit
        self._current_us = us
        self._current_angle = self._us_to_angle(us)

    def write(self, angle):
        """
        Set the servo position by specifying angle in degrees.

        Args:
            angle: Position in degrees (0-180)
        """
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180

        us = self._angle_to_us(angle)
        self.write_microseconds(us)

    def read_microseconds(self):
        """
        Read the current servo position in microseconds.

        Returns:
            Current pulse width in microseconds or None if position unknown
        """
        return self._current_us

    def read(self):
        """
        Read the current servo position in degrees.

        Returns:
            Current angle in degrees or None if position unknown
        """
        return self._current_angle

    def _angle_to_us(self, angle):
        """Convert angle to microseconds."""
        return int(self._min_us + (angle * (self._max_us - self._min_us) / 180))

    def _us_to_angle(self, us):
        """Convert microseconds to angle."""
        return int((us - self._min_us) * 180 / (self._max_us - self._min_us))

    def calibrate(self, min_us=None, max_us=None):
        """
        Calibrate the servo's minimum and maximum pulse widths.

        Args:
            min_us: New minimum pulse width in microseconds
            max_us: New maximum pulse width in microseconds
        """
        if min_us is not None:
            self._min_us = min_us
            self._min_duty = self._us_to_duty(min_us)
        if max_us is not None:
            self._max_us = max_us
            self._max_duty = self._us_to_duty(max_us)

    def detach(self):
        """Stop sending pulses to the servo."""
        self.pwm.duty_u16(0)

    def center(self):
        """Move servo to center position (90 degrees)."""
        self.write(90)

    def sweep(self, start_angle=0, end_angle=180, delay_ms=500):
        """
        Sweep the servo between specified angles.

        Args:
            start_angle: Starting angle in degrees
            end_angle: Ending angle in degrees
            delay_ms: Delay between positions in milliseconds
        """
        self.write(start_angle)
        sleep_ms(delay_ms)
        self.write(end_angle)
        sleep_ms(delay_ms)
