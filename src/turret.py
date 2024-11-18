from servo import Servo
from machine import Pin, PWM
from robot import RobotController
import utils

PAN_MIN = 500
PAN_MAX = 2500
TILT_MIN = 1250
TILT_MAX = 2000
TRIGGER_MIN = 1400
TRIGGER_MAX = 2500


class Turret:
    def __init__(self, pan, tilt, trigger, fire):
        self.pan_servo = Servo(pan)
        self.tilt_servo = Servo(tilt)
        self.trigger_servo = Servo(trigger)
        self.fire_motor = PWM(Pin(fire))

        self.pan_servo.write_microseconds((PAN_MIN + PAN_MAX) // 2)
        self.tilt_servo.write_microseconds((TILT_MIN + PAN_MAX) // 2)
        self.trigger_servo.write_microseconds(TRIGGER_MAX)

    def move(self, pan, tilt):
        pan = utils.map(
            pan,
            -RobotController.MAX_JOYSTICK_VALUE,
            RobotController.MAX_JOYSTICK_VALUE,
            PAN_MIN,
            PAN_MAX,
        )
        tilt = utils.map(
            tilt,
            -RobotController.MAX_JOYSTICK_VALUE,
            RobotController.MAX_JOYSTICK_VALUE,
            TILT_MIN,
            TILT_MAX,
        )

        pan = self.pan_servo.write_microseconds(pan)
        tilt = self.tilt_servo.write_microseconds(tilt)
