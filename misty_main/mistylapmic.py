import mistyctrlfuncs
import speech_recognition as sr
import time
import re
import sys
import pyttsx3
engine = pyttsx3.init()





def listen_command_with_wake_word():
    recognizer = sr.Recognizer()

    while True:
        try:
            with sr.Microphone(device_index=1) as source:
                print("🎧 Listening...")
                engine.say("Listening.")
                engine.runAndWait()


                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            print("⌛ Recognizing...")
            text = recognizer.recognize_google(audio)
            print(text)

            
            
            if re.search(rf"misty|chemistry|miss t|misht|misst|mish t", text, re.IGNORECASE):
                mistyctrlfuncs.execute_command(text)

            elif re.search(rf"Terminate", text, re.IGNORECASE):
                print("*Program Terminated*")
                sys.exit(0)


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



listen_command_with_wake_word()


















