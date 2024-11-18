"""
TB6612FNG Single Motor Control Class for MicroPython
"""

from machine import Pin, PWM
from typing import Optional


class Motor:
    PWM_MAX = 65535
    SPEED_MAX = 1023

    def __init__(
        self,
        in1: int,
        in2: int,
        pwm: int,
        stby: Optional[int] = None,
        offset: float = 0.0,
    ) -> None:
        """
        Initialize a single motor.

        Args:
            in1: First input pin number
            in2: Second input pin number
            pwm: PWM control pin number
            stby: Standby pin number (can be shared between multiple motors)
            offset: Speed offset for motor calibration (0-1)
        """
        self.in1 = Pin(in1, Pin.OUT)
        self.in2 = Pin(in2, Pin.OUT)
        self.pwm = PWM(Pin(pwm, Pin.OUT))
        self.stby = Pin(stby, Pin.OUT) if stby else None
        self.offset = offset
        self.stop()  # Ensure motor starts in stopped state

    def _set_speed(self, speed: float) -> int:
        """
        Convert and constrain speed value.

        Args:
            speed: Raw speed value (0-1023)

        Returns:
            Adjusted PWM duty cycle value
        """
        speed = max(0, min(self.SPEED_MAX, speed))  # Constrain speed
        # Map speed from 0-1023 to 0-65535
        return int((speed / self.SPEED_MAX) * self.PWM_MAX * (1 - self.offset))

    def _set_direction(self, forward: bool, speed: float) -> None:
        """
        Set motor direction and speed.

        Args:
            forward: True for forward, False for reverse
            speed: Motor speed (0-1023)
        """
        self.in1.value(forward)
        self.in2.value(not forward)
        self.pwm.duty_u16(self._set_speed(speed))
        if self.stby:
            self.stby.value(1)

    def forward(self, speed: float) -> None:
        """
        Run motor forward at specified speed.

        Args:
            speed: Motor speed (0-1023)
        """
        self._set_direction(True, speed)

    def reverse(self, speed: float) -> None:
        """
        Run motor in reverse at specified speed.

        Args:
            speed: Motor speed (0-1023)
        """
        self._set_direction(False, speed)

    def stop(self) -> None:
        """Stop the motor by setting both inputs and PWM low."""
        self.in1.value(0)
        self.in2.value(0)
        self.pwm.duty_u16(0)
        if self.stby:
            self.stby.value(0)

    def brake(self) -> None:
        """Actively brake the motor by setting both inputs high."""
        self.in1.value(1)
        self.in2.value(1)
        self.pwm.duty_u16(0)
