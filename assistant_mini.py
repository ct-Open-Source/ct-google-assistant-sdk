import json
import google.oauth2.credentials
from google.assistant.library import Assistant
from google.assistant.library.event import EventType
import RPi.GPIO as GPIO
from subprocess import call
import threading
from time import sleep

led_pin = 4
button_pin = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(button_pin, GPIO.IN)
muted = False

def mute(assistant):

  global muted
  while True:
    GPIO.wait_for_edge(button_pin, GPIO.RISING)
    sleep(.5)
    print('button')
    muted = not muted
    assistant.set_mic_mute(muted)

def process_event(event, assistant):

  if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
    call(["mpg123", "ding.mp3"])
    print("Bitte sprechen Sie jetzt.")
  elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
    command = event.args['text']
    print("Antworte")

    if command == 'turn LED on':
      assistant.stop_conversation()
      GPIO.output(led_pin, True)
    elif command == 'turn LED off':
      assistant.stop_conversation()
      GPIO.output(led_pin, False)

with open(
    "/home/pi/.config/google-oauthlib-tool/credentials.json",'r'
  ) as f:
  credentials = google.oauth2.credentials.Credentials(
    token=None,**json.load(f)
  )

  with Assistant(credentials) as assistant:
    button_thread = threading.Thread(target=mute, args=(assistant,))
    button_thread.start()

    print("Warte auf Hotword")
    for event in assistant.start():
      process_event(event, assistant)

