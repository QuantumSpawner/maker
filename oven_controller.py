import math
import numpy as np
from reflow_oven_def import *
import RPi.GPIO as GPIO
import smbus
import time


def ln(V):
    return math.log10(V) / math.log10(math.e)


class PIDcontroller:

    def __init__(self):
        self.Kp = 0.0
        self.Ki = 0.0
        self.Kd = 0.0

        self.deltaTime = 0

        # derivitive low-pass time constant
        self.tau = 0.0

        # output limits
        self.limMin = 0.0
        self.limMax = 0.0

        # integrator limits
        self.limMinInt = 0.0
        self.limMaxInt = 0.0

        # controller memory
        self.integrator = 0.0
        self.prevError = 0.0
        self.differentiator = 0.0
        self.prevMeasurement = 0.0

        self.out = 0

    def pidInit(self, deltaTime, limMin, limMax, limMinInt, limMaxInt, Kp, Ki,
                Kd):
        self.integrator = 0.0
        self.prevError = 0.0
        self.differentiator = 0.0
        self.prevMeasurement = 0.0
        self.out = 0.0

        self.deltaTime = deltaTime
        self.limMax = limMax
        self.limMin = limMin
        self.limMaxInt = limMaxInt
        self.limMinInt = limMinInt
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

    def pidUpdate(self, setpoint, measurement):

        error = setpoint - measurement
        proportional = error * self.Kp
        self.integrator = self.integrator + 0.5 * self.Ki * self.deltaTime * (
            error + self.prevError)

        # compute integrator clamping
        if (self.limMax > proportional):
            self.limMaxInt = self.limMax - proportional
        else:
            self.limMaxInt = 0.0

        if (self.limMin < proportional):
            self.limMinInt = self.limMin - proportional
        else:
            self.limMinInt = 0.0

        if (self.integrator > self.limMaxInt):
            self.integrator = self.limMaxInt
        elif (self.integrator < self.limMinInt):
            self.integrator = self.limMinInt

        # derivative
        self.differentiator = -(
            2.0 * self.Kd * (measurement - self.prevMeasurement) +
            (2.0 * self.tau - self.deltaTime) * self.differentiator) / (
                2.0 * self.tau + self.deltaTime)

        self.out = proportional + self.integrator + self.differentiator

        # output limit
        if (self.out > self.limMax):
            self.out = self.limMax
        elif (self.out < self.limMin):
            self.out = self.limMin

        # store error and measurement for later use
        self.prevError = error
        self.prevMeasurement = measurement

        return self.out


class NTC:

    def __init__(self):
        self._ratio = 0
        self._val = 0
        self._R = 0
        self._V = 0
        self._T = 0

    def set_ratio(self, ratio):
        self._ratio = ratio

    def set_val(self, val):
        self._val = val

    def val2V(self):
        V = self._val * self._ratio

    def V2R(self, Vref):
        self._R = 10000.0 * self._V / (Vref - self._V)

    def R2T(self):
        self._T = 1 / (0.0054 + (1 / 3444.5) *
                       (ln(self._R / 1000) - 4 * ln(10))) - 273.15
        if self._T <= 0:
            self._T = 0

    def get_Temp(self):
        return self._T


class OvenController:

    def __init__(self, reflow_oven_control: ReflowOvenControl):
        self.__reflow_oven_control = reflow_oven_control

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY_PIN, GPIO.OUT)
        self.__i2c = smbus.SMBus(1)
        self.__ntc = [NTC(), NTC()]
        self.__ntc[0].set_ratio(5 / 65536)
        self.__ntc[1].set_ratio(5 / 65536)
        self.__pid = PIDcontroller()
        self.__pid.pidInit(PID_DELTA_TIME, 0, 1200, 0, 600, PID_KP, PID_KI,
                           PID_KD)

    def run(self):
        while not self.__reflow_oven_control.reset_event.is_set():
            temp_data = [
                self.__i2c.read_word_data(ADC_ADDRESS, TEMP_ADDRESS),
                self.__i2c.read_word_data(ADC_ADDRESS, TEMP_ADDRESS)
            ]
            temp = []

            for i in range(2):
                self.__ntc[i].set_val(temp_data[i])
                self.__ntc[i].val2V()
                self.__ntc[i].V2R(5)
                self.__ntc[i].R2T()
                temp.append(self.__ntc[i].get_Temp())

            temp_avg = (temp[0] + temp[1]) / 2
            self.__reflow_oven_control.temp.put(temp_avg)
            if self.__time_passed > self.__time_profile[-1]:
                self.__started = False
                self.__reflow_oven_control.time.put(0)
            else:
                self.__reflow_oven_control.time.put(self.__time_passed)

            if self.__reflow_oven_control.start_event.is_set(
            ) and not self.__started:
                self.__started = True
                self.__reflow_oven_control.start_event.clear()
                self.__temp_profile = self.__reflow_oven_control.temp_setting.get(
                )
                self.__time_profile = self.__reflow_oven_control.time_setting.get(
                )

            if self.__started:
                target_temp = np.interp(self.__time_passed,
                                        self.__time_profile,
                                        self.__temp_profile)
                on_time = self.__pid.pidUpdate(target_temp, temp_avg) / 1000
                if on_time > 1:
                    on_time = 1
                off_time = 1 - on_time

                GPIO.output(RELAY_PIN, GPIO.HIGH)
                time.sleep(on_time)
                GPIO.output(RELAY_PIN, GPIO.LOW)
                time.sleep(off_time)

            else:
                time.sleep(1)

            self.__time_passed += 1

    __reflow_oven_control = None

    __i2c = None
    __ntc = None

    __pid = None

    __started = False
    __temp_profile = None
    __time_profile = None
    __time_passed = 0
