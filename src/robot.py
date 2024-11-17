from tb6612fng import Motor
from turret import Turret
import utils


class Robot:

    max_value = 150

    def __init__(self, left_motor_pins: list, right_motor_pins: list):
        """
        Initialize the robot with left and right motor pins.

        :param left_motor_pins: List of pin numbers for the left motors
        :param right_motor_pins: List of pin numbers for the right motors
        """
        self.left_motors = [Motor(pin[0], pin[1], pin[2]) for pin in left_motor_pins]
        self.right_motors = [Motor(pin[0], pin[1], pin[2]) for pin in right_motor_pins]

        self.turret = Turret(pan=19, tilt=18, trigger=23, fire=4)

    @staticmethod
    def _apply_deadzone(value, deadzone):
        """Helper method to handle deadzone and rescaling"""
        if abs(value) < deadzone:
            return 0

        sign = 1 if value > 0 else -1
        # Rescale the remaining range using max_value
        scaled = (
            (abs(value) - deadzone) * Robot.max_value / (Robot.max_value - deadzone)
        )
        return sign * max(0, min(Robot.max_value, scaled))

    @staticmethod
    def ramp_cubic(value, deadzone=0):
        if abs(value) < deadzone:
            return 0
        # Apply deadzone and rescale
        value = Robot._apply_deadzone(value, deadzone)
        # Apply cubic function
        normalized = value / Robot.max_value
        ramped = normalized * normalized * normalized
        return int(ramped * Robot.max_value)

    @staticmethod
    def ramp_quadratic(value, deadzone=0):
        if abs(value) < deadzone:
            return 0
        # Apply deadzone and rescale
        value = Robot._apply_deadzone(value, deadzone)
        # Apply quadratic function
        sign = 1 if value >= 0 else -1
        normalized = abs(value) / Robot.max_value
        ramped = normalized * normalized
        return int(sign * ramped * Robot.max_value)

    @staticmethod
    def ramp_exponential(value, deadzone=0, exponent=1.5):
        if abs(value) < deadzone:
            return 0
        # Apply deadzone and rescale
        value = Robot._apply_deadzone(value, deadzone)
        # Apply exponential function
        sign = 1 if value >= 0 else -1
        normalized = abs(value) / Robot.max_value
        ramped = pow(normalized, exponent)
        return int(sign * ramped * Robot.max_value)

    def update(self, data: dict):
        speed = float(data["drive"]["y"])
        turn = float(data["drive"]["x"])
        pan = float(data["turret"]["x"])
        tilt = float(data["turret"]["y"])

        # apply a ramp function with a small deadzone
        speed = self.ramp_cubic(speed, deadzone=10)
        turn = self.ramp_cubic(turn, deadzone=10)

        self.drive(speed, turn)
        self.turret.move(pan, tilt)

    def drive(self, speed: float, turn: float):
        """
        Drive the robot.

        :param speed: Speed of the robot (-100 to 100)
        :param turn: Turn of the robot (-100 to 100)
        """
        speed = utils.map(speed, -Robot.max_value, Robot.max_value, -1023, 1023)
        turn = utils.map(turn, -Robot.max_value, Robot.max_value, -511, 511)

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
