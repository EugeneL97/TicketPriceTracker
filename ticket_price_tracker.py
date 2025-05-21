import requests

url = "https://www.vividseats.com/hermes/api/v1/listings?productionId=5471078&includeIpAddress=true&currency=USD&localizeCurrency=true"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Accept": "application/json",
}

response = requests.get(url, headers=headers)
data = response.json()

# Define your parameters
MAX_PRICE_PER_TICKET = 350
REQUIRED_QUANTITY = 4
production_id = 'Unknown'

target_sections = [str(i) for i in range(305, 315)] + [str(i) for i in range(327, 337)]

print("Checking target sections...")

global_metadata = data.get('global', [])
if global_metadata:
    event_info = global_metadata[0]
    production_id = event_info.get('productionId', 'Unknown')
    print(f"Event: {event_info.get('productionName', 'Unknown')}")
    print(f"Venue: {event_info.get('mapTitle', 'Unknown')}")
    print("-" * 40)

# Create a list to store filtered tickets
filtered_tickets = []

# Process tickets listings
tickets = data.get('tickets', [])
if not tickets:
    print("No tickets found.")
else:
    for listing in tickets:
        section_label = listing.get('l', 'Unknown')
        price = listing.get('p', 'Unknown')
        quantity = listing.get('q', 'Unknown')
        
        # Split section label to get components
        label_parts = section_label.split()
        if len(label_parts) >= 3:  # Ensure we have enough parts
            level = label_parts[0]
            section_number = label_parts[-1]  # Get the last part (3-digit number)
            
            # Check if this listing matches our criteria
            if (int(quantity) == REQUIRED_QUANTITY and
                section_number in target_sections and
                price != 'Unknown' and
                float(price) <= MAX_PRICE_PER_TICKET):
                
                # Get base price and calculate fees
                base_price = float(price)
                all_inclusive_price = float(listing.get('aip', base_price))
                total_fees = all_inclusive_price - base_price
                
                # Construct the ticket URL
                listing_id = listing.get('i', '')
                ticket_url = f"https://www.vividseats.com/new-england-patriots-tickets-gillette-stadium-3-6-2026--sports-nfl-football/production/{production_id}?showDetails={listing_id}&qty={REQUIRED_QUANTITY}"
                
                filtered_tickets.append({
                    'section': section_number,
                    'level': level,
                    'base_price': base_price,
                    'fees': total_fees,
                    'total_price': all_inclusive_price,
                    'row': listing.get('r', 'Unknown'),
                    'notes': listing.get('n', 'No additional notes'),
                    'url': ticket_url
                })

    # Sort filtered tickets by total price
    filtered_tickets.sort(key=lambda x: x['total_price'], reverse=True)

    # Display results
    if filtered_tickets:
        print(f"\nFound {len(filtered_tickets)} matching listings under ${MAX_PRICE_PER_TICKET} per ticket:")
        print("-" * 40)
        for ticket in filtered_tickets:
            print(f"Section      : {ticket['section']} ({ticket['level']})")
            print(f"Row          : {ticket['row']}")
            print(f"Base Price   : ${ticket['base_price']:.2f}")
            print(f"Fees         : ${ticket['fees']:.2f}")
            print(f"Total Price  : ${ticket['total_price']:.2f}")
            print(f"Notes        : {ticket['notes']}")
            print(f"Purchase URL : {ticket['url']}")
            print("-" * 40)
    else:
        print(f"\nNo tickets found matching your criteria (4 tickets, target sections, under ${MAX_PRICE_PER_TICKET})")

print("Done.")