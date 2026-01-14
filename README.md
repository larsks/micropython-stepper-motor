# MicroPython Stepper Motor Driver

Code to drive a [28BYJ-48] motor attached to a [ULN2003] driver.

[28BYJ-48]: https://www.mouser.com/datasheet/2/758/stepd-01-data-sheet-1143075.pdf
[ULN2003]: https://en.wikipedia.org/wiki/ULN2003A

## Overview

The module [motor.py](motor.py) implements the following classes:

- `FullStepMotor` -- This class drives a stepper motor using full steps, which
  with the 28BYJ-48 means 2048 steps for a single rotation.

- `HalfStepMotor` -- This class drives a stepper motor using half steps, so
  4096 steps for a single rotation.

## API

Motor objects support the following methods:

- `zero()` -- set the current position as position 0.
- `step(n)` -- move forward (positive `n`) or backwards (negative `n`) the given number of steps
- `step_until(position)` -- move motor to the given position. By default the motor will move in the shortest direction, but you can force a direction with the optional `dir` keyword argument (`1` for forward, `-1` for reverse).
- `step_until_angle(angle)` -- move motor to the given angle.

## Examples

If you have a ULN2003 connected to a [Wemos D1] on pins D5, D6, D7, D8,
like this ([pinout][]):

[wemos d1]: https://www.wemos.cc/en/latest/d1/
[pinout]: https://escapequotes.net/esp8266-wemos-d1-mini-pins-and-diagram/

| Wemos pin   | ULN2003 pin |
| ----------- | ----------- |
| D5 (GPIO14) | IN1         |
| D6 (GPIO12) | IN2         |
| D7 (GPIO13) | IN3         |
| D8 (GPIO15) | IN4         |

Then you could create a `HalfStepMotor` object like this:

```python
import motor
m = motor.HalfStepMotor.frompins(14,12,13,15)
```

Once you have a motor object, you can run it forward:

```python
m.step(500)
```

Or backwards:

```python
m.step(-500)
```

You can run it to a specific position:

```python
m.step_until(2000)
```

Or to a specific angle:

```python
m.step_until_angle(270)
```

When using the `step_until*` methods, the motor will by default move
in the direction of shortest distance. You can force a direction with
the optional `dir` keyword argument:

```python
m.step_until(2000, dir=-1)
```
