import math
from typing import List, Dict

class SolarSimulator:
    def __init__(self, panel, sunrise: float = 6.0, sunset: float = 18.0, shadows: List[Dict] = None):
        self.panel = panel
        self.sunrise = sunrise
        self.sunset = sunset
        self.daylight_hours = sunset - sunrise
        self.shadows = shadows or []

    def _get_shade_factor(self, time_hours: float) -> float:
        factor = 0.0
        for s in self.shadows:
            if s["start_hour"] <= time_hours <= s["end_hour"]:
                factor = max(factor, s.get("shade_factor", 0))
        return min(factor, 1.0)

    def power_at_time(self, time_hours: float, peak_power: float) -> float:
        if time_hours <= self.sunrise or time_hours >= self.sunset:
            return 0.0

        time_fraction = (time_hours - self.sunrise) / self.daylight_hours
        angle = time_fraction * math.pi
        base_power = peak_power * math.sin(angle)
        shade = self._get_shade_factor(time_hours)
        return base_power * (1 - shade)

    def simulate_day(self, peak_power: float, steps_per_hour: int = 4) -> List[Dict[str, float]]:
        data_points = []
        total_steps = int(24 * steps_per_hour)
        dt = 1.0 / steps_per_hour

        for i in range(total_steps):
            t = i * dt
            base = self._power_no_shadows(t, peak_power)
            shade = self._get_shade_factor(t)
            p = base * (1 - shade)
            data_points.append({
                "time": t,
                "power": p,
                "power_ideal": base,
                "shade_factor": shade,
            })

        return data_points

    def _power_no_shadows(self, time_hours: float, peak_power: float) -> float:
        if time_hours <= self.sunrise or time_hours >= self.sunset:
            return 0.0
        time_fraction = (time_hours - self.sunrise) / self.daylight_hours
        angle = time_fraction * math.pi
        return peak_power * math.sin(angle)

    def calculate_daily_energy(self, peak_power: float, n_steps: int = 1000) -> float:
        dt = self.daylight_hours / n_steps
        total = 0.0
        for i in range(n_steps):
            t = self.sunrise + (i * dt)
            total += self._power_no_shadows(t, peak_power) * dt
        return total

    def calculate_daily_energy_details(self, peak_power: float, n_steps: int = 1000) -> Dict[str, float]:
        dt = self.daylight_hours / n_steps
        total_energy = 0.0
        ideal_energy = 0.0

        for i in range(n_steps):
            t = self.sunrise + (i * dt)
            base = self._power_no_shadows(t, peak_power)
            shade = self._get_shade_factor(t)
            ideal_energy += base * dt
            total_energy += base * (1 - shade) * dt

        return {
            "total_energy": total_energy,
            "ideal_energy": ideal_energy,
            "energy_loss": ideal_energy - total_energy,
        }
