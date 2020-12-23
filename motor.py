import machine
import time

# Thanks to:
# https://youtu.be/B86nqDRskVU


class Motor:
    stepms = 10

    # Do be defined by subclasses
    maxpos = 0
    states = []

    def __init__(self, p1, p2, p3, p4, stepms=None):
        self.pins = [p1, p2, p3, p4]

        if stepms is not None:
            self.stepms = stepms

        self._state = 0
        self._pos = 0

    def __repr__(self):
        return '<{} @ {}>'.format(
            self.__class__.__name__,
            self.pos,
        )

    @property
    def pos(self):
        return self._pos

    @classmethod
    def frompins(cls, *pins, **kwargs):
        return cls(*[machine.Pin(pin, machine.Pin.OUT) for pin in pins],
                   **kwargs)

    def zero(self):
        self._pos = 0

    def step(self, steps):
        if steps < 0:
            steps = abs(steps)
            dir = -1
        else:
            dir = 1

        for _ in range(steps):
            t_start = time.ticks_ms()
            state = self.states[self._state]

            if dir == 1:
                self._state = (self._state + 1) % len(self.states)
                self._pos = (self._pos + 1) % self.maxpos
            elif dir == -1:
                self._state = (self._state - 1) % len(self.states)
                self._pos = (self._pos - 1) % self.maxpos

            for i, val in enumerate(state):
                self.pins[i].value(val)

            t_end = time.ticks_ms()
            t_delta = time.ticks_diff(t_end, t_start)
            time.sleep_ms(self.stepms - t_delta)

    def step_until(self, target, dir=None):
        if target < 0 or target > self.maxpos:
            raise ValueError(target)

        delta = target - self.pos
        steps = abs(delta)

        if dir is None and delta < 0:
            dir = -1
        elif dir is None:
            dir = 1

        if delta < 0 and dir == 1:
            steps = delta % self.maxpos
        elif delta > 0 and dir == -1:
            steps = (0-delta) % self.maxpos

        print('target', target, 'pos', self.pos,
              'delta', delta, 'steps', steps,
              'dir', dir)

        self.step(steps * dir)

    def step_until_angle(self, angle, dir=None):
        target = angle / 360 * self.maxpos
        self.step_until(target, dir=dir)


class FullStepMotor(Motor):
    maxpos = 2048
    states = [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
        [1, 0, 0, 1],
    ]


class HalfStepMotor(Motor):
    maxpos = 4096
    states = [
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 1],
        [1, 0, 0, 1],
    ]
