import sys
import os
import json

# Ensure we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

def test():
    client = app.test_client()
    
    print("Testing /api/health ...")
    res = client.get('/api/health')
    print(res.get_json())
    
    print("\nTesting /api/simulate ...")
    res = client.post('/api/simulate', json={
        "latitude": -33.4489,
        "longitude": -70.6693,
        "power_gen_kw": 5.0,
        "width_m": 2.236,
        "height_m": 2.236,
        "season": "summer"
    })
    
    data = res.get_json()
    if 'plot_data' in data:
        data['plot_data'] = f"<list of {len(data['plot_data'])} elements>"
    print(json.dumps(data, indent=2))
    
    print("\nTesting /api/calculate ...")
    res = client.post('/api/calculate', json={
        "latitude": -33.4489,
        "longitude": -70.6693,
        "delta_theta": 10.0,
        "delta_phi": 10.0,
        "power_gen": 1.0
    })
    print(json.dumps(res.get_json(), indent=2))

if __name__ == '__main__':
    test()
