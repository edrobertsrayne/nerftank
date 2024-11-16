from tb6612fng import Motor


class Robot:
    def __init__(self, left_motor_pins: list, right_motor_pins: list):
        """
        Initialize the robot with left and right motor pins.

        :param left_motor_pins: List of pin numbers for the left motors
        :param right_motor_pins: List of pin numbers for the right motors
        """
        self.left_motors = [Motor(pin[0], pin[1], pin[2]) for pin in left_motor_pins]
        self.right_motors = [Motor(pin[0], pin[1], pin[2]) for pin in right_motor_pins]

    @staticmethod
    def map(
        x: float, in_min: float, in_max: float, out_min: float, out_max: float
    ) -> float:
        """
        Map a value from one range to another.

        :param x: Value to map
        :param in_min: Minimum value of the input range
        :param in_max: Maximum value of the input range
        :param out_min: Minimum value of the output range
        :param out_max: Maximum value of the output range
        :return: Mapped value
        """
        return (
            float(x - in_min) * (out_max - out_min) / float(in_max - in_min) + out_min
        )

    @staticmethod
    def _apply_deadzone(value, deadzone, max_value=100):
        """Helper method to handle deadzone and rescaling"""
        if abs(value) < deadzone:
            return 0

        sign = 1 if value > 0 else -1
        # Rescale the remaining range using max_value
        scaled = (abs(value) - deadzone) * max_value / (max_value - deadzone)
        return sign * max(0, min(max_value, scaled))

    @staticmethod
    def ramp_cubic(value, deadzone=0, max_value=100):
        if abs(value) < deadzone:
            return 0
        # Apply deadzone and rescale
        value = Robot._apply_deadzone(value, deadzone, max_value)
        # Apply cubic function
        normalized = value / max_value
        ramped = normalized * normalized * normalized
        return int(ramped * max_value)

    @staticmethod
    def ramp_quadratic(value, deadzone=0, max_value=100):
        if abs(value) < deadzone:
            return 0
        # Apply deadzone and rescale
        value = Robot._apply_deadzone(value, deadzone, max_value)
        # Apply quadratic function
        sign = 1 if value >= 0 else -1
        normalized = abs(value) / max_value
        ramped = normalized * normalized
        return int(sign * ramped * max_value)

    @staticmethod
    def ramp_exponential(value, deadzone=0, exponent=1.5, max_value=100):
        if abs(value) < deadzone:
            return 0
        # Apply deadzone and rescale
        value = Robot._apply_deadzone(value, deadzone, max_value)
        # Apply exponential function
        sign = 1 if value >= 0 else -1
        normalized = abs(value) / max_value
        ramped = pow(normalized, exponent)
        return int(sign * ramped * max_value)

    def update(self, data: dict):
        speed = float(data["drive"]["y"])
        turn = float(data["drive"]["x"])
        pan = float(data["turret"]["x"])
        tilt = float(data["turret"]["y"])

        # apply a ramp function with a small deadzone
        speed = self.ramp_cubic(speed, deadzone=10)
        turn = self.ramp_cubic(turn, deadzone=10)

        self.drive(speed, turn)

    def drive(self, speed: float, turn: float):
        """
        Drive the robot.

        :param speed: Speed of the robot (-100 to 100)
        :param turn: Turn of the robot (-100 to 100)
        """
        speed = self.map(speed, -100, 100, -1023, 1023)
        turn = self.map(turn, -100, 100, -511, 511)

        left_speed = speed + turn
        right_speed = speed - turn

        for motor in self.left_motors:
            if left_speed > 0:
                motor.forward(left_speed)
            elif left_speed < 0:
                motor.reverse(abs(left_speed))
            else:
                motor.stop()

        for motor in self.right_motors:
            if right_speed > 0:
                motor.forward(right_speed)
            elif right_speed < 0:
                motor.reverse(abs(right_speed))
            else:
                motor.stop()
