from servo import Servo
from machine import Pin, PWM
from enum import Enum
import utils
import uasyncio as asyncio

PAN_MIN = 500
PAN_MAX = 2500
TILT_MIN = 1250
TILT_MAX = 2000
TRIGGER_MIN = 1400
TRIGGER_MAX = 2500


class TurretState(Enum):
    STANDBY = "STANDBY"
    SPIN_UP = "SPIN_UP"
    READY = "READY"
    FIRING = "FIRING"
    COOLDOWN = "COOLDOWN"
    EMPTY = "EMPTY"


class Turret:
    def __init__(self, pan, tilt, trigger, fire):
        self.pan_servo = Servo(pan)
        self.tilt_servo = Servo(tilt)
        self.trigger_servo = Servo(trigger)
        self.fire_motor = PWM(Pin(fire))

        self.pan_servo.write_microseconds((PAN_MIN + PAN_MAX) // 2)
        self.tilt_servo.write_microseconds((TILT_MIN + PAN_MAX) // 2)
        self.trigger_servo.write_microseconds(TRIGGER_MAX)

        self._state = TurretState.STANDBY
        self._armed = asyncio.Event()
        self._firing = asyncio.Event()
        self._ammo = 5
        self._task = asyncio.create_task(self.run())

    def _get_next_state(self):
        if self._ammo < 1:
            self._state = TurretState.EMPTY

        elif not self._armed.is_set():
            self._state = TurretState.STANDBY

        elif self._state == TurretState.STANDBY:
            self._state = TurretState.SPIN_UP

        elif self._state == TurretState.SPIN_UP:
            self._state = TurretState.READY

        elif self._state == TurretState.READY:
            if self._firing.is_set():
                self._state = TurretState.FIRING

        elif self._state == TurretState.FIRING:
            self._state = TurretState.COOLDOWN

        elif self._state == TurretState.COOLDOWN:
            self._state = TurretState.READY

        else:
            raise ValueError(f"Unknown state: {self._state}")

    async def _execute_state_behaviour(self):
        if self._state == TurretState.STANDBY:
            # firing motor is off and wait for arming
            self.fire_motor.duty_u16(0)
            await self._armed.wait()

        elif self._state == TurretState.SPIN_UP:
            # spin up firing motor
            self.fire_motor.duty_u16(1 << 15)

        elif self._state == TurretState.READY:
            # do nothing
            pass

        elif self._state == TurretState.FIRING:
            # activate trigger, decrement ammo counter, and clear firing event
            self.trigger_servo.write_microseconds(TRIGGER_MIN)
            self._ammo -= 1
            self._firing.clear()
            await asyncio.sleep_ms(100)

        elif self._state == TurretState.COOLDOWN:
            # withdraw trigger and cooldown before next shot
            self.trigger_servo.write_microseconds(TRIGGER_MAX)
            await asyncio.sleep_ms(100)

        elif self._state == TurretState.EMPTY:
            # no ammuntion, do nothing
            self.fire_motor.duty_u16(0)

        else:
            raise ValueError(f"Unknown state: {self._state}")

    def arm(self):
        self._armed.set()

    def disarm(self):
        self._armed.clear()

    def fire(self):
        self._firing.set()

    @property
    def ammo(self):
        return self._ammo

    @property
    def state(self):
        return self._state

    @property
    def is_armed(self):
        return self._armed.is_set()

    async def run(self):
        while True:
            try:
                self._get_next_state()
                await self._execute_state_behaviour()
                await asyncio.sleep_ms(0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in turret state machine: {e}")
                await asyncio.sleep(1)

    def move(self, pan, tilt):
        pan = utils.map_range(pan, -1, 1, PAN_MIN, PAN_MAX)
        tilt = utils.map_range(tilt, -1, 1, TILT_MIN, TILT_MAX)

        pan = self.pan_servo.write_microseconds(pan)
        tilt = self.tilt_servo.write_microseconds(tilt)
