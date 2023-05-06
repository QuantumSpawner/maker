from reflow_oven_def import *
import threading
import time

if not FAKE_I2C:
    import smbus


class MessageHandler:

    def __init__(self, reflow_oven_control: ReflowOvenControl):
        self.__reflow_oven_control = reflow_oven_control

        if not FAKE_I2C:
            self.__i2c = smbus.SMBus(1)

        self.__wait_to_srart_thread = threading.Thread(target=self.__start)
        self.__wait_to_srart_thread.start()

    def __start(self):
        while not self.__reflow_oven_control.start_event.is_set(
        ) and not self.__reflow_oven_control.reset_event.is_set():
            time.sleep(0.1)

        if self.__reflow_oven_control.reset_event.is_set():
            return

        self.__started = True
        print("temp_settings: " +
              str(self.__reflow_oven_control.temp_setting.get()))
        print("time_setting: " +
              str(self.__reflow_oven_control.time_setting.get()))

    def run(self):
        while not self.__reflow_oven_control.reset_event.is_set():
            if FAKE_I2C:
                self.__reflow_oven_control.temp.put(40)
                self.__reflow_oven_control.time.put(self.__fake_time)
                if self.__started:
                    self.__fake_time += 10
            else:
                self.__reflow_oven_control.temp.put(
                    self.__i2c.read_word(SLAVE_ADDRESS, 0x00))
                self.__reflow_oven_control.time.put(
                    self.__i2c.read_word(SLAVE_ADDRESS, 0x01))

            time.sleep(1)

    __i2c = None

    __reflow_oven_control = None

    __wait_to_srart_thread = None

    __fake_time = 0

    __started = False
