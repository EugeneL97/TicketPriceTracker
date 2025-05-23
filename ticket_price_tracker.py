import requests
import sqlite3
from datetime import datetime
import os

class TicketTracker:
    def __init__(self, db_path=None):
        # Use environment variable if provided, otherwise use default
        self.db_path = db_path or os.environ.get('DB_PATH', 'ticket_history.db')
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.setup_database()
        self.url = "https://www.vividseats.com/hermes/api/v1/listings?productionId=5471078&includeIpAddress=true&currency=USD&localizeCurrency=true"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        self.production_id = 'Unknown'
        
        # Existing initialization code...

    def setup_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS ticket_history
                    (timestamp DATETIME,
                     section TEXT,
                     row TEXT,
                     listing_id TEXT,
                     base_price REAL,
                     total_price REAL,
                     price_change REAL)''')
        conn.commit()
        conn.close()

    def save_ticket_data(self, filtered_tickets):
        """Save current ticket data to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        timestamp = datetime.now()
        
        for ticket in filtered_tickets:
            # Get the last price for this listing to calculate change
            c.execute('''SELECT total_price 
                        FROM ticket_history 
                        WHERE listing_id = ? 
                        ORDER BY timestamp DESC 
                        LIMIT 1''', 
                     (ticket['listing_id'],))
            
            last_price = c.fetchone()
            price_change = 0 if not last_price else ticket['total_price'] - last_price[0]
            
            c.execute('''INSERT INTO ticket_history VALUES
                        (?, ?, ?, ?, ?, ?, ?)''',
                     (timestamp, ticket['section'], ticket['row'],
                      ticket['listing_id'], ticket['base_price'],
                      ticket['total_price'], price_change))
        
        conn.commit()
        conn.close()

    def check_price_changes(self, filtered_tickets):
        """Check how prices have changed for each ticket"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        price_updates = []

        for ticket in filtered_tickets:
            c.execute('''SELECT total_price 
                        FROM ticket_history 
                        WHERE listing_id = ? 
                        ORDER BY timestamp DESC 
                        LIMIT 1''', 
                     (ticket['listing_id'],))
            
            last_price = c.fetchone()
            
            if last_price:
                price_change = ticket['total_price'] - last_price[0]
                if price_change != 0:  # Only report if price changed
                    price_updates.append({
                        'section': ticket['section'],
                        'row': ticket['row'],
                        'current_price': ticket['total_price'],
                        'previous_price': last_price[0],
                        'change': price_change,
                        'url': ticket['url']
                    })

        conn.close()
        return price_updates

    def search_tickets(self, max_price, required_quantity, target_sections, show_metadata=False):
        """Search for tickets matching the specified criteria"""
        response = requests.get(self.url, headers=self.headers)
        data = response.json()

        # Process global metadata
        global_metadata = data.get('global', [])
        if global_metadata:
            event_info = global_metadata[0]
            self.production_id = event_info.get('productionId', 'Unknown')
            if show_metadata:
                print(f"Event: {event_info.get('productionName', 'Unknown')}")
                print(f"Venue: {event_info.get('mapTitle', 'Unknown')}")
                print("-" * 40)

        filtered_tickets = []
        tickets = data.get('tickets', [])
        
        if not tickets:
            print("No tickets found.")
            return filtered_tickets

        for listing in tickets:
            section_label = listing.get('l', 'Unknown')
            price = listing.get('p', 'Unknown')
            quantity = listing.get('q', 'Unknown')
            
            label_parts = section_label.split()
            if len(label_parts) >= 3:
                level = label_parts[0]
                section_number = label_parts[-1]
                
                if (int(quantity) == required_quantity and
                    section_number in target_sections and
                    price != 'Unknown' and
                    float(price) <= max_price):
                    
                    base_price = float(price)
                    all_inclusive_price = float(listing.get('aip', base_price))
                    total_fees = all_inclusive_price - base_price
                    
                    listing_id = listing.get('i', '')
                    ticket_url = f"https://www.vividseats.com/new-england-patriots-tickets-gillette-stadium-3-6-2026--sports-nfl-football/production/{self.production_id}?showDetails={listing_id}&qty={required_quantity}"
                    
                    filtered_tickets.append({
                        'section': section_number,
                        'level': level,
                        'base_price': base_price,
                        'fees': total_fees,
                        'total_price': all_inclusive_price,
                        'row': listing.get('r', 'Unknown'),
                        'notes': listing.get('n', 'No additional notes'),
                        'url': ticket_url,
                        'listing_id': listing_id
                    })

        filtered_tickets.sort(key=lambda x: x['total_price'], reverse=True)
        return filtered_tickets

    def display_results(self, filtered_tickets, max_price):
        """Display the search results"""
        if filtered_tickets:
            print(f"\nFound {len(filtered_tickets)} matching listings under ${max_price} per ticket:")
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
            print(f"\nNo tickets found matching your criteria (4 tickets, target sections, under ${max_price})")