import os, requests, datetime, asyncio
from edge_tts import Communicate

# CONFIGURATION
FLIGHT_NO = "7"
AIRLINE_IATA = "AA"
# Aviationstack Free Tier uses HTTP
URL = f"http://api.aviationstack.com/v1/flights?access_key={os.environ['AVIATIONSTACK_KEY']}&flight_iata={AIRLINE_IATA}{FLIGHT_NO}"

async def generate_tracker_audio():
    try:
        res = requests.get(URL).json()
        flight = res['data'][0]
        status = flight['flight_status']
        
        # 1. Get Landing Time
        arr_time_str = flight['arrival']['estimated'] or flight['arrival']['scheduled']
        arr_dt = datetime.datetime.fromisoformat(arr_time_str.replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
        diff = arr_dt - now
        
        # 2. Kid-Friendly Logic
        if status == "landed":
            msg = "Hooray! Grandpa has landed in Brisbane! He is off the plane and getting his bags. Go give him a giant hug!"
        elif status == "active":
            hours = diff.seconds // 3600
            mins = (diff.seconds % 3600) // 60
            # Calculate location based on flight duration (DFW-BNE is ~16 hours)
            msg = f"Grandpa is high in the sky right now on a giant Dreamliner plane! He is flying over the blue Pacific Ocean. He will land in Brisbane in about {hours} hours and {mins} minutes. Did you know his plane has magic windows that change color with a button? Wave at the sky and say 'Hi Grandpa!'"
        else:
            msg = "Grandpa's plane is at the airport in Dallas getting ready to fly! The pilots are checking the buttons and Grandpa is finding his seat."

        # 3. Generate High-Quality Voice (Free)
        # Using 'en-AU-WilliamNeural' for a friendly Aussie/International vibe
        communicate = Communicate(msg, "en-AU-WilliamNeural")
        await communicate.save("status.mp3")
        print("Audio updated!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(generate_tracker_audio())
