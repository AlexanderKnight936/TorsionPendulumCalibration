
import time as time

class PIDControl(kP, kI, kD):
    def __init__(self):
        self.P = kP
        self.I = kI
        self.D = kD

        # the state of the loop
        self.setpoint = 0
        self.position = 0
        self.offset = 0
        # the previous state of the loop
        self.lastSetpoint = 0
        self.lastPosition = 0
        self.lastOffset = 0

        self.output = 0

    def runloop(setpoint, position):
        # update the last position etc with the old data
        self.lastSetpoint = self.setpoint
        self.lastPosition = self.position
        self.lastOffset = self.offset

        # update the gains with the passed in values.
        self.setpoint = setpoint
        self.position = position
        self.offset = setpoint - position # swap these to make the output have the right sign

        # claculate the pid gains
        proportional = self.P * self.offset
        integral += self.I * ()
        # calculate the output from the pid gains
        self.output = () + (self.I * self.)

        return
