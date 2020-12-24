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

        self._dir = 1
        self._pos = 0
        self._running = False
        self._state = 0
        self._target = None
        self._steps = None
        self._timer = machine.Timer(-1)

    def __repr__(self):
        return '<{} @ {}>'.format(
            self.__class__.__name__,
            self.pos,
        )

    @property
    def pos(self):
        return self._pos

    @property
    def running(self):
        return self._running

    @classmethod
    def frompins(cls, *pins, **kwargs):
        return cls(*[machine.Pin(pin, machine.Pin.OUT) for pin in pins],
                   **kwargs)

    def zero(self):
        self._pos = 0

    # adance one step
    def _step(self):
        state = self.states[self._state]

        for i, val in enumerate(state):
            self.pins[i].value(val)

        self._state = (self._state + self._dir) % len(self.states)
        self._pos = (self._pos + self._dir) % self.maxpos

    # advance one step unless we have reached self._target
    def _step_target(self):
        if self._pos == self._target:
            self.stop()
            return

        self._step()

    # advance one step unless we have already completed self._steps steps
    def _step_count(self):
        if self._steps == 0:
            self.stop()
            return

        self._steps -= 1

        self._step()

    def setTarget(self, target):
        if target is None:
            self._target = None
            return

        if target < 0 or target > self.maxpos:
            raise ValueError(target)

        self._target = target

        self._dir = 1 if target > self._pos else -1
        if abs(target - self._pos) > self.maxpos//2:
            self._dir = -self._dir

    def setDirection(self, dir):
        if dir not in [-1, 1]:
            raise ValueError(dir)

        self._dir = dir

    def runSteps(self, steps):
        if self._running:
            raise ValueError('already running')

        self._running = True
        self._dir = 1 if steps >= 0 else -1
        self._steps = abs(steps)
        self._timer.init(mode=machine.Timer.PERIODIC, period=self.stepms, callback=lambda t: self._step_count())

    def runToTarget(self, target, dir=None):
        if self._running:
            raise ValueError('already running')

        self.setTarget(target)
        if dir is not None:
            self.setDirection(dir)

        self._running = True
        self._timer.init(mode=machine.Timer.PERIODIC, period=self.stepms, callback=lambda t: self._step_target())

    def runToAngle(self, angle, dir=None):
        if self._running:
            raise ValueError('already running')

        if angle < 0 or angle > 360:
            raise ValueError(angle)

        target = int(self.maxpos / 360 * angle)

        self.setTarget(target)
        if dir is not None:
            self.setDirection(dir)

        self._running = True
        self._timer.init(mode=machine.Timer.PERIODIC, period=self.stepms, callback=lambda t: self._step_target())

    def stop(self):
        self._running = False
        self._timer.deinit()

    def wait(self):
        while self._running:
            time.sleep_ms(500)


class FullStepMotor(Motor):
    stepms = 5
    maxpos = 2048
    states = [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
        [1, 0, 0, 1],
    ]


class HalfStepMotor(Motor):
    stepms = 3
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
