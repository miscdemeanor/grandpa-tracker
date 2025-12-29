import os
import requests
import datetime
from zoneinfo import ZoneInfo
import asyncio
import random
from edge_tts import Communicate

# --- CONFIGURATION ---
API_KEY = os.environ.get('AVIATIONSTACK_KEY')
FLIGHT_NO = "7"
AIRLINE = "AA"
URL = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&flight_iata={AIRLINE}{FLIGHT_NO}"

# --- KID-FRIENDLY GEOGRAPHY ENGINE ---
# This estimates location based on flight progress (DFW to BNE is approx 15-16 hours)
def get_location_description(progress_percent):
    if progress_percent < 5:
        return "just left Texas and is seeing the giant deserts below!"
    elif progress_percent < 15:
        return "crossing the coast of Mexico and heading out over the big blue ocean!"
    elif progress_percent < 30:
        return "soaring high above the deep Pacific Ocean, far away from any land!"
    elif progress_percent < 50:
        return "approaching the International Date Line. He's about to fly from yesterday into tomorrow! That's real time travel!"
    elif progress_percent < 65:
        return "flying near the beautiful islands of Kiribati and Fiji. Look out the window for coral reefs!"
    elif progress_percent < 85:
        return "crossing over the Coral Sea. He's getting so close to Australia now!"
    elif progress_percent < 95:
        return "slowing down as he approaches the Queensland coast. He'll see the Sunshine Coast soon!"
    else:
        return "doing his final descent into Brisbane! He can probably see the Gateway Bridge right now!"

async def generate_tracker_audio():
    try:
        res = requests.get(URL).json()
        if 'data' not in res or not res['data']:
            msg = "Mission Control here! Grandpa's plane hasn't appeared on my radar yet. It's likely still at the airport in Dallas getting all the suitcases on board!"
        else:
            flight = res['data'][0]
            status = flight['flight_status']
            
            # Timezone Handling (Convert everything to Brisbane AEST)
            bne_tz = ZoneInfo("Australia/Brisbane")
            now_bne = datetime.datetime.now(bne_tz)
            
            # Get arrival time and convert to AEST
            arr_str = flight['arrival']['estimated'] or flight['arrival']['scheduled']
            # Aviationstack gives UTC, we convert to BNE
            arr_utc = datetime.datetime.fromisoformat(arr_str.replace('Z', '+00:00'))
            arr_bne = arr_utc.astimezone(bne_tz)
            
            # Get departure time to calculate progress
            dep_str = flight['departure']['actual'] or flight['departure']['scheduled']
            dep_utc = datetime.datetime.fromisoformat(dep_str.replace('Z', '+00:00'))
            
            # Calculations
            time_left = arr_bne - now_bne
            total_duration = arr_utc - dep_utc
            elapsed = now_bne - dep_utc.astimezone(bne_tz)
            progress = (elapsed.total_seconds() / total_duration.total_seconds()) * 100
            
            hours = int(time_left.total_seconds() // 3600)
            mins = int((time_left.total_seconds() % 3600) // 60)
            
            # Metric conversion (787-9 averages)
            speed_kmh = 900 
            altitude_m = 11500 
            
            location_action = get_location_description(progress)
            arrival_clock_time = arr_bne.strftime("%I:%M %p")

            # --- DYNAMIC MESSAGES ---
            intros = [
                f"Beep boop! Mission control update! I've spotted Grandpa's big silver bird!",
                f"Attention! This is a Grandpa-Tracker update! We have a signal!",
                f"Guess what? I just pinged the satellites and found Grandpa high in the sky!",
                f"Wow! Grandpa's plane is moving so fast! Let me check the radar map..."
            ]
            
            missions = [
                f"His current mission is {location_action}",
                f"Right now, Grandpa is {location_action}",
                f"Looking at the map, Grandpa is {location_action}"
            ]
            
            fun_facts = [
                f"He is zooming along at {speed_kmh} kilometers per hour! That's faster than the world's fastest racing car!",
                f"He is flying {altitude_m} meters high in the sky. If you stacked 30 Eiffel Towers on top of each other, that's how high he is!",
                f"The air outside his window is 50 degrees below zero, but it's nice and toasty inside the plane.",
                f"His plane, the Dreamliner, has wings that flex like a giant bird to keep the flight smooth."
            ]

            if status == "landed":
                msg = "Touchdown! Grandpa's plane has landed in Brisbane! Welcome home Grandpa! Go give him a huge hug!"
            elif status == "active":
                msg = (f"{random.choice(intros)} {random.choice(missions)} "
                       f"He will be landing in Brisbane at exactly {arrival_clock_time}. "
                       f"That is in {hours} hours and {mins} minutes. {random.choice(fun_facts)} "
                       f"Wave at the clouds and say: See you soon, Grandpa!")
            else:
                msg = f"Grandpa's plane is still in Dallas. The pilots are finishing their coffee and checking the engines. He'll be in the air soon!"

        print(msg)
        # Use an Australian voice for local context
        communicate = Communicate(msg, "en-AU-WilliamNeural")
        await communicate.save("status.mp3")
        
    except Exception as e:
        print(f"Error: {e}")
        fallback = Communicate("Mission control is having trouble reaching the satellites! Grandpa is so far over the ocean that the signal is weak. Try again in a little while!", "en-AU-WilliamNeural")
        await fallback.save("status.mp3")

if __name__ == "__main__":
    asyncio.run(generate_tracker_audio())
