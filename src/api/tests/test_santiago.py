import sys
import os

# Add src to the Python path so we can import the model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from api.models.solar_panel import SolarPanel

# Santiago, Chile coordinates
lat = -33.4489
lon = -70.6693

print(f"Testing SolarPanel in Santiago, Chile (Lat: {lat}, Lon: {lon})...\n")

# Instantiate a generic 5.0 kW panel
panel = SolarPanel(power_gen=5.0, latitude=lat, longitude=lon)

# Fetch location terrain
location = panel.fetch_location_details()
print(f"Fetched Location Details: {location}")

# Get ideal facing direction
direction = panel.get_ideal_facing_direction()
print(f"Ideal Facing Direction: {direction}")

print("\nModel Representation:")
print(panel)
