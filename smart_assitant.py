import openai
import json
import time

# import RPi.GPIO as GPIO
# import sounddevice as sd
# import numpy as np
# import io
# # install ffmpeg for pydub
# from pydub import AudioSegment
# import tempfile

from audio import *
from command import * 


# Replace with your Whisper ASR and ChatGPT API keys
openai.api_key = "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"

# # Configure GPIO for oven control
# GPIO.setmode(GPIO.BOARD)
# OVEN_PIN = 12  # Change this to the GPIO pin you're using
# GPIO.setup(OVEN_PIN, GPIO.OUT)


def get_audio_input():
    # Record audio for 5 seconds
    audio_data = record_audio(duration=5)
    
    # Play audio back using default output device
    play_audio(audio_data)
    
    # Convert audio to text using Whisper ASR API
    print("Converting voice to text...")
    text = voice_to_text(audio_data)
    print(f"Recognized text: {text}")
    
    return text
    

def get_command(current_oven_temp, previous_response, user_input, user_new_input):
    
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

    """.format(current_oven_temp, previous_response, user_input, user_new_input)
    
    
    # Use ChatGPT API to generate a command based on the text
    print("Generating command...")
    
    response = generate_command(prompt)
    
    previous_response = response
    
    print(f"Generated command: {response}")
    
    start_index = response.find("{")
    end_index = response.rfind("}")
    
    response = response[start_index:end_index+1]
    
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    print(response)
    
    data = json.loads(response)
    
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(data)

    comment_text = data["comment"]["text"]

    text_to_speech(comment_text)

    # print(f'Comment: {}')
    
    
class SmartAssistant:
    def __init__(self):
        self.current_oven_temp = "35"
        self.previous_response = "None"
        self.user_input = ""
        self.user_new_input = ""
        
    def run(self):
        # print("Welcome to the smart assistant!")
        while True
            while not start_audio_event.is_set():
                time.sleep(0.1)
                
            
        input_flag = True   
        self.user_input = get_audio_input()
        while True:
            if input_flag:
                get_command(self.current_oven_temp, self.previous_response, self.user_input, self.user_new_input)
                input_flag = False
            determine = input()
            if determine == "yes" or determine == "1":
                input_flag = True
                self.user_new_input = get_audio_input()

    
            
smart_assitant = SmartAssistant()

smart_assitant.run()

