from matplotlib import text
import requests
import websocket
import json
import signal
import sys
import mistyvoicefuncs
import re
import time
import os
from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer


# This loads the variables from .env into the system environment
load_dotenv()

# Access the variables
api_key= os.getenv("api_key1") #API KEY
misty_ip = os.getenv("misty_ip") #MISTY IP


#VELOCITIES
head_velocity = 90
movement_velocity = 40
angular_velocity = 90
arm_velocity = 50



music_name = "ghoomar3.wav"


introduction = "Hello there! I m Misty, your friendly humanoid robot companion. I m here to help, learn, and explore alongside you. Whether its answering questions, solving problems, or just having a fun chat, I m always ready with curiosity and a smile. Lets make something awesome together!"

hello = "Hello everyone, i am misty. it's pleasure to meet you all!"


def detect_head_touch(misty_ip):

    last_states = {
        "HeadLeft": False,
        "HeadRight": False,
        "HeadBack": False
    }

    def handle_exit(sig, frame):
        print("*Program Terminated*")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)

    def on_open(ws):
        print("CONNECTED")

        ws.send(json.dumps({
            "$id": "1",
            "Operation": "subscribe",
            "Type": "TouchSensor",
            "DebounceMs": 100
        }))

    def on_message(ws, message):
        nonlocal last_states

        data = json.loads(message)

        if "message" in data:
            msg = data["message"]

            pos = msg.get("sensorPosition")
            current = msg.get("isContacted")

            if pos in last_states:
                if current and not last_states[pos]:
                    print("✅ HEAD SENSOR DETECTED")
                    ws.close()

                last_states[pos] = current

    ws = websocket.WebSocketApp(
        f"ws://{misty_ip}/pubsub",
        on_open=on_open,
        on_message=on_message
    )

    ws.run_forever(ping_interval=0, ping_timeout=None)


def chin_detection(misty_ip):

    last_state = False

    def handle_exit(sig, frame):
        print("*Program Terminated*")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)

    def on_open(ws):
        print("CONNECTED")

        ws.send(json.dumps({
            "$id": "1",
            "Operation": "subscribe",
            "Type": "TouchSensor",
            "DebounceMs": 100
        }))

    def on_message(ws, message):
        nonlocal last_state

        data = json.loads(message)

        if "message" in data:
            msg = data["message"]

            if msg.get("sensorPosition") == "Chin":
                current = msg.get("isContacted")

                if current and not last_state:
                    print("✅ CHIN DETECTED")
                    ws.close()        
                            
                last_state = current


    ws = websocket.WebSocketApp(
        f"ws://{misty_ip}/pubsub",
        on_open=on_open,
        on_message=on_message
    )

    ws.run_forever(ping_interval=0, ping_timeout=None)


def move_head_pitch(pitch, head_velocity):
    print("Moving head...")

    url = f"http://{misty_ip}/api/head"
    payload = {
        "Pitch": pitch,
        "Velocity": head_velocity
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, data=json.dumps(payload), headers=headers)


def move_head_roll(roll, head_velocity):
    print("Moving head...")

    url = f"http://{misty_ip}/api/head"
    payload = {
        "Roll": roll,
        "Velocity": head_velocity
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, data=json.dumps(payload), headers=headers)


def move_head_yaw(yaw, head_velocity):
    print("Moving head...")

    url = f"http://{misty_ip}/api/head"
    payload = {
        "Yaw": yaw,
        "Velocity": head_velocity
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, data=json.dumps(payload), headers=headers)


def move(linear_velocity, angular_velocity):
    print("Moving...")

    url = f"http://{misty_ip}/api/drive"

    payload = {
        "LinearVelocity": linear_velocity,   # Forward speed (+ forward, - backward)
        "AngularVelocity": angular_velocity    # Turning
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    print(response.json())


def move_arms(left_position, right_position, arm_velocity):
    url = f"http://{misty_ip}/api/arms/set"

    payload = {
        "LeftArmPosition": left_position,     # -29.0 to 90.0 degrees
        "RightArmPosition": right_position,   # -29.0 to 90.0 degrees
        "LeftArmVelocity": arm_velocity,     # 0 to 100
        "RightArmVelocity": arm_velocity
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Arms moved successfully!")
    else:
        print("Error:", response.text)


def response_generation_misty(text):
    print("Generating response...")
    mistyvoicefuncs.askgroqapi(api_key, text)

    with open("llm_response.txt", "r") as file:
        ai_text = file.read()            

    mistyvoicefuncs.mistyspeak(misty_ip, ai_text, voice="hi-IN-SwaraNeural")

    chin_detection(misty_ip)
    mistyvoicefuncs.mistystopspeak(misty_ip)


def play_music(music_name):
    
    response = requests.post(
        f"http://{misty_ip}/api/audio/play",
        json={
            "FileName": music_name,
            "Volume": 100
        }
    )

    print(response.text)


def response_generation_lap(text):
    print("Generating response...")
    mistyvoicefuncs.askgroqapi(api_key, text)

    with open("llm_response.txt", "r") as file:
        ai_text = file.read()            

    mistyvoicefuncs.mistyspeak(misty_ip, ai_text, voice="hi-IN-SwaraNeural")


def reset_position():
    print("Resetting position...")
    move(0, 0)
    move_head_pitch(0, head_velocity)
    move_head_roll(0, head_velocity)
    move_head_yaw(0, head_velocity)
    move_arms(90, 90, arm_velocity)


def stop_all_movement():
    print("Stopping all movement...")
    requests.post(f"http://{misty_ip}/api/drive/stop")





def execute_command(text):

    if re.search(r"Stop|Freeze|Hold", text, re.IGNORECASE):
        print("Stopping")
        stop_all_movement()
        mistyvoicefuncs.mistystopspeak(misty_ip)

    elif re.search(r"Reset", text, re.IGNORECASE):
        if re.search(r"Body|Position", text, re.IGNORECASE):
            reset_position()

    elif re.search(r"Say", text, re.IGNORECASE):
        print("Saying...")
    
        if re.search(r"Hello|Hi|Hey|High", text, re.IGNORECASE):
            mistyvoicefuncs.mistyspeak(misty_ip, hello, voice="hi-IN-SwaraNeural")

            for _ in range(5):
                move_arms(90, -90, arm_velocity)
                time.sleep(0.5)
                move_arms(90, 45, arm_velocity)
                time.sleep(0.5)
        
    elif re.search(r"Introduce", text, re.IGNORECASE):
        print("Introducing...")
        mistyvoicefuncs.mistyspeak(misty_ip, introduction, voice="hi-IN-SwaraNeural")

        for _ in range(10):
            move_arms(90, -90, arm_velocity)
            time.sleep(0.5)
            move_arms(90, 45, arm_velocity)
            time.sleep(0.5)

    elif re.search(r"Dance", text, re.IGNORECASE):
        print("Dancing...")
        mistyvoicefuncs.mistyspeak(misty_ip, "Okay. Let's dance!", voice="hi-IN-SwaraNeural")
        time.sleep(2)

        play_music(music_name)

        try:
            for _ in range(10):
                move(0, 120)
                move_head_roll(-50, head_velocity)
                move_arms(90, -90, arm_velocity)
                time.sleep(0.5)
                move_head_roll(50, head_velocity)
                move_arms(-90, 90, arm_velocity)
                time.sleep(0.5)

        except KeyboardInterrupt:
            print("*program terminated*")
            sys.exit(0)

        except Exception as e:
            print("🔥 ERROR:", e)

        stop_all_movement()
        reset_position()

    elif re.search(r"look", text, re.IGNORECASE):
        print("Looking")

        if re.search(r"Up", text, re.IGNORECASE):
            print("Up")

            if re.search(r"Little", text, re.IGNORECASE):
                print("a Little...")
                move_head_pitch()
            else:
                print("Full...")
                move_head_pitch(-40, head_velocity)

        elif re.search(r"Down", text, re.IGNORECASE):
            print("Down")

            if re.search(r"Little", text, re.IGNORECASE):
                print("a Little...")
                move_head_pitch()

            else:
                print("Full...")
                move_head_pitch(25, head_velocity)

        if re.search(r"Left", text, re.IGNORECASE):
            print("Left")

            if re.search(r"Little", text, re.IGNORECASE):
                print("a Little...")
                move_head_yaw()
                
            else:
                print("Full...")
                move_head_yaw(90, head_velocity)

        elif re.search(r"Right", text, re.IGNORECASE):
            print("Right")

            if re.search(r"Little", text, re.IGNORECASE):
                print("a Little...")
                move_head_yaw()

            else:
                print("Full...")
                move_head_yaw(-90, head_velocity)

        elif re.search(r"front|forward", text, re.IGNORECASE):
            print("Forward")
            
            move_head_pitch(0, head_velocity)
            move_head_roll(0, head_velocity)
            move_head_yaw(0, head_velocity)

    elif re.search(r"Move", text, re.IGNORECASE):
        print("Moving")

        if re.search(r"Head", text, re.IGNORECASE):
            print("Head")

            if re.search(r"Up", text, re.IGNORECASE):
                print("Up")

                if re.search(r"Little", text, re.IGNORECASE):
                    print("a Little...")
                    move_head_pitch()

                else:
                    print("Full...")
                    move_head_pitch(-40, head_velocity)

            elif re.search(r"Down", text, re.IGNORECASE):
                print("Down")

                if re.search(r"Little", text, re.IGNORECASE):
                    print("a Little...")
                    move_head_pitch()

                else:
                    print("Full...")
                    move_head_pitch(25, head_velocity)

            if re.search(r"Left", text, re.IGNORECASE):
                print("Left")

                if re.search(r"Little", text, re.IGNORECASE):
                    print("a Little...")
                    move_head_yaw()

                else:
                    print("Full...")
                    move_head_yaw(90, head_velocity)

            elif re.search(r"Right", text, re.IGNORECASE):
                print("Right")

                if re.search(r"Little", text, re.IGNORECASE):
                    print("a Little...")
                    move_head_yaw()

                else:
                    print("Full...")
                    move_head_yaw(-90, head_velocity)

        elif re.search(r"Hand", text, re.IGNORECASE):
            print("Hand")

            if re.search(r"Left", text, re.IGNORECASE):
                print("Left Hand")

                if re.search(r"Up", text, re.IGNORECASE):
                    print("Up")

                    if re.search(r"Little", text, re.IGNORECASE):
                        print("a Little...")
                        move_arms()

                    else:
                        print("Full...")
                        move_arms(-90, "", arm_velocity)

                if re.search(r"Down", text, re.IGNORECASE):
                    print("Down")

                    if re.search(r"Little", text, re.IGNORECASE):
                        print("a Little...")
                        move_arms()

                    else:
                        print("Full...")
                        move_arms(90, "", arm_velocity)

            if re.search(r"Right", text, re.IGNORECASE):
                print("Right Hand")

                if re.search(r"Up", text, re.IGNORECASE):
                    print("Up")

                    if re.search(r"Little", text, re.IGNORECASE):
                        print("a Little...")
                        move_arms()

                    else:
                        print("Full...")    
                        move_arms("", -90, arm_velocity)

                if re.search(r"Down", text, re.IGNORECASE):
                    print("Down")

                    if re.search(r"Little", text, re.IGNORECASE):
                        print("a Little...")
                        move_arms()

                    else:
                        print("Full...")
                        move_arms("", 90, arm_velocity)

            elif re.search(r"Up", text, re.IGNORECASE):
                print("Up")

                if re.search(r"Little", text, re.IGNORECASE):
                    print("a Little...")
                    move_arms()

                else:
                    print("Full...")
                    move_arms(-90, -90, arm_velocity)

            elif re.search(r"Down", text, re.IGNORECASE):
                print("Down")

                if re.search(r"Little", text, re.IGNORECASE):
                    print("a Little...")
                    move_arms()

                else:
                    print("Full...")
                    move_arms(90, 90, arm_velocity)

        elif re.search(r"Forward", text, re.IGNORECASE):
            print("Forward")

            if re.search(r"Little", text, re.IGNORECASE):
                print("a Little...")
                move(movement_velocity, 0)
                time.sleep(3)
                move(0, 0)

            else:
                print("Full...")
                move(movement_velocity, 0)

        elif re.search(r"Backward", text, re.IGNORECASE):
            print("Backward")

            if re.search(r"Little", text, re.IGNORECASE):
                print("a Little...")
                move(movement_velocity * -1, 0)
                time.sleep(3)
                move(0, 0)

            else:
                print("Full...")
                move(movement_velocity * -1, 0)

        elif re.search(r"Right", text, re.IGNORECASE):
            print("Right")

            if re.search(r"Little", text, re.IGNORECASE):
                print("a Little...")
                move(0, (angular_velocity * -1)/2)
                time.sleep(3)

                move(0, 0)
                move(movement_velocity, 0)

            else:
                print("Full...")
                move(0, angular_velocity * -1)
                time.sleep(3)

                move(0, 0)
                move(movement_velocity, 0)

        elif re.search(r"Left", text, re.IGNORECASE):
            print("Left")

            if re.search(r"Little", text, re.IGNORECASE):
                print("a Little...")
                move(0, (angular_velocity)/2)
                time.sleep(3)

                move(0, 0)
                move(movement_velocity, 0)

            else:
                print("Full...")
                move(0, angular_velocity)
                time.sleep(3)

                move(0, 0)
                move(movement_velocity, 0)

    elif re.search(r"Lift|Raise", text, re.IGNORECASE):
        print("Lifting")

        if re.search(r"Hand", text, re.IGNORECASE):
            print("Hand")

            if re.search(r"Left", text, re.IGNORECASE):
                print("of Left Side")

                if re.search(r"Up", text, re.IGNORECASE):
                    print("Up")

                    if re.search(r"Little", text, re.IGNORECASE):
                        print("a Little...")
                        move_arms()

                    else:
                        print("Full...")
                        move_arms(-90, "", arm_velocity)

            elif re.search(r"Right", text, re.IGNORECASE):
                print("of Right Side")

                if re.search(r"Up", text, re.IGNORECASE):
                    print("Up")

                    if re.search(r"Little", text, re.IGNORECASE):
                        print("a Little...")
                        move_arms()

                    else:
                        print("Full...")
                        move_arms("", -90, arm_velocity)

            elif re.search(r"Up", text, re.IGNORECASE):
                print("Up")

                if re.search(r"Little", text, re.IGNORECASE):
                    print("a Little...")
                    move_arms()

                else:
                    print("Full...")
                    move_arms(-90, -90, arm_velocity)

    elif re.search(r"Lower|Put", text, re.IGNORECASE):
        print("Lowering")

        if re.search(r"Hand", text, re.IGNORECASE):
            print("Hand")

            if re.search(r"Left", text, re.IGNORECASE):
                print("of Left Side")

                if re.search(r"Down", text, re.IGNORECASE):
                    print("Down")

                    if re.search(r"Little", text, re.IGNORECASE):
                        print("a Little...")
                        move_arms()

                    else:
                        print("Full...")
                        move_arms(90, "", arm_velocity)

            elif re.search(r"Right", text, re.IGNORECASE):
                print("of Right Side")

                if re.search(r"Down", text, re.IGNORECASE):
                    print("Down")

                    if re.search(r"Little", text, re.IGNORECASE):
                        print("a Little...")
                        move_arms()

                    else:
                        print("Full...")
                        move_arms("", 90, arm_velocity)

            elif re.search(r"Down", text, re.IGNORECASE):
                print("Down")

                if re.search(r"Little", text, re.IGNORECASE):
                    print("a Little...")
                    move_arms()

                else:
                    print("Full...")
                    move_arms(90, 90, arm_velocity)

    elif re.search(r"Rotate|Turn", text, re.IGNORECASE):
        print("Rotating")

        if re.search(r"Head", text, re.IGNORECASE):
            print("Head")

            if re.search(r"Left", text, re.IGNORECASE):
                print("Left")

                if re.search(r"Little", text, re.IGNORECASE):
                    print("a Little...")
                    move_head_yaw()

                else:
                    print("Full...")
                    move_head_yaw(90, head_velocity)

            elif re.search(r"Right", text, re.IGNORECASE):
                print("Right")

                if re.search(r"Little", text, re.IGNORECASE):
                    print("a Little...")
                    move_head_yaw()

                else:
                    print("Full...")
                    move_head_yaw(-90, head_velocity)

        elif re.search(r"Left", text, re.IGNORECASE):
            print("Left")
            move(0, angular_velocity)
            time.sleep(3)
            move(0, 0)

        elif re.search(r"Right", text, re.IGNORECASE):
            print("Right")
            move(0, angular_velocity * -1)
            time.sleep(3)
            move(0, 0)

        elif re.search(r"Backward", text, re.IGNORECASE):
            print("Backward")
            move(0, angular_velocity)
            time.sleep(5)
            move(0, 0)

    elif re.search(r"Tilt|Lean", text, re.IGNORECASE):
        print("Tilting")

        if re.search(r"Head", text, re.IGNORECASE):
            print("Head")

            if re.search(r"Left", text, re.IGNORECASE):
                print("Left")

                if re.search(r"Little", text, re.IGNORECASE):
                    print("a Little...")
                    move_head_roll()

                else:
                    print("Full...")
                    move_head_roll(-42, head_velocity)

            elif re.search(r"Right", text, re.IGNORECASE):
                print("Right")

                if re.search(r"Little", text, re.IGNORECASE):
                    print("a Little...")
                    move_head_roll()

                else:
                    print("Full...")
                    move_head_roll(42, head_velocity)

    elif re.search(r"Terminate", text, re.IGNORECASE):
        print("*Program Terminated*")
        sys.exit(0)

    else:
        response_generation_lap(text)




