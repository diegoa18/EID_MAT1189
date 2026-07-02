import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'streamlit')))
from api import obtener_hessiano, simular

def test_api():
    print("Testing simular...")
    res_sim = simular(-33.4489, -70.6693, 1.0, 1.6, "summer", 2.5)
    if res_sim.get("status") != "success":
        print(f"Failed simular: {res_sim}")
        return False
    print("simular OK. Applied shadows:", res_sim.get("results", {}).get("applied_shadows", []))

    print("Testing obtener_hessiano...")
    res_hess = obtener_hessiano(30, 45, 1.0, 33, 0)
    if res_hess.get("status") != "success":
        print(f"Failed obtener_hessiano: {res_hess}")
        return False
    print("obtener_hessiano OK. Determinant:", res_hess.get("determinant"))

    return True

if __name__ == '__main__':
    # Add retries in case the server is just starting
    success = False
    for _ in range(5):
        try:
            if test_api():
                success = True
                break
        except Exception as e:
            print(f"Waiting for server... {e}")
            time.sleep(2)
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
