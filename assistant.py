#!/usr/bin/env python

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modifications by Merlin Schumacher (mls@ct.de) for c't magazin für computer technik


import argparse
import os.path
import os
import re
import json
from time import sleep

# Import der für den Google Assistant notwendigen Module
import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file

# Import der für den Google Text-To-Speech Service notwendigen Module. Dadurch kann man eigene Sprachantworten ausgeben
from gtts import gTTS
from subprocess import call

# Import der Module für die Ansteuerung der GPIO-Pins der Raspberry Pi
import RPi.GPIO as GPIO

# Die Nummerierung folgt dem BCM-System.
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# led_pin legt den Pin einer am Raspi angeschlossenen LED fest. Sie kann per Sprachkommando ein und ausgeschaltet werden. 
led_pin = 4
# button_pin legt den Pin eines am Raspi angeschlossenen Buttons fest. 
button_pin = 14
# status_led_pin legt den Pin einer am Raspi angeschlossenen LED fest. Sie leuchtet, wenn der Assistant zuhört.
status_led_pin = 15
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(status_led_pin, GPIO.OUT)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.output(led_pin, False)
GPIO.output(status_led_pin, False)

# Muted enthält die Information ob der Assistant zuhört oder nicht.
muted = False

# Threading für das Warten auf einen Knopfdruck
import threading



# Die Funktion mute läuft als Thread und schaltet bei einem Knopfdruck den Assistant stumm.
def mute(assistant):
    global muted
    while True:
        GPIO.wait_for_edge(button_pin, GPIO.RISING)
        sleep(.5)
        print("Mute Button pressed")
        muted = not muted
        assistant.set_mic_mute(muted)


# speak_tts erzeugt aus einem übergebenen Text mittel Googles TTS-Dienst eine
# MP3-Datei. Diese wird von sox abgespielt.
# Optional kann eine Sprache angegeben werden.
def speak_tts(ttstext, language="en-us"):
    tts = gTTS(text=ttstext, lang=language)
    tts.save("answer.mp3")
    call(["mpg123", "answer.mp3"])


# turn_on_led schaltet die LED an.
def turn_on_led():
    print("LED an")
    speak_tts("Turning LED on.")
    GPIO.output(led_pin, True)


# turn_on_led schaltet die LED ab.
def turn_off_led():
    print("LED aus")
    speak_tts("Turning LED off.")
    GPIO.output(led_pin, False)

# turn_on_led schaltet die LED ab.
def shutdown():
    print("Shutdown")
    speak_tts("Powering off.")
    call(["sudo", "poweroff"])

# sagt die IP-Adresse an
def say_ip_address():
    try:
        ethernet = re.search(re.compile(r'(?<=inet )(.*)(?=\/)', re.M), os.popen('ip addr show eth0').read()).groups()[0]
    except:
        ethernet = "none"
    
    try:
        wifi = re.search(re.compile(r'(?<=inet )(.*)(?=\/)', re.M), os.popen('ip addr show wlan0').read()).groups()[0]
    except:
        wifi = "none"

    print("IPs: " + ethernet+ " " + wifi )
    speak_tts("The WiFi address is "+wifi+". The wired address is " +
              ethernet)
    GPIO.output(led_pin, False)

## process_event verarbeitet die von der Google-Assistant-Instanz zurückgegebenen Events.
def process_event(event, assistant):
     global muted
#    # Um alle Eventtypen zu sehen kommentieren Sie die nachfolgende Zeile ein.
     #print(event.type)
#
#    # Wurde das Hotword erkannt, beginnt Google mit der Aufzeichnung und Erkennung des Textes
     if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        call(["mpg123", "ding.mp3"])
        print("Bitte sprechen Sie jetzt.")
#
#    # Nach dem Ende der Spracheingabe verarbeitet der Assistant den Text.
     if event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
         command = event.args['text']
         print("Erkannter Text:"+command)
         print("Antworte")
 
         # Falls der erkannte Text einem der lokalen Befehle entspricht, wird der Dialog mit dem Assistant abgebrochen
         # und die zugehörige lokale Funktion ausgeführt.
         command = str.lower(command)
         if command == 'turn led on':
             assistant.stop_conversation()
             turn_on_led()
         elif command == 'turn led off':
             assistant.stop_conversation()
             turn_off_led()
         elif command == 'what\'s your device ip':
             assistant.stop_conversation()
             say_ip_address()
         elif command == 'shut yourself down':
             assistant.stop_conversation()
             shutdown()
        
     # Nach dem Ende der Konversation wartet Google wieder auf das Hotword. Ist das Argument 'with_follow_on_turn' wahr,
     # ist der Dialog noch nicht beendet und Google wartet auf weitere Anweisungen vom Nutzer.
     if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
         event.args and not event.args['with_follow_on_turn']):
         print("Warte auf Hotword")
     
     # Falls der Assistant ein Mute-Event auslöst, wird ein Hinweis ausgegeben
     # und die LED entspreched umgeschaltet.
     if (event.type == EventType.ON_MUTED_CHANGED):
         muted = bool(event.args['is_muted'])
         print("Assistant hört zu: " + str(not muted))
         GPIO.output(status_led_pin, not muted)


def main():
    # Mittels des Parameters --crendentials kann eine eigene Credentials-Datei angegeben werden.
    # Wurde keine angegeben, greift das Programm auf die Datei ~/.config/google-oauthlib-tool/credentials.json zurück.
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--credentials', type=existing_file,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'google-oauthlib-tool',
                            'credentials.json'
                        ),
                        help='Path to store and read OAuth2 credentials')
    args = parser.parse_args()

    # Die für die Anmeldung an Googles API notwendigen Credentials werden geladen.
    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))
        # Die Instanz des Google Assistant in assistant beginnt Ereignisse auszulösen, diese werden mittels process_event
        # verarbeitet.
        with Assistant(credentials) as assistant:
            # Started den Thread, der auf den Mute-Button reagiert
            button_thread = threading.Thread(target=mute, args=(assistant,))
            button_thread.start()
            print("Warte auf Hotword")
            for event in assistant.start():
                process_event(event, assistant)

if __name__ == '__main__':
    main()
