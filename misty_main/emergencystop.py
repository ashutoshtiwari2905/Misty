import mistyctrlfuncs
import mistyvoicefuncs
import os
from dotenv import load_dotenv

load_dotenv()


misty_ip = os.getenv("misty_ip") #Misty IP


print("Stopping all movement...")
mistyctrlfuncs.stop_all_movement()
mistyvoicefuncs.mistystopspeak(misty_ip)

print("Resetting Body Position")
mistyctrlfuncs.reset_position()

