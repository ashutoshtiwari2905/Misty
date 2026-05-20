import requests
import time
import mistyvoicefuncs
import mistyctrlfuncs
import sys
import os
from dotenv import load_dotenv

# This loads the variables from .env into the system environment
load_dotenv()

# Access the variables
api_key= os.getenv("api_key1") #API KEY
misty_ip = os.getenv("misty_ip") #Misty IP






while True:
    try:
        res = requests.get(f"http://{misty_ip}/api/device", timeout=2)

        if res.status_code == 200:
            print("🟢 Misty connected")

            mistyctrlfuncs.chin_detection(misty_ip)
            mistyvoicefuncs.startrecmain(misty_ip, "mistydoi.wav")

            mistyctrlfuncs.chin_detection(misty_ip)
            mistyvoicefuncs.stoprecmain(misty_ip)

            mistyvoicefuncs.getaudiofile(misty_ip, "mistydoi.wav")

            mistyvoicefuncs.mistystt("mistydoi.wav")

            with open("mistydoi.txt", "r") as file:
                text = file.read()

            mistyctrlfuncs.execute_command(text)


        else:
            print("🟠 Misty API issue")

    except KeyboardInterrupt:
        print("*program terminated*")
        sys.exit(0)

    except:
        sys.exit(0)

    time.sleep(2)
    
    






