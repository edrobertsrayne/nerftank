"""
TB6612FNG Single Motor Control Class for MicroPython
"""

from machine import Pin


class Motor:
    def __init__(self, in1, in2, pwm, stby=None, offset=0):
        """
        Initialize a single motor

        Args:
            in1 (Pin): First input pin
            in2 (Pin): Second input pin
            pwm (Pin): PWM control pin
            stby (Pin): Standby pin (can be shared between multiple motors)
            offset (float): Speed offset for motor calibration (0-1)
        """
        self.in1 = Pin(in1, Pin.OUT)
        self.in2 = Pin(in2, Pin.OUT)
        self.pwm = Pin(pwm, Pin.OUT)
        self.stby = Pin(stby, Pin.OUT) if stby else None
        self.offset = offset

        # Ensure motor starts in stopped state
        self.stop()

    @staticmethod
    def _constain(value, min_value, max_value):
        if value < min_value:
            return min_value
        if value > max_value:
            return max_value
        return value

    def forward(self, speed):
        """
        Run motor forward at specified speed

        Args:
            speed (float): Motor speed from 0 to 1
        """
        speed = self._constain(speed, 0, 1023)
        self.in1.value(1)
        self.in2.value(0)
        self.pwm.value(int(speed * (1 - self.offset)))
        self.stby.value(1) if self.stby else None

    def reverse(self, speed):
        """
        Run motor in reverse at specified speed

        Args:
            speed (float): Motor speed from 0 to 1
        """
        speed = self._constain(speed, 0, 1023)
        self.in1.value(0)
        self.in2.value(1)
        self.pwm.value(int(speed * (1 - self.offset)))
        self.stby.value(1) if self.stby else None

    def stop(self):
        """Stop the motor"""
        self.in1.value(0)
        self.in2.value(0)
        self.pwm.value(0)
        self.stby.value(0) if self.stby else None

    def brake(self):
        """
        Actively brake the motor (different from stop)
        by setting both inputs high
        """
        self.in1.value(1)
        self.in2.value(1)
        self.pwm.value(0)
        self.stby.value(1) if self.stby else None
