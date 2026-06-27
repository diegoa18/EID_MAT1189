import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

def test_los_angeles_winter_cloudy():
    client = app.test_client()
    
    # Los Angeles, Chile coordinates
    # Winter schedule: sunrise ~ 8:00 AM (8.0), sunset ~ 5:30 PM (17.5)
    # Cloudy weather: We specify 'cloudy' and the model handles the efficiency drop
    payload = {
        "latitude": -37.4697,
        "longitude": -72.3537,
        "power_gen_kw": 1.0, # Base peak power
        "width_m": 1.0,
        "height_m": 1.0,
        "season": "winter"
    }
    
    print("Testing /api/simulate for Los Angeles, Chile (Winter + Cloudy) ...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    res = client.post('/api/simulate', json=payload)
    data = res.get_json()
    
    # Trim the plot_data output to keep the terminal output clean
    if 'plot_data' in data:
        data['plot_data'] = f"<list of {len(data['plot_data'])} elements>"
        
    print("\nResponse:")
    print(json.dumps(data, indent=2))

if __name__ == '__main__':
    test_los_angeles_winter_cloudy()
