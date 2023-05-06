#!/usr/bin/env python3

from display import Display
from message_handler import MessageHandler
from reflow_oven_def import *
import threading


class ReflowOven:

    def __init__(self):
        self.__reflow_oven_control = ReflowOvenControl()

        self.__message_handler = MessageHandler(self.__reflow_oven_control)
        self.__message_handler_thread = threading.Thread(
            target=self.__message_handler.run)

        self.__display = Display(self.__reflow_oven_control)

    def run(self):
        self.__message_handler_thread.start()

        self.__display.run()

        self.__message_handler_thread.join()

    __reflow_oven_control = None

    __message_handler = None
    __message_handler_thread = None

    __display = None


if __name__ == "__main__":
    reflow_oven = ReflowOven()
    reflow_oven.run()
