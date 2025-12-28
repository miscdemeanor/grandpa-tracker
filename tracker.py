import os
import requests
import datetime
import asyncio
import random
from edge_tts import Communicate

# CONFIG
FLIGHT_NO = "7"
AIRLINE_IATA = "AA"
API_KEY = os.environ.get('AVIATIONSTACK_KEY')
URL = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&flight_iata={AIRLINE_IATA}{FLIGHT_NO}"

# FUN FACTS FOR A KID
FUN_FACTS = [
    "Grandpa is flying in a Boeing 787 Dreamliner. It's made of special carbon fiber, just like a high-tech racing bike!",
    "The wings on Grandpa's plane curve up like a bird's wings when it flies.",
    "The windows on this plane are magic! They don't have plastic shades; they turn blue with a special button.",
    "Grandpa is flying over the deep blue Pacific Ocean. It's the biggest ocean in the whole world!",
    "Outside the plane, it is 50 degrees below zero! That's colder than a freezer, but Grandpa is nice and cozy inside.",
    "Grandpa's plane is traveling at 560 miles per hour. That's ten times faster than a car on the highway!",
    "The plane Grandpa is on is so big it can carry over 200 people and all their suitcases!"
]

INTROS = [
    "Beep boop! Flight tracker activated!",
    "Checking the sky... checking the clouds...",
    "High five! It's time to check on Grandpa!",
    "Hello! I found Grandpa's plane on my radar!"
]

async def generate_tracker_audio():
    try:
        res = requests.get(URL).json()
        if 'data' not in res or not res['data']:
            msg = "I can't see the plane on my radar just yet. It might still be at the airport in Dallas. Let's check again soon!"
        else:
            flight = res['data'][0]
            status = flight['flight_status']
            
            # Time calculation
            arr_time_str = flight['arrival']['estimated'] or flight['arrival']['scheduled']
            arr_dt = datetime.datetime.fromisoformat(arr_time_str.replace('Z', '+00:00'))
            now = datetime.datetime.now(datetime.timezone.utc)
            diff = arr_dt - now
            
            hours = diff.total_seconds() // 3600
            mins = (diff.total_seconds() % 3600) // 60

            intro = random.choice(INTROS)
            fact = random.choice(FUN_FACTS)

            if status == "landed":
                msg = "Hooray! The radar shows Grandpa has landed in Brisbane! He's back on the ground. Go give him a giant hug!"
            elif status == "active":
                # Special Date Line Logic for DFW-BNE
                date_line_msg = ""
                if hours > 8:
                    date_line_msg = "Grandpa is crossing the International Date Line. He's literally flying into tomorrow!"
                
                msg = (f"{intro} Grandpa is on American Airlines Flight 7. "
                       f"He is {date_line_msg} high over the Pacific Ocean. "
                       f"He will land in Brisbane in about {int(hours)} hours and {int(mins)} minutes. "
                       f"{fact} Wave at the sky and say, Safe travels, Grandpa!")
            else:
                msg = "Grandpa's plane is at the gate in Dallas! The pilots are fueling up and Grandpa is getting settled in his seat."

        print(f"Script generated: {msg}")
        # Using a friendly US voice for the American Airlines vibe
        communicate = Communicate(msg, "en-US-GuyNeural")
        await communicate.save("status.mp3")
        
    except Exception as e:
        print(f"Error: {e}")
        # Fallback file so the Yoto doesn't play silence
        communicate = Communicate("I'm having a little trouble talking to the satellites. Let's try again in a few minutes!", "en-US-GuyNeural")
        await asyncio.run(communicate.save("status.mp3"))

if __name__ == "__main__":
    asyncio.run(generate_tracker_audio())
