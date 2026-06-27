import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from api.models.solar_panel import SolarPanel
from api.models.simulator import SolarSimulator

def main():
    print("=== Testing Solar Simulator ===")
    
    # Create panel in Santiago
    panel = SolarPanel(latitude=-33.4489, longitude=-70.6693, power_gen=5.0)
    
    # Calculate peak power over area (let's say 5 m^2 panel to match 5kW)
    # At peak efficiency, it generates 5.0 kW peak
    peak_power = panel.calculate_hourly_energy_area_integral(width_m=2.236, height_m=2.236)
    
    # Create Simulator (Assuming Santiago summer: sunrise ~6:30, sunset ~20:30)
    simulator = SolarSimulator(panel, sunrise=6.5, sunset=20.5)
    
    # 1. Test Daily Energy Integration
    daily_energy = simulator.calculate_daily_energy(peak_power)
    print(f"Peak Power: {peak_power:.2f} kW")
    print(f"Total Daily Energy (Integrated over time): {daily_energy:.2f} kWh/day")
    
    # 2. Test Time-Series Simulation Data Generation
    print("\nTime-Series Data Points (Partial):")
    data = simulator.simulate_day(peak_power, steps_per_hour=1) # 1 hour intervals
    for point in data:
        if 5.0 <= point['time'] <= 21.0:
            print(f"Time: {point['time']:05.2f} h | Power: {point['power']:.2f} kW")

if __name__ == "__main__":
    main()
