import requests
import os
import mistyctrlfuncs
from openai import OpenAI
from dotenv import load_dotenv
import whisper


# This loads the variables from .env into the system environment
load_dotenv()



# Access the variables
api_key= os.getenv("api_key1")
misty_ip = os.getenv("misty_ip")
temp_audio = "temp_audio.wav"


#STARTS REC FROM MISTY MIC
def startrecmain(misty_ip, file_name):

    url = f"http://{misty_ip}/api/audio/record/start"

    payload = {
        "FileName": file_name,
        "MaxDurationSeconds": 60  # optional
    }

    response = requests.post(url, json=payload)

    print("Start Recording Response:")


#START N STOP REC ON LAP USING CHIN
def startnstopreclap(file_path):

    import numpy as np
    import sounddevice as sd
    from scipy.io.wavfile import write


    # Global variables
    recording = False
    audio_data = []
    sample_rate = 44100
    sample_rate = 44100


    # 🔥 WAIT FOR START TRIGGER
    mistyctrlfuncs.chin_detection(misty_ip)

    print("Recording started...")

    audio_data = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_data.append(indata.copy())

    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        callback=callback
    ):
        # 🔥 WAIT FOR STOP TRIGGER
        mistyctrlfuncs.chin_detection(misty_ip)

        sd.sleep(200)  # flush buffer

    print("Recording stopped.")

    if len(audio_data) == 0:
        print("❌ No audio recorded")
        return

    audio = np.concatenate(audio_data, axis=0)

    write(file_path, sample_rate, audio)

    print(f"Audio saved at: {file_path}")


#START N STOP REC ON LAP USING ENTER KEY
def startnstoplapmain(file_path):

    import numpy as np
    import sounddevice as sd
    from scipy.io.wavfile import write


    # Global variables
    recording = False
    audio_data = []
    sample_rate = 44100
    sample_rate = 44100

    # 🔥 WAIT FOR START TRIGGER
    trigger = input("Press Enter to start recording...")

    if trigger == "":
        
        print("Recording started...")

        audio_data = []

        def callback(indata, frames, time, status):
            if status:
                print(status)
            audio_data.append(indata.copy())

        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            callback=callback
        ):
            # 🔥 WAIT FOR STOP TRIGGER
            trigger = input("Press Enter to stop recording...")
            if trigger == "":

                sd.sleep(200)  # flush buffer

        print("Recording stopped.")

        if len(audio_data) == 0:
            print("❌ No audio recorded")
            return

        audio = np.concatenate(audio_data, axis=0)

        write(file_path, sample_rate, audio)

        print(f"Audio saved at: {file_path}")


def startnstoplapmain1sec(temp_audio):

    import numpy as np
    import sounddevice as sd
    from scipy.io.wavfile import write


    # Global variables
    recording = False
    audio_data = []
    sample_rate = 44100
    sample_rate = 44100

    print("Recording for 1 second...")

    audio_data = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_data.append(indata.copy())

    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        callback=callback
    ):
        sd.sleep(1000)  # record for 1 second

    print("Recording stopped.")

    if len(audio_data) == 0:
        print("❌ No audio recorded")
        return

    audio = np.concatenate(audio_data, axis=0)

    write(temp_audio, sample_rate, audio)

    print(f"Audio saved at: {temp_audio}")


#STOP REC FROM MISTY MIC
def stoprecmain(misty_ip):
    
    url = f"http://{misty_ip}/api/audio/record/stop"

    response = requests.post(url)

    print("Stop Recording Response:")


#DOWNLOAD AUDIO FILE FROM MISTY
def getaudiofile(misty_ip, file_name):

    save_path = r"C:\Users\Ashutosh Tiwari\OneDrive\Desktop\misty"  # your desired folder

        # 📁 Ensure folder exists
    os.makedirs(save_path, exist_ok=True)

    # 🌐 URL to fetch audio
    url = f"http://{misty_ip}/api/audio?FileName={file_name}"

    # ⬇️ Download file
    response = requests.get(url)

    if response.status_code == 200:
        full_path = os.path.join(save_path, file_name)
    
        with open(full_path, "wb") as f:
            f.write(response.content)
    
        print(f"✅ Downloaded successfully to: {full_path}")
    else:
        print("❌ Failed to download file")
        print("Status Code:", response.status_code)


#SPEECH TO TEXT CONVERSION OF AUDIO
def mistystt(audio_file):
    
    # Load best accuracy model (large) 
    model = whisper.load_model("small")

    # Transcribe (force English)
    result = model.transcribe(audio_file, language="en")

    # Save to text file
    with open("mistydoi.txt", "w", encoding="utf-8") as f:
        f.write(result["text"])

    print("Transcription completed!")
    print(result["text"])


#ASK AND GET RESPONSE OF TEXT FROM GROQ AI
def askgroqapi(api_key, text):
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    user_input = text

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ WORKING MODEL
            messages=[{"role": "user", "content": user_input}]
        )

        ai_text = response.choices[0].message.content

    except Exception as e:
        ai_text = f"Error: {e}"

    with open("llm_response.txt", "w", encoding="utf-8") as f:
        f.write(ai_text)

    print(ai_text)


#MAKE MISTY SPEAK A TEXT
def mistyspeak(misty_ip, ai_text, voice="hi-IN-SwaraNeural"):
    url = f"http://{misty_ip}/api/tts/speak"

    data = {
        "Text": ai_text,
        "Voice": voice,
        "Style": "default",
        "Rate": 0,
        "Pitch": 0
    }

    requests.post(url, json=data)

    print("Misty Speaking...")


#MAKE MISTY STOP SPEAKING
def mistystopspeak(misty_ip):
        url = f"http://{misty_ip}/api/tts/stop"
        response = requests.post(url)
        print("Misty Stopped Speaking...")



startnstoplapmain1sec(temp_audio)
mistystt(temp_audio)


