import os
import requests

# API Endpoint & Parameters
URL = "https://prod-nz-rdr.recreation-management.tylerapp.com/nzrdr/rdr/search/greatwalkplacefacility"

PLACE_ID = 880            # Paparoa Track ID
START_DATE = "2027-02-15" # YYYY-MM-DD: Start date to check
DAYS_TO_CHECK = 12        # Number of days to check starting from START_DATE

# Optional: Set to a specific hut name (e.g., "Moonlight Tops Hut"), or set to None to check all huts
TARGET_HUT_NAME = "None"

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

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
    "arrivalDate": START_DATE,
    "nights": DAYS_TO_CHECK
}

def send_alert(message):
    print(message)
    if WEBHOOK_URL:
        payload = {"content": message[:1900]}
        requests.post(WEBHOOK_URL, json=payload)

def check_availability():
    try:
        response = requests.post(URL, json=PAYLOAD, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()

        facilities = data.get("GreatWalkFacilityData", [])
        availability_report = []

        for facility in facilities:
            facility_name = facility.get("FacilityName", "Unknown Hut")

            # Filter for a specific hut if TARGET_HUT_NAME is set
            if TARGET_HUT_NAME and TARGET_HUT_NAME.lower() not in facility_name.lower():
                continue

            date_records = facility.get("GreatWalkFacilityDateData", [])

            open_dates_for_hut = []
            for record in date_records:
                total_available = record.get("TotalAvailable", 0)
                arrival_date_raw = record.get("ArrivalDate", "")
                
                # Extract YYYY-MM-DD string
                date_only = arrival_date_raw.split("T")[0]

                if total_available > 0:
                    open_dates_for_hut.append(f"  • **{date_only}**: {total_available} spot(s) available")

            if open_dates_for_hut:
                hut_summary = f"🏠 **{facility_name}**:\n" + "\n".join(open_dates_for_hut)
                availability_report.append(hut_summary)

        if availability_report:
            filter_text = f" for {TARGET_HUT_NAME}" if TARGET_HUT_NAME else ""
            report_message = (
                f"🚨 **DOC Availability Report{filter_text}**\n"
                f"Checking {DAYS_TO_CHECK} days starting {START_DATE}:\n\n"
                + "\n\n".join(availability_report)
            )
            send_alert(report_message)
        else:
            target_scope = TARGET_HUT_NAME if TARGET_HUT_NAME else f"placeId {PLACE_ID}"
            print(f"Checked {DAYS_TO_CHECK} days starting {START_DATE} for {target_scope}: No spots available.")

    except Exception as e:
        print(f"Error checking availability: {e}")

if __name__ == "__main__":
    check_availability()
