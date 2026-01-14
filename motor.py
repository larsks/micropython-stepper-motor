import time

import machine

# Thanks to:
# https://youtu.be/B86nqDRskVU


class Motor:
    stepms: int = 10

    # To be defined by subclasses
    maxpos: int = 0
    states: list[list[int]] = []

    def __init__(
        self,
        p1: machine.Pin,
        p2: machine.Pin,
        p3: machine.Pin,
        p4: machine.Pin,
        stepms: int | None = None,
    ):
        self.pins: list[machine.Pin] = [p1, p2, p3, p4]

        if stepms is not None:
            self.stepms = stepms

        self._state: int = 0
        self._pos: int = 0

    def __repr__(self):
        return "<{} @ {}>".format(
            self.__class__.__name__,
            self.pos,
        )

    @property
    def pos(self):
        return self._pos

    @classmethod
    def frompins(cls, *pins: int, stepms: int | None = None):
        return cls(*[machine.Pin(pin, machine.Pin.OUT) for pin in pins], stepms=stepms)

    def zero(self):
        self._pos = 0

    def _step(self, dir: int):
        state = self.states[self._state]

        for i, val in enumerate(state):
            self.pins[i].value(val)  # pyright: ignore[reportUnusedCallResult]

        self._state = (self._state + dir) % len(self.states)
        self._pos = (self._pos + dir) % self.maxpos

    def step(self, steps: int):
        dir = 1 if steps >= 0 else -1
        steps = abs(steps)

        for _ in range(steps):
            t_start = time.ticks_ms()

            self._step(dir)

            t_end = time.ticks_ms()
            t_delta = time.ticks_diff(t_end, t_start)
            time.sleep_ms(self.stepms - t_delta)

    def step_until(self, target: int, dir: int | None = None):
        if target < 0 or target > self.maxpos:
            raise ValueError(target)

        if dir is None:
            dir = 1 if target > self._pos else -1
            if abs(target - self._pos) > self.maxpos / 2:
                dir = -dir

        while True:
            if self._pos == target:
                break
            self.step(dir)

    def step_until_angle(self, angle: int, dir: int | None = None):
        if angle < 0 or angle > 360:
            raise ValueError(angle)

        target = int(angle / 360 * self.maxpos)
        self.step_until(target, dir=dir)


class FullStepMotor(Motor):
    stepms: int = 5
    maxpos: int = 2048
    states: list[list[int]] = [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
        [1, 0, 0, 1],
    ]


class HalfStepMotor(Motor):
    stepms: int = 3
    maxpos: int = 4096
    states: list[list[int]] = [
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 1],
        [1, 0, 0, 1],
    ]
