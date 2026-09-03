import os
import requests

# API Endpoint & Parameters
URL = "https://prod-nz-rdr.recreation-management.tylerapp.com/nzrdr/rdr/search/greatwalkplacefacility"

TARGET_DATE = "2027-02-15"  # YYYY-MM-DD
PLACE_ID = 880               # Paparoa Track ID
NIGHTS_COUNT = 12            # Date window range
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Optional: Set to a specific hut name (e.g., "Moonlight Tops Hut"), or None to check all huts on the track
TARGET_HUT_NAME = None 

HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://bookings.doc.govt.nz",
    "referer": "https://bookings.doc.govt.nz/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
}

PAYLOAD = {
    "accomodation": "",
    "placeId": PLACE_ID,
    "customerClassificationId": 0,
    "arrivalDate": TARGET_DATE,
    "nights": NIGHTS_COUNT
}

def send_alert(message):
    print(message)
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": message})

def check_availability():
    try:
        response = requests.post(URL, json=PAYLOAD, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()

        facilities = data.get("GreatWalkFacilityData", [])
        available_spots = []

        for facility in facilities:
            facility_name = facility.get("FacilityName", "Unknown Hut")

            # Skip if filtering for a single specific hut
            if TARGET_HUT_NAME and TARGET_HUT_NAME.lower() not in facility_name.lower():
                continue

            date_records = facility.get("GreatWalkFacilityDateData", [])
            for record in date_records:
                arrival_date = record.get("ArrivalDate", "")
                total_available = record.get("TotalAvailable", 0)

                # Match date (formatted as "2027-02-15T00:00:00") and check for open bunks
                if arrival_date.startswith(TARGET_DATE) and total_available > 0:
                    available_spots.append(f"• **{facility_name}**: {total_available} spot(s) open")

        if available_spots:
            alert_message = f"🚨 **DOC Spot Available for {TARGET_DATE}!**\n" + "\n".join(available_spots)
            send_alert(alert_message)
        else:
            print(f"Checked: No availability found for {TARGET_DATE}.")

    except Exception as e:
        print(f"Error checking availability: {e}")

if __name__ == "__main__":
    check_availability()
