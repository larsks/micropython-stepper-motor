import machine

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

        self._dir = 1
        self._pos = 0
        self._running = False
        self._state = 0
        self._target = None
        self._timer = machine.Timer(-1)

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

    def _step(self, dir=None):
        if self._pos == self._target:
            return self.stop()

        if dir is None:
            dir = self._dir

        if dir not in [-1, 1]:
            raise ValueError(dir)

        state = self.states[self._state]

        self._state = (self._state + dir) % len(self.states)
        self._pos = (self._pos + dir) % self.maxpos

        for i, val in enumerate(state):
            self.pins[i].value(val)

    def step(self, steps):
        dir = 1 if steps >= 0 else -1
        self.setTarget(self.pos + steps, dir)
        self.start()

    def step_until(self, target, dir=None):
        self.setTarget(target, dir=dir)
        self.start()

    def step_until_angle(self, angle, dir=None):
        target = int(angle / 360 * self.maxpos)
        self.step_until(target, dir=dir)

    def start(self):
        if self._running:
            raise ValueError('already running')

        self._running = True
        self._timer.init(mode=machine.Timer.PERIODIC, period=self.stepms, callback=lambda t: self._step())

    def stop(self):
        self._running = False
        self._timer.deinit()

    def setTarget(self, target, dir=None):
        target = target % self.maxpos

        self._target = target % self.maxpos

        if dir is None:
            dir = 1 if target > self._pos else -1
            if abs(target - self._pos) > self.maxpos//2:
                dir = -dir

        self._dir = dir


class FullStepMotor(Motor):
    stepms = 7
    maxpos = 2048
    states = [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
        [1, 0, 0, 1],
    ]


class HalfStepMotor(Motor):
    stepms = 5
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
