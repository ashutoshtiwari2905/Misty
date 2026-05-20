from unittest import result
import mistyvoicefuncs
import mistyctrlfuncs
import speech_recognition as sr
import time
import re
import sys








def listen_commands():
    recognizer = sr.Recognizer()

    while True:
        try:            
            mistyvoicefuncs.startnstoplapmain("output.wav")      
            mistyvoicefuncs.mistystt("output.wav")

            with open("mistydoi.txt", "r") as file:
                text = file.read()           
            

            mistyctrlfuncs.execute_command(text)


        except sr.UnknownValueError:
            print("Sorry, could not understand audio.")

        except sr.RequestError as e:
            print(f"API error: {e}")

        except KeyboardInterrupt:
            print("*program terminated*")
            sys.exit(0)

        except Exception as e:
            print("🔥 ERROR:", e)

        time.sleep(1)  # small delay before next listen

def listen_command():
    recognizer = sr.Recognizer()

    while True:
        try:
            with sr.Microphone() as source:
                print("🎧 Listening...")

                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            print("⌛ Recognizing...")
            text = recognizer.recognize_google(audio)
            print(text)

            if re.search(rf"Terminate", text, re.IGNORECASE):
                print("*Program Terminated*")
                sys.exit(0)

            else:
                mistyctrlfuncs.execute_command(text)

        except sr.UnknownValueError:
            print("Sorry, could not understand audio.")

        except sr.RequestError as e:
            print(f"API error: {e}")

        except KeyboardInterrupt:
            print("*program terminated*")
            sys.exit(0)

        except Exception as e:
            print("🔥 ERROR:", e)

        time.sleep(1)  # small delay before next listen



listen_commands()


















