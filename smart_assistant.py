from audio import *
from command import *
import json
import openai
from reflow_oven_def import *
import time

# Replace with your Whisper ASR and ChatGPT API keys
openai.api_key = ""


class SmartAssistant:

    def __init__(self, reflow_oven_control: ReflowOvenControl):
        self.__reflow_oven_control = reflow_oven_control

        self.__current_oven_temp = 30
        self.__previous_response = ""
        self.__user_input = ""
        self.__user_new_input = ""

    def __ai_interact(self):
        self.__reflow_oven_control.smart_assist_prompt.put(
            "Recording\naudio input")
        audio_data = record_audio(duration=5)

        if REPLAY_AUDIO:
            play_audio(audio_data)

        self.__reflow_oven_control.smart_assist_prompt.put(
            "Processing\naudio input")
        self.__user_new_input = voice_to_text(audio_data)
        if PRINT_EVEYTHING:
            print(f"Recognized text: {self.__user_new_input}")

        prompt = """

        This is the instruction:

            You have been asked to [request]

            Respond to this request sent to a diy-reflow_soldering_oven only in JSON format which will be interpreted by an application code to execute the actions:

            - "command": change the state of the oven 
            
            You would have to give the final "command" based on the oven initail state temperature: {0} celsius
            
            Details about the response JSON:
            
            {{
                "command":{{
                    "heat_up": "True"
                }},

                "target_temperature":[
                    {{"state": "initial_state", "time": 0, "temperature":30}},
                    {{"state": "preheating", "time":60, "temperature":150}},
                    {{"state": "recirculation", "time":140, "temperature":160}},
                    {{"state": "reflow", "time":200, "temperature":250}},
                    {{"state": "cooling", "time":350, "temperature":30}}
                ],
                
                "comment": {{
                    "text": "you will need to add some comment here"
                }}
                
            }}
            


            The "target_temperature" property should be the generated desired heating temperature:
                The content of the property should contain 5 timestamp in seconds and the temperature in celsius, the first point must be 0 second and the current oven temperature(obtain by first requesting "query" )
                The maximum heating rate of the oven is 5 celsius per second.
                The maximum cooling rate of the oven is 1 celsius per second.
                
            The "comment" property should be commenting on what you do to the target_temperature and add some additional information about the modification if any.

            Only output the response in JSON format! Do not add additional repsonse text.
            Generate the "target_temperature" based on your training data experiences.
            
        This is the request:

            previous reponse: {1}

            User's request: {2}
            
            User's additonal request: {3}
            
            Modify the response JSON based on previous response and User's additional request, if any. 

        """.format(self.__current_oven_temp, self.__previous_response,
                   self.__user_input, self.__user_new_input)

        self.__reflow_oven_control.smart_assist_prompt.put(
            "Generating\nsmart output")
        response = generate_command(prompt)
        self.__previous_response = response
        if PRINT_EVEYTHING:
            print(f"Generated command: {response}")

        start_index = response.find("{")
        end_index = response.rfind("}")
        jason_response = response[start_index:end_index + 1]
        if PRINT_EVEYTHING:
            print(f'Generated json:\n{jason_response}')

        data = json.loads(jason_response)
        temp_setting = []
        time_setting = []
        for i in range(5):
            temp_setting.append(data["target_temperature"][i]["temperature"])
            time_setting.append(data["target_temperature"][i]["time"])
        self.__reflow_oven_control.smart_assist_temp_setting.put(temp_setting)
        self.__reflow_oven_control.smart_assist_time_setting.put(time_setting)

        if PRINT_EVEYTHING:
            print(f'Generated dict:\n{data}')

        self.__reflow_oven_control.smart_assist_prompt.put("Audio response")
        comment_text = data["comment"]["text"]
        text_to_speech(comment_text)

    def run(self):
        while True:
            while not self.__reflow_oven_control.start_listen_event.is_set(
            ) and not self.__reflow_oven_control.reset_event.is_set():
                time.sleep(0.1)

            if self.__reflow_oven_control.reset_event.is_set():
                return

            self.__ai_interact()

            self.__reflow_oven_control.start_listen_event.clear()

            self.__reflow_oven_control.smart_assist_prompt.put(
                "Press button to\nstart listen")
            self.__reflow_oven_control.finish_listen_event.set()

    __reflow_oven_control = None

    __current_oven_temp = None
    __previous_response = None
    __user_input = None
    __user_new_input = None


if __name__ == "__main__":
    smart_assitant = SmartAssistant()
    smart_assitant.run()
