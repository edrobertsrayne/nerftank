from tb6612fng import Motor


class Robot:
    def __init__(self):
        self.left_motors = [Motor(14, 12, 13), Motor(15, 16, 17)]
        self.right_motors = [Motor(14, 12, 13), Motor(15, 16, 17)]

    @staticmethod
    def _map(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def drive(self, speed, turn):
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
