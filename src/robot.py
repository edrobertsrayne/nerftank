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
    def _map(
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
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def update(self, data: dict):
        print(data)

    def drive(self, speed: float, turn: float):
        """
        Drive the robot.

        :param speed: Speed of the robot (-100 to 100)
        :param turn: Turn of the robot (-100 to 100)
        """
        speed = self._map(speed, -100, 100, -1023, 1023)
        turn = self._map(turn, -100, 100, -511, 511)

        left_speed = speed - turn
        right_speed = speed + turn

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
