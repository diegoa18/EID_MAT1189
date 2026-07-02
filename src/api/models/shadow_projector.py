import datetime
import math
from typing import Dict, List

import requests

try:
    from pysolar.solar import get_altitude, get_azimuth
except ImportError:
    pass


def point_in_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y):
            if x <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= xinters:
                    inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def ray_intersects_segment(p_x, p_y, dir_x, dir_y, a_x, a_y, b_x, b_y, max_dist):
    v1_x = a_x - p_x
    v1_y = a_y - p_y
    v2_x = b_x - p_x
    v2_y = b_y - p_y
    v3_x = -dir_y
    v3_y = dir_x

    dot1 = v1_x * v3_x + v1_y * v3_y
    dot2 = v2_x * v3_x + v2_y * v3_y
    if (dot1 * dot2) >= 0:
        return False, 0

    cross = (b_x - a_x) * dir_y - (b_y - a_y) * dir_x
    if cross == 0:
        return False, 0

    t = ((a_x - p_x) * (b_y - a_y) - (a_y - p_y) * (b_x - a_x)) / cross
    if 0 <= t <= max_dist:
        return True, t
    return False, 0


class ShadowProjector:
    @staticmethod
    def calculate_shade_fraction_double_integral(
        lat: float,
        lon: float,
        buildings: List[Dict],
        alt_deg: float,
        az_deg: float,
        panel_width: float = 1.0,
        panel_height: float = 1.6,
    ) -> float:
        """
        Calcula la fraccion de sombra utilizando una integral doble de Riemann sobre el area fisica del panel.
        P(shade) = (1/A) * integral_x integral_y S(x,y) dx dy
        """
        if not buildings or alt_deg <= 0:
            return 0.0

        n_x, n_y = 5, 5  # Resolucion de la integral doble
        dx_m = panel_width / n_x
        dy_m = panel_height / n_y

        deg_to_m_lat = 111320.0
        deg_to_m_lon = 40075000.0 * math.cos(math.radians(lat)) / 360.0

        shaded_area_integral = 0.0

        sun_az_rad = math.radians(az_deg)
        ray_dx = math.sin(sun_az_rad) / deg_to_m_lon
        ray_dy = math.cos(sun_az_rad) / deg_to_m_lat

        for i in range(n_x):
            for j in range(n_y):
                offset_x_m = (i - n_x / 2.0 + 0.5) * dx_m
                offset_y_m = (j - n_y / 2.0 + 0.5) * dy_m

                pt_lon = lon + (offset_x_m / deg_to_m_lon)
                pt_lat = lat + (offset_y_m / deg_to_m_lat)

                is_shaded = False
                for b in buildings:
                    poly = b["polygon"]
                    height = b["height"]

                    shadow_length_m = height / math.tan(math.radians(alt_deg))
                    if shadow_length_m <= 0 or shadow_length_m > 500:
                        continue

                    dist_deg = shadow_length_m / deg_to_m_lat

                    if point_in_polygon(pt_lon, pt_lat, poly):
                        is_shaded = True
                        break

                    for k in range(len(poly)):
                        p1 = poly[k]
                        p2 = poly[(k + 1) % len(poly)]
                        intersects, _ = ray_intersects_segment(
                            pt_lon,
                            pt_lat,
                            ray_dx,
                            ray_dy,
                            p1[0],
                            p1[1],
                            p2[0],
                            p2[1],
                            dist_deg,
                        )
                        if intersects:
                            is_shaded = True
                            break
                    if is_shaded:
                        break

                if is_shaded:
                    shaded_area_integral += dx_m * dy_m

        return shaded_area_integral / (panel_width * panel_height)

    @staticmethod
    def get_building_shadows(
        lat: float,
        lon: float,
        date: datetime.datetime,
        panel_width: float = 1.0,
        panel_height: float = 1.6,
    ) -> List[Dict[str, float]]:
        radius = 100  # meters around point
        overpass_url = "https://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        (
          way["building"](around:{radius},{lat},{lon});
          relation["building"](around:{radius},{lat},{lon});
        );
        out body geom;
        """
        try:
            headers = {"User-Agent": "SolarOptimizationApp/1.0"}
            response = requests.get(
                overpass_url,
                params={"data": overpass_query},
                headers=headers,
                timeout=15,
            )
            data = response.json()
        except Exception as e:
            print("Error fetching Overpass data:", e)
            return []

        buildings = []
        for element in data.get("elements", []):
            if "geometry" not in element:
                continue

            tags = element.get("tags", {})
            height = float(tags.get("height", 0))
            if height == 0:
                levels = float(tags.get("building:levels", 1))
                height = levels * 3.0

            pts = [(node["lon"], node["lat"]) for node in element["geometry"]]
            if len(pts) >= 3:
                buildings.append({"polygon": pts, "height": height})

        if not buildings:
            return []

        shadow_events = []
        in_shadow = False
        start_shadow = None

        deg_to_m_lat = 111320
        deg_to_m_lon = 40075000 * math.cos(math.radians(lat)) / 360

        for hour_int in range(6 * 4, 19 * 4):  # check every 15 min from 6am to 7pm
            h = hour_int / 4.0
            dt = datetime.datetime(
                date.year,
                date.month,
                date.day,
                int(h),
                int((h % 1) * 60),
                tzinfo=datetime.timezone.utc,
            )

            try:
                alt_deg = get_altitude(lat, lon, dt)
                az_deg = get_azimuth(lat, lon, dt)
            except NameError:
                return []

            if alt_deg <= 0:
                continue

            shade_factor = ShadowProjector.calculate_shade_fraction_double_integral(
                lat, lon, buildings, alt_deg, az_deg, panel_width, panel_height
            )

            # Use 90% opacity for the shaded area fraction
            effective_shade = shade_factor * 0.90

            if effective_shade > 0.05:
                if not in_shadow:
                    in_shadow = True
                    start_shadow = h
                    current_shade_factors = [effective_shade]
                else:
                    current_shade_factors.append(effective_shade)
            else:
                if in_shadow:
                    in_shadow = False
                    avg_shade = sum(current_shade_factors) / len(current_shade_factors)
                    shadow_events.append(
                        {
                            "start_hour": start_shadow,
                            "end_hour": h,
                            "shade_factor": round(avg_shade, 3),
                        }
                    )
                    current_shade_factors = []

        if in_shadow:
            avg_shade = sum(current_shade_factors) / len(current_shade_factors)
            shadow_events.append(
                {
                    "start_hour": start_shadow,
                    "end_hour": 19.0,
                    "shade_factor": round(avg_shade, 3),
                }
            )

        return shadow_events
