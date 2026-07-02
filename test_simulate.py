import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.app import app
import json

with app.test_client() as client:
    data = {
        "latitude": -33.4489,
        "longitude": -70.6693,
        "width_m": 1.0,
        "height_m": 1.6,
        "season": "summer",
        "power_gen_kw": 2.5,
        "shadows": [
            {"start_hour": 10.0, "end_hour": 12.0, "shade_factor": 0.5},
            {"start_hour": 16.0, "end_hour": 18.0, "shade_factor": 0.8}
        ]
    }
    response = client.post('/api/simulate', json=data)
    result = response.get_json()
    
    # Exclude large plot_data and multivariable_surface for a cleaner terminal output
    if 'plot_data' in result:
        result['plot_data'] = f"< {len(result['plot_data'])} time series points >"
    if 'multivariable_surface' in result:
        result['multivariable_surface'] = "< surface meshgrid arrays >"
        
    print(json.dumps(result, indent=2))
