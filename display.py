from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os
import time
import tkinter as tk
from tkinter import ttk
from reflow_oven_def import *
import requests


class Display:

    def __init__(self, reflow_oven_control: ReflowOvenControl):
        ########################################################################
        # back end                                                             #
        ########################################################################
        self.__reflow_oven_control = reflow_oven_control

        ########################################################################
        # front end                                                            #
        ########################################################################
        # create the main window
        self.main_window = tk.Tk()
        self.main_window.title("Reflow Oven")
        self.main_window.geometry("800x480")

        # configure grid
        for i in range(self.NUM_ROWS):
            self.main_window.rowconfigure(i, minsize=20)
        for i in range(self.NUM_COLUMNS):
            self.main_window.columnconfigure(i, minsize=20)

        if SHOW_GRID:
            for i in range(self.NUM_ROWS):
                for j in range(self.NUM_COLUMNS):
                    if (i + j) % 2 == 0:
                        tk.Label(self.main_window,
                                 background='#fff').grid(row=i,
                                                         column=j,
                                                         sticky=tk.NSEW)
                    else:
                        tk.Label(self.main_window,
                                 background='#888').grid(row=i,
                                                         column=j,
                                                         sticky=tk.NSEW)

        # property
        if FULL_SCREEN:
            self.main_window.attributes("-fullscreen", True)

        # labels ###############################################################
        # add a lable to show time to the main window
        if LABELS and TIME_LABEL:
            self.__time_label = tk.Label(self.main_window)
            self.__time_label.grid(row=22,
                                   column=34,
                                   rowspan=2,
                                   columnspan=6,
                                   sticky=tk.NSEW)
            self.__periodic_update_time_label()

        # add a mode label for selecting mode to the main window
        if LABELS and MODE_LABEL:
            self.__mode_label = tk.Label(self.main_window,
                                         text="MODE",
                                         font=("", 14))
            self.__mode_label.grid(row=16,
                                   column=2,
                                   rowspan=3,
                                   columnspan=5,
                                   sticky=tk.NSEW)

        # add a mode label for selecting profile to the main window
        if LABELS and PROFILE_LABEL:
            self.__profile_label = tk.Label(self.main_window,
                                            text="PROFILE",
                                            font=("", 14))
            self.__profile_label.grid(row=16,
                                      column=16,
                                      rowspan=3,
                                      columnspan=5,
                                      sticky=tk.NSEW)

        # add a time passed label for showing remaining time to the main window
        if LABELS and TIME_PASSED_LABEL:
            self.__time_passed_label = tk.Label(self.main_window,
                                                text="Passed\n0:00",
                                                font=("", 12))
            self.__time_passed_label.grid(row=19,
                                          column=2,
                                          rowspan=3,
                                          columnspan=5,
                                          sticky=tk.NSEW)

        # add a time remaining label for showing remaining time to the main
        # window
        if LABELS and TIME_REMAINING_LABEL:
            sec = self.PROFILES[0][2][4] % 60
            min = self.PROFILES[0][2][4] // 60
            self.__time_remaining_label = tk.Label(
                self.main_window,
                text=f"Remaining\n{min}:{sec:02d}",
                font=("", 12))
            self.__time_remaining_label.grid(row=19,
                                             column=25,
                                             rowspan=3,
                                             columnspan=5,
                                             sticky=tk.NSEW)

        # add a current temperature label for showing current temperature to
        # the main window
        if LABELS and CURRENT_TEMP_LABEL:
            self.__current_temp_label = tk.Label(
                self.main_window,
                text=f"Temp: {self.__real_temp_point[-1]}\N{DEGREE SIGN}C",
                font=("", 18))
            self.__current_temp_label.grid(row=2,
                                           column=26,
                                           rowspan=2,
                                           columnspan=12,
                                           sticky=tk.NSEW)

        # add a total time label for showing total time to the main window
        if LABELS and TOTAL_TIME_LABEL:
            sec = self.PROFILES[0][2][4] % 60
            min = self.PROFILES[0][2][4] // 60
            self.__total_time_label = tk.Label(
                self.main_window,
                text=f"Total Time: {min}:{sec:02d}",
                font=("", 18))
            self.__total_time_label.grid(row=4,
                                         column=26,
                                         rowspan=2,
                                         columnspan=12,
                                         sticky=tk.NSEW)

        # add a stage scrolling label to show the currently selected heating to
        # set  profile to the main window
        if LABELS and STAGE_SCROLL_LABEL:
            self.__stage_scroll_label = tk.Label(self.main_window,
                                                 text=self.REFLOW_STAGE[0],
                                                 font=("", 18))
            self.__stage_scroll_label.grid(row=6,
                                           column=28,
                                           rowspan=2,
                                           columnspan=8,
                                           sticky=tk.NSEW)

        # add a termperature setting label to show the setting for temperature
        # to the main window
        if LABELS and TEMP_SETTING_LABEL:
            self.__temp_setting_label = tk.Label(
                self.main_window,
                text=f"Temp Setting: {self.PROFILES[0][1][1]}\N{DEGREE SIGN}C",
                font=("", 14))
            self.__temp_setting_label.grid(row=8,
                                           column=26,
                                           rowspan=2,
                                           columnspan=12,
                                           sticky=tk.NSEW)

        # add a period setting label to show the setting for period to the main
        # window
        if LABELS and PERIOD_SETTING_LABEL:
            self.__period_setting_label = tk.Label(
                self.main_window,
                text=f"Period Setting: {self.PROFILES[0][2][1]}s",
                font=("", 14))
            self.__period_setting_label.grid(row=12,
                                             column=26,
                                             rowspan=2,
                                             columnspan=12,
                                             sticky=tk.NSEW)

        # add a smart assist prompt label to show the smart assist prompt to
        # the main window
        if LABELS and SMART_ASSIST_PROMPT_LABEL:
            self.__smart_assist_prompt_label = tk.Label(self.main_window,
                                                        font=("", 18))

        # progress bar #########################################################
        # add a progress bar for showing heating process to the main window
        if PROGRESS_BAR:
            self.__progress_bar = ttk.Progressbar(self.main_window,
                                                  orient=tk.HORIZONTAL,
                                                  length=100,
                                                  mode='determinate')
            self.__progress_bar.grid(row=19,
                                     column=7,
                                     rowspan=3,
                                     columnspan=18,
                                     sticky=tk.NSEW)
            self.__progress_bar['value'] = 0

        # chart ################################################################
        # add a temperature chart to the main window
        if TEMP_CHART:
            self.__temp_figure = plt.Figure(figsize=(12, 7), dpi=39)

            self.__temp_axle = self.__temp_figure.add_subplot(111)
            if TEMP_POINT:
                self.__temp_line, = self.__temp_axle.plot(self.__time_point,
                                                          self.__temp_point,
                                                          label='Temp Setting')
                self.__temp_line.set_linewidth(10)
            if REAL_TEMP_POINT:
                self.__real_temp_line, = self.__temp_axle.plot(
                    self.__real_time_point,
                    self.__real_temp_point,
                    label='Real Temp')
                self.__real_temp_line.set_linewidth(10)
            self.__temp_axle.set_title("Temperature Chart", fontsize=36)
            self.__temp_axle.set_xlabel("Time (s)", fontsize=28)
            self.__temp_axle.set_ylabel("Temp (\N{DEGREE SIGN}C)", fontsize=28)
            self.__temp_axle.tick_params(axis='both', labelsize=20)
            self.__temp_axle.legend(loc='best', fontsize=24)

            self.__temp_canvas = FigureCanvasTkAgg(self.__temp_figure,
                                                   master=self.main_window)
            self.__temp_canvas.draw()
            self.__temp_canvas.get_tk_widget().grid(row=2,
                                                    column=2,
                                                    rowspan=14,
                                                    columnspan=24)

        # buttons ##############################################################
        # add a shutdown button to the main window
        if BUTTONS and SHUTDOWN_BUTTON:
            self.__shutdown_button_image = tk.PhotoImage(
                file="image/power_button.png")
            self.__shutdown_button = tk.Button(
                self.main_window,
                image=self.__shutdown_button_image,
                background='#f00',
                command=self.__on_shutdown_button_click)
            self.__shutdown_button.grid(row=0,
                                        column=38,
                                        rowspan=2,
                                        columnspan=2,
                                        sticky=tk.NSEW)

        # add a settings button to the main window
        if BUTTONS and SETTINGS_BUTTON:
            self.__settings_button_image = tk.PhotoImage(
                file="image/settings.png")
            self.__settings_button = tk.Button(
                self.main_window, image=self.__settings_button_image)
            self.__settings_button.grid(row=22,
                                        column=0,
                                        rowspan=2,
                                        columnspan=2,
                                        sticky=tk.NSEW)

        # add a wifi button to the main window
        if BUTTONS and WIFI_BUTTON:
            self.__wifi_button_image = tk.PhotoImage(file="image/wifi.png")
            self.__no_wifi_button_image = tk.PhotoImage(
                file="image/no_wifi.png")
            self.__wifi_button = tk.Button(self.main_window,
                                           command=self.__on_wifi_button_click,
                                           image=self.__wifi_button_image)
            self.__wifi_button.grid(row=0,
                                    column=36,
                                    rowspan=2,
                                    columnspan=2,
                                    sticky=tk.NSEW)
            self.__periodic_check_wifi()

        # add a mode button for selecting mode to the main window
        if BUTTONS and MODE_BUTTON:
            self.__mode_button = tk.Button(self.main_window,
                                           command=self.__on_mode_button_click,
                                           text="Manual",
                                           font=("", 14))
            self.__mode_button.grid(row=16,
                                    column=7,
                                    rowspan=3,
                                    columnspan=9,
                                    sticky=tk.NSEW)

        # add a profile button for selecting profile to the main window
        if BUTTONS and PROFILE_BUTTON:
            self.__profile_button = tk.Button(
                self.main_window,
                command=self.__on_profile_button_click,
                text=self.PROFILES[0][0],
                font=("", 14))
            self.__profile_button.grid(row=16,
                                       column=21,
                                       rowspan=3,
                                       columnspan=9,
                                       sticky=tk.NSEW)

        # add a stage scroll left button for scrolling left the stage to the
        # main window
        if BUTTONS and STAGE_SCROLL_LEFT_BUTTON:
            self.__scroll_left_button_image = tk.PhotoImage(
                file="image/left_arrow.png")
            self.__stage_scroll_left_button = tk.Button(
                self.main_window,
                command=self.__on_stage_scroll_left_button_click,
                image=self.__scroll_left_button_image)
            self.__stage_scroll_left_button.grid(row=6,
                                                 column=26,
                                                 rowspan=2,
                                                 columnspan=2,
                                                 sticky=tk.NSEW)

        # add a stage scroll right button for scrolling right the stage to the
        # main window
        if BUTTONS and STAGE_SCROLL_RIGHT_BUTTON:
            self.__scroll_right_button_image = tk.PhotoImage(
                file="image/right_arrow.png")
            self.__stage_scroll_right_button = tk.Button(
                self.main_window,
                command=self.__on_stage_scroll_right_button_click,
                image=self.__scroll_right_button_image)
            self.__stage_scroll_right_button.grid(row=6,
                                                  column=36,
                                                  rowspan=2,
                                                  columnspan=2,
                                                  sticky=tk.NSEW)

        # add a smart assist start listen button to the main window
        if BUTTONS and SMART_ASSIST_START_LISTEN_BUTTON:
            self.__smart_assist_start_listen_button = tk.Button(
                self.main_window,
                command=self.__on_smart_assist_start_listen_button_click,
                text="Start Listen",
                font=("", 18))

        # add a start button to start heating to the main window
        if BUTTONS and START_BUTTON:
            self.__start_button = tk.Button(
                self.main_window,
                command=self.__on_start_button_click,
                text="START",
                font=("", 20, "bold"),
                background='#0f0')
            self.__start_button.grid(row=16,
                                     column=30,
                                     rowspan=6,
                                     columnspan=8,
                                     sticky=tk.NSEW)

        # sliders ##############################################################
        # add a temperature slider for tuning temperature to the main window
        if SLIDERS and TEMP_SLIDER:
            self.__temp_slider = tk.Scale(self.main_window,
                                          from_=self.MIN_TEMP,
                                          to=self.MAX_TEMP,
                                          command=self.__on_temp_slider_change,
                                          resolution=self.SLIDER_RESOLUTION,
                                          showvalue=False,
                                          tickinterval=50,
                                          width=14,
                                          orient=tk.HORIZONTAL)
            self.__temp_slider.set(self.__temp_point[1])
            self.__temp_slider.grid(row=10,
                                    column=26,
                                    rowspan=2,
                                    columnspan=12,
                                    sticky=tk.NSEW)

        # add a period slider for tuning period to the main window
        if SLIDERS and PERIOD_SLIDER:
            period_min = (self.DEFAULT_TEMP -
                          self.MIN_TEMP) / self.HEATING_REATE
            self.__period_slider = tk.Scale(
                self.main_window,
                from_=period_min,
                to=self.MAX_PERIOD,
                command=self.__on_period_slider_change,
                resolution=self.SLIDER_RESOLUTION,
                showvalue=False,
                tickinterval=60,
                width=14,
                orient=tk.HORIZONTAL)
            self.__period_slider.set(self.__time_point[1])
            self.__period_slider.grid(row=14,
                                      column=26,
                                      rowspan=2,
                                      columnspan=12,
                                      sticky=tk.NSEW)

        # start periodic update
        self.__period_update()

    # callback functions #######################################################
    def __shutdown(self):
        # TODO: add shutdown logic here
        self.main_window.destroy()

    # button
    def __on_shutdown_button_click(self):
        self.__shutdown_dialog = tk.Toplevel(self.main_window)
        self.__shutdown_dialog.title("Shutdown")
        self.__shutdown_dialog.resizable(False, False)
        label = tk.Label(self.__shutdown_dialog, text="Choose an option:")
        label.pack(
            padx=10,
            pady=10,
        )

        options_frame = tk.Frame(self.__shutdown_dialog)
        options_frame.pack()

        options = ["Shutdown", "Reboot", "Reset", "Cancel"]

        for option in options:
            button = tk.Button(options_frame,
                               text=option,
                               command=lambda opt=option: self.
                               __shutdown_dialog_response(opt))
            button.pack(side='left', padx=5, pady=5)

    def __on_wifi_button_click(self):
        if self.__wifi_connected:
            tk.messagebox.showinfo(
                "WiFi", "WiFi is connected.\nSmart assistant is available.")
        else:
            tk.messagebox.showerror(
                "WiFi",
                "WiFi is not connected.\nSmart assistant is not available.")

    def __on_mode_button_click(self):
        if self.__smart_assist:

            self.__smart_assist = False

            self.__show_smart_assist_settings(False)
            self.__show_manual_settings(True)
            self.__profile_button.config(state=tk.ACTIVE)

            self.__mode_button.config(text="Manual")
        elif self.__wifi_connected:
            self.__smart_assist = True

            self.__show_manual_settings(False)
            self.__show_smart_assist_settings(True)
            self.__profile_button.config(state=tk.DISABLED)

            self.__mode_button.config(text="Smart Assistant")
        else:
            tk.messagebox.showerror(
                "Smart Assistant",
                "WiFi is not connected.\nSmart assistant is not available.")

    def __on_profile_button_click(self):
        self.__profile_index = (self.__profile_index + 1) % self.NUM_PROFILES
        self.__temp_point = self.PROFILES[self.__profile_index][1].copy()
        self.__time_point = self.PROFILES[self.__profile_index][2].copy()
        self.__profile_button.config(
            text=self.PROFILES[self.__profile_index][0])

        # restore previous slider value
        self.__temp_slider.set(self.__temp_point[self.__stage_index + 1])
        self.__period_slider.set(self.__time_point[self.__stage_index + 1] -
                                 self.__time_point[self.__stage_index])
        self.__update_temp_slider_bar_range()
        self.__update_period_slider_bar_range()
        self.__update_temp_chart()
        self.__update_time_lable()

    def __on_stage_scroll_left_button_click(self):
        self.__stage_index = (self.__stage_index - 1) % self.NUM_REFLOW_STAGES

        # restore previous slider value
        self.__temp_slider.set(self.__temp_point[self.__stage_index + 1])
        self.__period_slider.set(self.__time_point[self.__stage_index + 1] -
                                 self.__time_point[self.__stage_index])
        self.__update_temp_slider_bar_range()
        self.__update_period_slider_bar_range()

        self.__stage_scroll_label.config(
            text=self.REFLOW_STAGE[self.__stage_index])

    def __on_stage_scroll_right_button_click(self):
        self.__stage_index = (self.__stage_index + 1) % self.NUM_REFLOW_STAGES

        # restore previous slider value
        self.__temp_slider.set(self.__temp_point[self.__stage_index + 1])
        self.__period_slider.set(self.__time_point[self.__stage_index + 1] -
                                 self.__time_point[self.__stage_index])
        self.__update_temp_slider_bar_range()
        self.__update_period_slider_bar_range()

        self.__stage_scroll_label.config(
            text=self.REFLOW_STAGE[self.__stage_index])

    def __on_smart_assist_start_listen_button_click(self):
        self.__reflow_oven_control.start_listen_event.set()
        self.__smart_assist_start_listen_button.config(state=tk.DISABLED)
        self.__period_update_smart_assist()

    def __on_start_button_click(self):
        if not self.__started:
            self.__started = True

            # send start signal and settings
            self.__reflow_oven_control.temp_setting.put(self.__temp_point)
            self.__reflow_oven_control.time_setting.put(self.__time_point)
            self.__reflow_oven_control.start_event.set()

            self.__start_button.config(text="STOP", background='#f00')

            # lock setting buttons and sliders
            self.__mode_button.config(state=tk.DISABLED)
            self.__profile_button.config(state=tk.DISABLED)
            self.__stage_scroll_left_button.config(state=tk.DISABLED)
            self.__stage_scroll_right_button.config(state=tk.DISABLED)
            self.__temp_slider.config(state=tk.DISABLED)
            self.__period_slider.config(state=tk.DISABLED)

        else:
            answer = tk.messagebox.askquestion(
                "Confirm", "Do you want to stop? This will cause a reset.")
            if answer == "yes":
                self.__reflow_oven_control.reset_event.set()
                self.__shutdown()

    # silder
    def __on_temp_slider_change(self, value):
        if float(value) != self.__temp_point[self.__stage_index + 1]:
            self.__change_to_custom_profile()

        self.__temp_point[self.__stage_index + 1] = float(value)
        self.__temp_setting_label.config(
            text=f"Temp Setting: {value}\N{DEGREE SIGN}C")

        self.__update_period_slider_bar_range()
        self.__update_time_lable()
        self.__update_temp_point_value()
        self.__update_temp_chart()

    def __on_period_slider_change(self, value):
        if float(value) != self.__time_point[self.__stage_index +
                                             1] - self.__time_point[
                                                 self.__stage_index]:
            self.__change_to_custom_profile()

        self.__time_point[
            self.__stage_index +
            1] = self.__time_point[self.__stage_index] + float(value)
        self.__period_setting_label.config(text=f"Period Setting: {value}s")

        self.__update_time_point_value()
        self.__update_time_lable()
        self.__update_temp_chart()

    # timed callback functions #################################################
    def __periodic_check_wifi(self):
        try:
            request = requests.get("http://www.google.com", timeout=5)
            if not self.__wifi_connected:
                self.__wifi_connected = True
                self.__wifi_button.config(image=self.__wifi_button_image)
        except (requests.ConnectionError, requests.Timeout):
            if self.__wifi_connected:
                self.__wifi_connected = False
                self.__wifi_button.config(image=self.__no_wifi_button_image)
            if self.__smart_assist:
                self.__smart_assist = False
                tk.messagebox.showerror(
                    "Smart Assistant",
                    "WiFi is not connected.\nSmart assistant is not available."
                )

        self.main_window.after(10000, self.__periodic_check_wifi)

    def __periodic_update_time_label(self):
        current_time = time.strftime('%H:%M:%S')
        current_date = time.strftime('%b %d, %Y')
        self.__time_label.config(text=f"{current_date}\n{current_time}")
        self.main_window.after(1000, self.__periodic_update_time_label)

    def __period_update(self):
        if not self.__reflow_oven_control.temp.empty():
            temp = self.__reflow_oven_control.temp.get()
            time = self.__reflow_oven_control.time.get()

            if self.__started:
                self.__real_temp_point.append(temp)
                self.__real_time_point.append(time)

                self.__update_time_lable()
                self.__progress_bar['value'] = time / (
                    self.__time_point[-1] - self.__time_point[0]) * 100
                self.__update_temp_chart()

            else:
                self.__real_temp_point[-1] = temp

            self.__current_temp_label.config(
                text=f"Temp: {self.__real_temp_point[-1]}\N{DEGREE SIGN}C")

        self.main_window.after(1000, self.__period_update)

    def __period_update_smart_assist(self):
        if not self.__reflow_oven_control.smart_assist_prompt.empty():
            self.__smart_assist_prompt_label.config(
                text=self.__reflow_oven_control.smart_assist_prompt.get())

        if self.__reflow_oven_control.finish_listen_event.is_set():
            self.__reflow_oven_control.finish_listen_event.clear()
            self.__smart_assist_start_listen_button.config(state=tk.ACTIVE)
        else:
            self.main_window.after(100, self.__period_update_smart_assist)

    # other functions ##########################################################
    def __shutdown_dialog_response(self, opt):
        if opt == "Shutdown":
            answer = tk.messagebox.askquestion(
                "Confirm", "Do you really want to shutdown RPi?")
            if answer == "yes":
                self.__reflow_oven_control.reset_event.set()
                time.sleep(3)
                os.system("shutdown now")
            else:
                self.__shutdown_dialog.destroy()
        elif opt == "Reboot":
            answer = tk.messagebox.askquestion(
                "Confirm", "Do you really want to restart RPi?")
            if answer == "yes":
                self.__reflow_oven_control.reset_event.set()
                time.sleep(3)
                os.system("reboot")
            else:
                self.__shutdown_dialog.destroy()
        elif opt == "Reset":
            answer = tk.messagebox.askquestion(
                "Confirm", "Do you really want to reset the system?")
            if answer == "yes":
                self.__reflow_oven_control.reset_event.set()
                self.__shutdown()
            else:
                self.__shutdown_dialog.destroy()
        else:
            self.__shutdown_dialog.destroy()

    def __change_to_custom_profile(self):
        if self.__profile_index != -1:
            self.__profile_index = -1
            self.__profile_button.config(text="Custom")

    def __show_manual_settings(self, show):
        if show:
            self.__stage_scroll_label.grid(row=6,
                                           column=28,
                                           rowspan=2,
                                           columnspan=8,
                                           sticky=tk.NSEW)
            self.__temp_setting_label.grid(row=8,
                                           column=26,
                                           rowspan=2,
                                           columnspan=12,
                                           sticky=tk.NSEW)
            self.__period_setting_label.grid(row=12,
                                             column=26,
                                             rowspan=2,
                                             columnspan=12,
                                             sticky=tk.NSEW)
            self.__stage_scroll_left_button.grid(row=6,
                                                 column=26,
                                                 rowspan=2,
                                                 columnspan=2,
                                                 sticky=tk.NSEW)
            self.__stage_scroll_right_button.grid(row=6,
                                                  column=36,
                                                  rowspan=2,
                                                  columnspan=2,
                                                  sticky=tk.NSEW)
            self.__temp_slider.grid(row=10,
                                    column=26,
                                    rowspan=2,
                                    columnspan=12,
                                    sticky=tk.NSEW)
            self.__period_slider.grid(row=14,
                                      column=26,
                                      rowspan=2,
                                      columnspan=12,
                                      sticky=tk.NSEW)
        else:
            self.__stage_scroll_label.grid_forget()
            self.__temp_setting_label.grid_forget()
            self.__period_setting_label.grid_forget()
            self.__stage_scroll_left_button.grid_forget()
            self.__stage_scroll_right_button.grid_forget()
            self.__temp_slider.grid_forget()
            self.__period_slider.grid_forget()

    def __show_smart_assist_settings(self, show):
        if show:
            self.__smart_assist_prompt_label.config(
                text="Press button to\nstart listen")
            self.__smart_assist_prompt_label.grid(row=6,
                                                  column=26,
                                                  rowspan=5,
                                                  columnspan=12,
                                                  sticky=tk.NSEW)
            self.__smart_assist_start_listen_button.grid(row=11,
                                                         column=26,
                                                         rowspan=5,
                                                         columnspan=12,
                                                         sticky=tk.NSEW)
        else:
            self.__smart_assist_prompt_label.grid_forget()
            self.__smart_assist_start_listen_button.grid_forget()

    def __update_temp_point_value(self):
        if self.__temp_point[2] < self.__temp_point[1]:
            self.__temp_point[2] = self.__temp_point[1]

        if self.__temp_point[3] < self.__temp_point[2]:
            self.__temp_point[3] = self.__temp_point[2]

        if self.__temp_point[4] > self.__temp_point[3]:
            self.__temp_point[4] = self.__temp_point[3]

    def __update_time_point_value(self):
        for i in range(4):
            period_min = (
                self.__temp_point[i + 1] -
                (self.MIN_TEMP if i == 0 else self.__temp_point[i])) / (
                    self.HEATING_REATE if i != 3 else self.COOLING_RATE)
            if self.__time_point[i + 1] < self.__time_point[i] + period_min:
                self.__time_point[i + 1] = self.__time_point[i] + period_min
            elif self.__time_point[i +
                                   1] > self.__time_point[i] + self.MAX_PERIOD:
                self.__time_point[i +
                                  1] = self.__time_point[i] + self.MAX_PERIOD

    def __update_temp_slider_bar_range(self):
        if self.__stage_index == 0:
            self.__temp_slider.config(from_=self.MIN_TEMP)
            self.__temp_slider.config(to_=self.MAX_TEMP)
        elif self.__stage_index == 3:
            self.__temp_slider.config(from_=self.MIN_TEMP)
            self.__temp_slider.config(to_=self.__temp_point[3])
            pass
        else:
            # very wierd bug that the slider bar value for cooling stage will be
            # changed to the same as soaking stage only when scrolling right by
            # this line of code
            self.__temp_slider.config(
                from_=self.__temp_point[self.__stage_index])
            self.__temp_slider.config(to_=self.MAX_TEMP)

    def __update_period_slider_bar_range(self):
        period_min = (self.__temp_point[self.__stage_index + 1] -
                      (self.MIN_TEMP if self.__stage_index == 0 else
                       self.__temp_point[self.__stage_index])) / (
                           self.HEATING_REATE
                           if self.__stage_index != 3 else self.COOLING_RATE)
        self.__period_slider.config(from_=period_min)

    def __update_temp_chart(self):
        if TEMP_POINT:
            self.__temp_line.set_data(self.__time_point, self.__temp_point)
        if REAL_TEMP_POINT:
            self.__real_temp_line.set_data(self.__real_time_point,
                                           self.__real_temp_point)
        self.__temp_axle.relim()
        self.__temp_axle.autoscale_view()
        self.__temp_canvas.draw()

    def __update_time_lable(self):
        total_time_sec = self.__time_point[4] % 60
        total_time_min = self.__time_point[4] // 60
        self.__total_time_label.config(
            text=f"Total time: {int(total_time_min)}:{int(total_time_sec):02d}"
        )

        if self.__started:
            time_passed_sec = self.__real_time_point[-1] % 60
            time_passed_min = self.__real_time_point[-1] // 60
            self.__time_passed_label.config(
                text=
                f"Passed\n{int(time_passed_min)}:{int(time_passed_sec):02d}")

            time_reamining = self.__time_point[4] - self.__real_time_point[-1]
            time_reamining_sec = time_reamining % 60
            time_reamining_min = time_reamining // 60
            self.__time_remaining_label.config(
                text=
                f"Remaining\n{int(time_reamining_min)}:{int(time_reamining_sec):02d}"
            )
        else:
            self.__time_remaining_label.config(
                text=
                f"Remaining\n{int(total_time_min)}:{int(total_time_sec):02d}")

    def run(self):
        self.main_window.mainloop()

    # config ###################################################################
    # display
    NUM_ROWS = 24
    NUM_COLUMNS = 40
    SLIDER_RESOLUTION = 10

    # reflow oven
    MAX_TEMP = 300
    MIN_TEMP = 0
    MAX_PERIOD = 300
    DEFAULT_TEMP = 200
    HEATING_REATE = 5  # degree per second
    COOLING_RATE = -5  # degree per second
    REFLOW_STAGE = ["PREHEAT", "SOAK", "REFLOW", "COOl"]
    NUM_REFLOW_STAGES = len(REFLOW_STAGE)

    # (name, temperature point, time point)
    PROFILES = [("Wikipedia", [MIN_TEMP, 150, 140, 200,
                               MIN_TEMP], [0, 60, 160, 250, 350]),
                ("Profile 2", [MIN_TEMP, 100, 150, 250,
                               MIN_TEMP], [0, 100, 200, 300, 400])]
    NUM_PROFILES = len(PROFILES)

    main_window = None

    ############################################################################
    # front end                                                                #
    ############################################################################
    # labels ###################################################################
    # utilities
    __time_label = None

    # reflow oven
    __mode_label = None
    __profile_label = None
    __profile_index = 0
    __time_passed_label = None
    __time_remaining_label = None
    __current_temp_label = None
    __total_time_label = None
    __stage_scroll_label = None
    __stage_index = 0
    __temp_setting_label = None
    __period_setting_label = None
    __smart_assist_prompt_label = None

    # progress bar #############################################################
    __progress_bar = None

    # chart ####################################################################
    __temp_figure = None
    __temp_axle = None
    __real_temp_line = None
    __temp_line = None
    __temp_canvas = None

    # buttons ##################################################################
    # utilities
    __shutdown_dialog = None
    __shutdown_button = None
    __shutdown_button_image = None
    __settings_button = None
    __settings_button_image = None
    __wifi_connected = None
    __wifi_button = None
    __wifi_button_image = None
    __no_wifi_button_image = None

    # reflow oven
    __mode_button = None
    __profile_button = None
    __stage_scroll_left_button = None
    __scroll_left_button_image = None
    __stage_scroll_right_button = None
    __scroll_right_button_image = None
    __smart_assist_start_listen_button = None
    __start_button = None

    # slider ###################################################################
    __temp_slider = None
    __period_slider = None

    ############################################################################
    # back end                                                                 #
    ############################################################################
    __reflow_oven_control = None
    __started = False
    __smart_assist = False
    __temp_point = PROFILES[0][1].copy()
    __time_point = PROFILES[0][2].copy()
    __real_temp_point = [30]
    __real_time_point = [0]


if __name__ == "__main__":
    display = Display()
    display.run()
