import time
from ticket_price_tracker import TicketTracker
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
import os

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
print(DISCORD_WEBHOOK_URL)
def send_discord_notification(title, message, url=None):
    """Send a Discord notification"""
    webhook = DiscordWebhook(
        url=DISCORD_WEBHOOK_URL,
        content=""
    )
    
    # Create embed
    embed = DiscordEmbed(
        title=title,
        description=message,
        color="03b2f8"  # Blue color
    )
    
    if url:
        embed.add_embed_field(name="Purchase Link", value=url)
    
    webhook.add_embed(embed)
    webhook.execute()

def main():
    # Define search parameters
    MAX_PRICE_PER_TICKET = 350
    REQUIRED_QUANTITY = 4
    target_sections = [str(i) for i in range(305, 315)] + [str(i) for i in range(327, 337)]
    
    tracker = TicketTracker()
    first_run = True
    
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\nChecking prices at {current_time}")
            print("-" * 40)

            # Search for tickets
            filtered_tickets = tracker.search_tickets(
                max_price=MAX_PRICE_PER_TICKET,
                required_quantity=REQUIRED_QUANTITY,
                target_sections=target_sections,
                show_metadata=first_run  # Only show metadata on first run
            )
            
            # Display full results only on first run
            if first_run:
                tracker.display_results(filtered_tickets, MAX_PRICE_PER_TICKET)
                first_run = False
            
            # Check for price changes
            price_changes = tracker.check_price_changes(filtered_tickets)
            if price_changes:
                print("\nPrice Changes Detected:")
                print("-" * 40)
                for update in price_changes:
                    change_type = "decreased" if update['change'] < 0 else "increased"
                    
                    # Send Discord notification
                    notification_title = "🎫 Ticket Price Change!"
                    notification_message = (
                        f"Section {update['section']}, Row {update['row']}\n"
                        f"Price has {change_type} by ${abs(update['change']):.2f}\n"
                        f"New price: ${update['current_price']:.2f}"
                    )
                    send_discord_notification(
                        notification_title,
                        notification_message,
                        update['url']
                    )
                
                # Show full current listing after price changes
                print("\nCurrent listings after price changes:")
                tracker.display_results(filtered_tickets, MAX_PRICE_PER_TICKET)
            else:
                print(f"No price changes detected in the last hour")
            
            # Save current data
            tracker.save_ticket_data(filtered_tickets)
            
            # Wait for next check
            print(f"\nNext check will be in 1 hour...")
            time.sleep(3600)  # 1 hour
            
        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(300)  # Wait 5 minutes if there's an error

if __name__ == "__main__":
    main() 
