import requests

url = "https://www.vividseats.com/hermes/api/v1/listings?productionId=5471078&includeIpAddress=true&currency=USD&localizeCurrency=true"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Accept": "application/json",
}

response = requests.get(url, headers=headers)
data = response.json()

# Define your target sections
target_sections = [str(i) for i in range(305, 315)] + [str(i) for i in range(327, 337)]

print("Checking target sections...")

global_metadata = data.get('global', [])
if global_metadata:
    event_info = global_metadata[0]
    print(f"Event: {event_info.get('productionName', 'Unknown')}")
    print(f"Venue: {event_info.get('mapTitle', 'Unknown')}")
    print("-" * 40)

# Process tickets listings
tickets = data.get('tickets', [])
if not tickets:
    print("No tickets found.")
else:
    for listing in tickets:
        section_id = listing.get('i', 'Unknown')
        section_label = listing.get('l', 'Unknown')
        price = listing.get('p', 'Unknown')
        row = listing.get('r', 'Unknown')
        quantity = listing.get('q', 'Unknown')
        notes = listing.get('n', 'No additional notes')

        print(f"Section ID   : {section_id}")
        print(f"Section Label: {section_label}")
        print(f"Row          : {row}")
        print(f"Quantity     : {quantity}")
        print(f"Price        : ${price}")
        print(f"Notes        : {notes}")
        print("-" * 40)

print("Done.")