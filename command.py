import openai
# import RPi.GPIO as GPIO
# import io

GPT_API_MODEL = "text-davinci-003"  # Change this to your preferred GPT model

def generate_command(prompt):
    completions = openai.Completion.create(
        engine=GPT_API_MODEL,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return completions.choices[0].text.strip()


# def control_oven_temperature(OVEN_PIN, command):
#     if "target_temperature" in command:
        
#         GPIO.output(OVEN_PIN, GPIO.HIGH)
        
#     elif "turn off" in command:
#         # Turn off the oven (use your oven's API or relay module)
#         # Example: oven.turn_off()
#         GPIO.output(OVEN_PIN, GPIO.LOW)
#     else:
#         print("Command not recognized.")
#     return
