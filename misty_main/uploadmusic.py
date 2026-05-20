import os
import requests
from dotenv import load_dotenv


load_dotenv()

misty_ip = os.getenv("misty_ip") #MISTY IP
music_name = "ghoomar3.wav"



with open(music_name, "rb") as f:
    response = requests.post(
        f"http://{misty_ip}/api/audio",
        files={"file": (music_name, f, "audio/wav")},
        data={"FileName": music_name}   # 🔥 THIS WAS MISSING
    )

print(response.text)

