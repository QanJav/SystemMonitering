import psutil  # Library for system and hardware information
import json    # Library for working with JSON files
import os      # Library for operating system functionalities
import datetime # Library for working with dates and times

# Create a log file name with the current date and time
LOG_FILE = f'logs/monitoring_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
ALERTS_FILE = 'alerts.json'  # File to store alerts

# Function to log events with the current date and time
def log_event(event):
    # Format timestamp for the log entry
    timestamp = datetime.datetime.now().strftime("%Y/%m/%d_%H:%M")  
    # Open log file in append mode to add new entries
    with open(LOG_FILE, 'a') as log:  
        # Write the event with the timestamp to the log file
        log.write(f"{timestamp} {event}\n")  

# Class to represent an alert
class Alert:
    def __init__(self, alert_type, threshold):  # Constructor to initialize alert properties
        self.alert_type = alert_type  # Type of alert (CPU, Memory, Disk)
        self.threshold = threshold      # Threshold percentage to trigger alert

    def __str__(self):
        # Format the alert display string
        return f"{self.alert_type} larm {self.threshold}%"  

# Class to manage monitoring and alerts
class Monitor:
    def __init__(self):
        # Load existing alerts from file when Monitor is initialized
        self.alerts = self.load_alerts()  
        self.monitoring = False            # Monitoring status (on/off)

    # Function to load alerts from a JSON file if it exists
    def load_alerts(self):
        if os.path.exists(ALERTS_FILE):  # Check if the alerts file exists
            with open(ALERTS_FILE, 'r') as f:
                # Load alerts from the file and create Alert objects
                return [Alert(**alert) for alert in json.load(f)]  
        return []  # Return empty list if no alerts are found

    # Function to save alerts to a JSON file
    def save_alerts(self):
        # Write all alerts to the JSON file
        with open(ALERTS_FILE, 'w') as f:
            json.dump([alert.__dict__ for alert in self.alerts], f)

    # Function to add a new alert
    def add_alert(self, alert_type, threshold):
        new_alert = Alert(alert_type, threshold)  # Create a new Alert object
        self.alerts.append(new_alert)  # Add it to the list of alerts
        self.save_alerts()  # Save updated alerts to the file
        # Log the addition of the alert
        log_event(f"{alert_type}_larm_konfigurerat_{threshold}_procent")  
        print(f"Larm för {alert_type} satt till {threshold}%.")  # Confirm to user

    # Function to list all configured alerts
    def list_alerts(self):
        if not self.alerts:  # Check if there are no alerts
            print("Inga konfigurerade larm.")
            return
        # Sort alerts by type and print them
        for alert in sorted(self.alerts, key=lambda a: a.alert_type):
            print(alert)

    # Function to check system usage against configured alerts
    def check_alerts(self):
        if self.monitoring:  # Check only if monitoring is active
            cpu_usage = psutil.cpu_percent()  # Get CPU usage
            memory_info = psutil.virtual_memory()  # Get memory info
            disk_usage = psutil.disk_usage('/')  # Get disk usage

            active_alerts = []  # List to hold any active alerts
            # Sort alerts by threshold in descending order and check
            for alert in sorted(self.alerts, key=lambda a: a.threshold, reverse=True):
                # Check if CPU usage exceeds the alert threshold
                if alert.alert_type == 'CPU' and cpu_usage > alert.threshold:
                    active_alerts.append(f"***VARNING, LARM AKTIVERAT, CPU ANVÄNDNING ÖVERSTIGER {alert.threshold}%***")
                # Check if memory usage exceeds the alert threshold
                elif alert.alert_type == 'Minnes' and memory_info.percent > alert.threshold:
                    active_alerts.append(f"***VARNING, LARM AKTIVERAT, MINNESANVÄNDNING ÖVERSTIGER {alert.threshold}%***")
                # Check if disk usage exceeds the alert threshold
                elif alert.alert_type == 'Disk' and disk_usage.percent > alert.threshold:
                    active_alerts.append(f"***VARNING, LARM AKTIVERAT, DISKANVÄNDNING ÖVERSTIGER {alert.threshold}%***")

            if active_alerts:  # If there are any active alerts
                for alert in active_alerts:
                    print(alert)  # Print the alert message
                    # Log the alert without the warning formatting
                    log_event(alert.split("***")[1].strip())  

    # Function to start monitoring system usage
    def start_monitoring(self):
        self.monitoring = True  # Set monitoring status to true
        log_event("Övervakningsläge_startat")  # Log the start of monitoring
        print("Övervakning har startats. Tryck Ctrl + C för att avsluta övervakningen.")

        try:
            # Loop to continuously check alerts while monitoring is active
            while self.monitoring:
                self.check_alerts()  # Check for alerts
                print("Övervakning är aktiv, tryck på valfri tangent för att återgå till menyn.")
                input("Tryck på valfri tangent för att fortsätta övervakningen...")  # Wait for user input
        except KeyboardInterrupt:  # Catch Ctrl + C to stop monitoring
            self.monitoring = False  # Set monitoring status to false
            log_event("Övervakningsläge_avslutat")  # Log the end of monitoring
            print("Övervakningen har avslutats.")

    # Function to remove an alert
    def remove_alert(self):
        if not self.alerts:  # Check if there are no alerts to remove
            print("Inga konfigurerade larm att ta bort.")
            return

        print("Välj ett konfigurerat larm att ta bort:")  # Prompt user for an alert to remove
        for index, alert in enumerate(sorted(self.alerts, key=lambda a: a.alert_type), start=1):
            print(f"{index}. {alert}")  # Display each alert with an index

        choice = input("Ange numret på larmet du vill ta bort: ")  # Get user choice
        if choice.isdigit() and 1 <= int(choice) <= len(self.alerts):
            # Remove the selected alert from the list
            removed_alert = self.alerts.pop(int(choice) - 1)  
            self.save_alerts()  # Save updated alerts to the file
            # Log the removal of the alert
            log_event(f"{removed_alert.alert_type}_larm_borttaget_{removed_alert.threshold}_procent")  
            print(f"Larm för {removed_alert.alert_type} borttaget.")  # Confirm removal
        else:
            print("Ogiltigt val.")  # Handle invalid choice

# Main menu function for user interaction
def main_menu():
    monitor = Monitor()  # Create a Monitor object
    while True:  # Loop to display the menu until user chooses to exit
        print("\n1. Starta övervakning")
        print("2. Lista aktiv övervakning")
        print("3. Skapa larm")
        print("4. Visa larm")
        print("5. Övervakningsläge") 
        print("6. Ta bort larm")
        print("0. Avsluta")

        val = input("Välj ett alternativ: ")  # Get user choice

        if val == '1':
            monitor.start_monitoring()  # Start monitoring
        elif val == '2':
            if not monitor.monitoring:  # Check if monitoring is active
                print("Ingen övervakning är aktiv.")
            else:
                # Display current system usage
                cpu_usage = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()
                disk_usage = psutil.disk_usage('/')
                print(f"CPU Användning: {cpu_usage}%")
                print(f"Minnesanvändning: {memory_info.percent}% ({memory_info.used / (1024 ** 3):.2f} GB out of {memory_info.total / (1024 ** 3):.2f} GB used)")
                print(f"Diskanvändning: {disk_usage.percent}% ({disk_usage.used / (1024 ** 3):.2f} GB out of {disk_usage.total / (1024 ** 3):.2f} GB used)")
                input("Tryck valfri tangent för att gå tillbaka till huvudmeny.")
        elif val == '3':
            alert_type = input("Ange larmtyp (CPU, Minnes, Disk): ")  # Get alert type from user
            threshold = input("Ställ in nivå för larm mellan 0-100: ")  # Get threshold value
            # Validate threshold input
            if threshold.isdigit() and 0 < int(threshold) <= 100:
                monitor.add_alert(alert_type, int(threshold))  # Add the alert
            else:
                print("Felaktig nivå.")  # Handle invalid threshold
        elif val == '4':
            monitor.list_alerts()  # List all configured alerts
            input("Tryck valfri tangent för att gå tillbaka till huvudmeny.")
        elif val == '5':
            if monitor.monitoring:  # Check if monitoring is already active
                print("Övervakning är redan aktiv.")
            else:
                monitor.start_monitoring()  # Start monitoring directly from here
        elif val == '6':
            monitor.remove_alert()  # Remove an alert
        elif val == '0':
            break  # Exit the loop to end the program
        else:
            print("Ogiltigt alternativ.")  # Handle invalid menu option

# Start the program
if __name__ == "__main__":
    main_menu()  # Call the main menu function to begin