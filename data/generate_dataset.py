"""
AeroSight Aviation Dataset Generator & Ingestion Module
Generates statistically authentic aviation operational data matching the schema and
distributions of the US Bureau of Transportation Statistics (BTS) On-Time Performance dataset.
"""

import os
import random
import math
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Set deterministic seed for reproducible data generation
random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SAMPLE_DIR = os.path.join(DATA_DIR, "sample")
RAW_DIR = os.path.join(DATA_DIR, "raw")

# 1. Airport Reference Metadata
AIRPORTS = [
    {"iata": "ATL", "icao": "KATL", "name": "Hartsfield-Jackson Atlanta International Airport", "city": "Atlanta", "state": "GA", "lat": 33.6407, "lon": -84.4277, "elev": 1026, "tz": "America/New_York", "hub": "Large Hub", "terminals": 2, "gates": 192},
    {"iata": "ORD", "icao": "KORD", "name": "O'Hare International Airport", "city": "Chicago", "state": "IL", "lat": 41.9742, "lon": -87.9073, "elev": 672, "tz": "America/Chicago", "hub": "Large Hub", "terminals": 4, "gates": 189},
    {"iata": "DFW", "icao": "KDFW", "name": "Dallas/Fort Worth International Airport", "city": "Dallas", "state": "TX", "lat": 32.8998, "lon": -97.0403, "elev": 607, "tz": "America/Chicago", "hub": "Large Hub", "terminals": 5, "gates": 165},
    {"iata": "DEN", "icao": "KDEN", "name": "Denver International Airport", "city": "Denver", "state": "CO", "lat": 39.8561, "lon": -104.6737, "elev": 5434, "tz": "America/Denver", "hub": "Large Hub", "terminals": 1, "gates": 150},
    {"iata": "CLT", "icao": "KCLT", "name": "Charlotte Douglas International Airport", "city": "Charlotte", "state": "NC", "lat": 35.2144, "lon": -80.9473, "elev": 748, "tz": "America/New_York", "hub": "Large Hub", "terminals": 1, "gates": 115},
    {"iata": "LAX", "icao": "KLAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "state": "CA", "lat": 33.9425, "lon": -118.4081, "elev": 128, "tz": "America/Los_Angeles", "hub": "Large Hub", "terminals": 9, "gates": 146},
    {"iata": "JFK", "icao": "KJFK", "name": "John F. Kennedy International Airport", "city": "New York", "state": "NY", "lat": 40.6413, "lon": -73.7781, "elev": 13, "tz": "America/New_York", "hub": "Large Hub", "terminals": 6, "gates": 128},
    {"iata": "SFO", "icao": "KSFO", "name": "San Francisco International Airport", "city": "San Francisco", "state": "CA", "lat": 37.6188, "lon": -122.3754, "elev": 13, "tz": "America/Los_Angeles", "hub": "Large Hub", "terminals": 4, "gates": 115},
    {"iata": "SEA", "icao": "KSEA", "name": "Seattle-Tacoma International Airport", "city": "Seattle", "state": "WA", "lat": 47.4489, "lon": -122.3094, "elev": 433, "tz": "America/Los_Angeles", "hub": "Large Hub", "terminals": 1, "gates": 103},
    {"iata": "MIA", "icao": "KMIA", "name": "Miami International Airport", "city": "Miami", "state": "FL", "lat": 25.7959, "lon": -80.2870, "elev": 8, "tz": "America/New_York", "hub": "Large Hub", "terminals": 3, "gates": 131},
    {"iata": "BOS", "icao": "KBOS", "name": "Logan International Airport", "city": "Boston", "state": "MA", "lat": 42.3656, "lon": -71.0096, "elev": 20, "tz": "America/New_York", "hub": "Large Hub", "terminals": 4, "gates": 102},
    {"iata": "EWR", "icao": "KEWR", "name": "Newark Liberty International Airport", "city": "Newark", "state": "NJ", "lat": 40.6895, "lon": -74.1745, "elev": 18, "tz": "America/New_York", "hub": "Large Hub", "terminals": 3, "gates": 110},
    {"iata": "PHX", "icao": "KPHX", "name": "Phoenix Sky Harbor International Airport", "city": "Phoenix", "state": "AZ", "lat": 33.4352, "lon": -112.0101, "elev": 1135, "tz": "America/Phoenix", "hub": "Large Hub", "terminals": 2, "gates": 106},
    {"iata": "IAH", "icao": "KIAH", "name": "George Bush Intercontinental Airport", "city": "Houston", "state": "TX", "lat": 29.9902, "lon": -95.3368, "elev": 97, "tz": "America/Chicago", "hub": "Large Hub", "terminals": 5, "gates": 130},
    {"iata": "LAS", "icao": "KLAS", "name": "Harry Reid International Airport", "city": "Las Vegas", "state": "NV", "lat": 36.0840, "lon": -115.1537, "elev": 2181, "tz": "America/Los_Angeles", "hub": "Large Hub", "terminals": 2, "gates": 110},
    {"iata": "DTW", "icao": "KDTW", "name": "Detroit Metropolitan Airport", "city": "Detroit", "state": "MI", "lat": 42.2162, "lon": -83.3554, "elev": 645, "tz": "America/New_York", "hub": "Large Hub", "terminals": 2, "gates": 129},
    {"iata": "MSP", "icao": "KMSP", "name": "Minneapolis-Saint Paul International Airport", "city": "Minneapolis", "state": "MN", "lat": 44.8848, "lon": -93.2223, "elev": 841, "tz": "America/Chicago", "hub": "Large Hub", "terminals": 2, "gates": 131},
    {"iata": "MCO", "icao": "KMCO", "name": "Orlando International Airport", "city": "Orlando", "state": "FL", "lat": 28.4312, "lon": -81.3081, "elev": 96, "tz": "America/New_York", "hub": "Large Hub", "terminals": 3, "gates": 129},
    {"iata": "BWI", "icao": "KBWI", "name": "Baltimore/Washington International Airport", "city": "Baltimore", "state": "MD", "lat": 39.1774, "lon": -76.6684, "elev": 146, "tz": "America/New_York", "hub": "Large Hub", "terminals": 1, "gates": 78},
    {"iata": "SLC", "icao": "KSLC", "name": "Salt Lake City International Airport", "city": "Salt Lake City", "state": "UT", "lat": 40.7899, "lon": -111.9791, "elev": 4227, "tz": "America/Denver", "hub": "Large Hub", "terminals": 1, "gates": 68},
    {"iata": "SAN", "icao": "KSAN", "name": "San Diego International Airport", "city": "San Diego", "state": "CA", "lat": 32.7338, "lon": -117.1933, "elev": 17, "tz": "America/Los_Angeles", "hub": "Medium Hub", "terminals": 2, "gates": 51},
    {"iata": "IAD", "icao": "KIAD", "name": "Washington Dulles International Airport", "city": "Dulles", "state": "VA", "lat": 38.9531, "lon": -77.4565, "elev": 313, "tz": "America/New_York", "hub": "Large Hub", "terminals": 1, "gates": 123},
    {"iata": "TPA", "icao": "KTPA", "name": "Tampa International Airport", "city": "Tampa", "state": "FL", "lat": 27.9755, "lon": -82.5332, "elev": 26, "tz": "America/New_York", "hub": "Large Hub", "terminals": 1, "gates": 56},
    {"iata": "MDW", "icao": "KMDW", "name": "Chicago Midway International Airport", "city": "Chicago", "state": "IL", "lat": 41.7868, "lon": -87.7522, "elev": 620, "tz": "America/Chicago", "hub": "Large Hub", "terminals": 1, "gates": 43},
    {"iata": "PDX", "icao": "KPDX", "name": "Portland International Airport", "city": "Portland", "state": "OR", "lat": 45.5898, "lon": -122.5951, "elev": 31, "tz": "America/Los_Angeles", "hub": "Medium Hub", "terminals": 1, "gates": 60},
    {"iata": "DAL", "icao": "KDAL", "name": "Dallas Love Field", "city": "Dallas", "state": "TX", "lat": 32.8471, "lon": -96.8518, "elev": 487, "tz": "America/Chicago", "hub": "Medium Hub", "terminals": 1, "gates": 20},
    {"iata": "STL", "icao": "KSTL", "name": "St. Louis Lambert International Airport", "city": "St. Louis", "state": "MO", "lat": 38.7472, "lon": -90.3599, "elev": 618, "tz": "America/Chicago", "hub": "Medium Hub", "terminals": 2, "gates": 54},
    {"iata": "HNL", "icao": "PHNL", "name": "Daniel K. Inouye International Airport", "city": "Honolulu", "state": "HI", "lat": 21.3187, "lon": -157.9224, "elev": 13, "tz": "Pacific/Honolulu", "hub": "Large Hub", "terminals": 3, "gates": 60},
    {"iata": "FLL", "icao": "KFLL", "name": "Fort Lauderdale-Hollywood International Airport", "city": "Fort Lauderdale", "state": "FL", "lat": 26.0726, "lon": -80.1527, "elev": 9, "tz": "America/New_York", "hub": "Large Hub", "terminals": 4, "gates": 66},
    {"iata": "AUS", "icao": "KAUS", "name": "Austin-Bergstrom International Airport", "city": "Austin", "state": "TX", "lat": 30.1975, "lon": -97.6664, "elev": 542, "tz": "America/Chicago", "hub": "Medium Hub", "terminals": 2, "gates": 34},
    {"iata": "BNA", "icao": "KBNA", "name": "Nashville International Airport", "city": "Nashville", "state": "TN", "lat": 36.1263, "lon": -86.6774, "elev": 599, "tz": "America/Chicago", "hub": "Medium Hub", "terminals": 1, "gates": 42}
]

# 2. Airline Reference Metadata
AIRLINES = [
    {"carrier_code": "DL", "airline_name": "Delta Air Lines", "callsign": "DELTA", "country": "USA", "fleet_size": 950, "primary_hub": "ATL", "on_time_baseline": 0.83},
    {"carrier_code": "AA", "airline_name": "American Airlines", "callsign": "AMERICAN", "country": "USA", "fleet_size": 940, "primary_hub": "DFW", "on_time_baseline": 0.79},
    {"carrier_code": "UA", "airline_name": "United Airlines", "callsign": "UNITED", "country": "USA", "fleet_size": 920, "primary_hub": "ORD", "on_time_baseline": 0.80},
    {"carrier_code": "WN", "airline_name": "Southwest Airlines", "callsign": "SOUTHWEST", "country": "USA", "fleet_size": 815, "primary_hub": "DAL", "on_time_baseline": 0.78},
    {"carrier_code": "AS", "airline_name": "Alaska Airlines", "callsign": "ALASKA", "country": "USA", "fleet_size": 310, "primary_hub": "SEA", "on_time_baseline": 0.82},
    {"carrier_code": "B6", "airline_name": "JetBlue Airways", "callsign": "JETBLUE", "country": "USA", "fleet_size": 290, "primary_hub": "JFK", "on_time_baseline": 0.73},
    {"carrier_code": "NK", "airline_name": "Spirit Airlines", "callsign": "SPIRIT WINGS", "country": "USA", "fleet_size": 200, "primary_hub": "FLL", "on_time_baseline": 0.71},
    {"carrier_code": "OO", "airline_name": "SkyWest Airlines", "callsign": "SKYWEST", "country": "USA", "fleet_size": 520, "primary_hub": "SLC", "on_time_baseline": 0.81},
    {"carrier_code": "F9", "airline_name": "Frontier Airlines", "callsign": "FRONTIER FLIGHT", "country": "USA", "fleet_size": 135, "primary_hub": "DEN", "on_time_baseline": 0.72},
    {"carrier_code": "HA", "airline_name": "Hawaiian Airlines", "callsign": "HAWAIIAN", "country": "USA", "fleet_size": 62, "primary_hub": "HNL", "on_time_baseline": 0.88}
]

# 3. Aircraft Metadata
AIRCRAFT_MODELS = [
    {"model": "Boeing 737-800", "manufacturer": "Boeing", "capacity": 162, "speed_knots": 450, "wake": "M"},
    {"model": "Boeing 737-MAX8", "manufacturer": "Boeing", "capacity": 178, "speed_knots": 453, "wake": "M"},
    {"model": "Boeing 777-200ER", "manufacturer": "Boeing", "capacity": 314, "speed_knots": 490, "wake": "H"},
    {"model": "Boeing 787-9 Dreamliner", "manufacturer": "Boeing", "capacity": 290, "speed_knots": 488, "wake": "H"},
    {"model": "Airbus A320neo", "manufacturer": "Airbus", "capacity": 160, "speed_knots": 445, "wake": "M"},
    {"model": "Airbus A321neo", "manufacturer": "Airbus", "capacity": 196, "speed_knots": 450, "wake": "M"},
    {"model": "Airbus A350-900", "manufacturer": "Airbus", "capacity": 306, "speed_knots": 488, "wake": "H"},
    {"model": "Embraer E175", "manufacturer": "Embraer", "capacity": 76, "speed_knots": 430, "wake": "M"},
    {"model": "Bombardier CRJ-900", "manufacturer": "Bombardier", "capacity": 79, "speed_knots": 440, "wake": "M"}
]

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate Great Circle distance in nautical miles using Haversine formula."""
    r = 3440.065 # Earth radius in NM
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return max(50, int(r * c))

def generate_aircraft_fleet(n=250):
    """Generate simulated fleet tail numbers."""
    fleet = []
    carriers = [a["carrier_code"] for a in AIRLINES]
    for i in range(1, n + 1):
        carrier = random.choice(carriers)
        model = random.choice(AIRCRAFT_MODELS)
        tail = f"N{random.randint(100, 999)}{carrier}"
        year = random.randint(2005, 2023)
        fleet.append({
            "tail_number": tail,
            "carrier_code": carrier,
            "model": model["model"],
            "manufacturer": model["manufacturer"],
            "seat_capacity": model["capacity"],
            "cruise_speed_knots": model["speed_knots"],
            "wake_turbulence": model["wake"],
            "year_manufactured": year
        })
    return pd.DataFrame(fleet)

def generate_flight_dataset(num_records=35000):
    """Generate comprehensive flight dataset matching US BTS specifications."""
    print(f"Generating {num_records} flight records with realistic aviation distributions...")
    
    airports_df = pd.DataFrame(AIRPORTS)
    airport_map = {a["iata"]: a for a in AIRPORTS}
    airlines_df = pd.DataFrame(AIRLINES)
    airline_map = {a["carrier_code"]: a for a in AIRLINES}
    fleet_df = generate_aircraft_fleet(300)
    fleet_map = {row["tail_number"]: row for _, row in fleet_df.iterrows()}
    carrier_tails = {code: fleet_df[fleet_df["carrier_code"] == code]["tail_number"].tolist() for code in airline_map}

    start_date = datetime(2024, 1, 1)
    date_range_days = 90 # Q1 2024 (Jan 1 to Mar 31)

    records = []
    weather_events = []
    baggage_events = []

    # Weather condition probabilities by airport
    weather_conditions = ["Clear", "Cloudy", "Rain", "Fog", "Snow", "Thunderstorm"]
    weather_weights_winter = [0.55, 0.25, 0.10, 0.04, 0.04, 0.02]

    for i in range(1, num_records + 1):
        flight_id = f"FL-2024-{i:06d}"
        day_offset = random.randint(0, date_range_days - 1)
        flight_date = start_date + timedelta(days=day_offset)
        
        # Pick carrier and origin/dest
        carrier = random.choices(AIRLINES, weights=[a["fleet_size"] for a in AIRLINES])[0]
        carrier_code = carrier["carrier_code"]
        
        # Hub bias: 50% chance origin or dest is the carrier's primary hub
        if random.random() < 0.5:
            origin_code = carrier["primary_hub"]
            dest_code = random.choice([a["iata"] for a in AIRPORTS if a["iata"] != origin_code])
        else:
            orig_dest = random.sample([a["iata"] for a in AIRPORTS], 2)
            origin_code, dest_code = orig_dest[0], orig_dest[1]

        orig_apt = airport_map[origin_code]
        dest_apt = airport_map[dest_code]

        # Flight number & tail
        flight_num = random.randint(100, 2999)
        tails = carrier_tails.get(carrier_code, fleet_df["tail_number"].tolist())
        tail_num = random.choice(tails) if tails else f"N{random.randint(100, 999)}{carrier_code}"
        aircraft_info = fleet_map.get(tail_num, {"seat_capacity": 160, "cruise_speed_knots": 450})

        # Scheduled departure time (distributed across operational hours 06:00 to 22:00)
        dep_hour = int(np.clip(np.random.normal(14, 4), 6, 22))
        dep_min = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
        crs_dep_time = dep_hour * 100 + dep_min

        # Distance and scheduled elapsed time
        dist = calculate_distance(orig_apt["lat"], orig_apt["lon"], dest_apt["lat"], dest_apt["lon"])
        speed_nm_min = (aircraft_info.get("cruise_speed_knots", 450) / 60.0)
        nominal_air_time = int(dist / speed_nm_min)
        nominal_taxi_out = random.randint(12, 24)
        nominal_taxi_in = random.randint(5, 15)
        crs_elapsed = nominal_taxi_out + nominal_air_time + nominal_taxi_in
        
        # Scheduled arrival
        sched_dep_dt = datetime.combine(flight_date, datetime.min.time()) + timedelta(hours=dep_hour, minutes=dep_min)
        sched_arr_dt = sched_dep_dt + timedelta(minutes=crs_elapsed)
        crs_arr_time = sched_arr_dt.hour * 100 + sched_arr_dt.minute

        # Weather generation
        is_cold_origin = orig_apt["lat"] > 38
        origin_cond = random.choices(weather_conditions, weights=weather_weights_winter)[0]
        dest_cond = random.choices(weather_conditions, weights=weather_weights_winter)[0]
        
        origin_temp = int(random.gauss(32 if is_cold_origin else 58, 12))
        origin_wind = max(2, int(np.random.exponential(8)))
        origin_vis = 10 if origin_cond in ["Clear", "Cloudy"] else (4 if origin_cond == "Rain" else (1 if origin_cond in ["Fog", "Snow"] else 2))

        dest_temp = int(random.gauss(45, 15))
        dest_wind = max(2, int(np.random.exponential(7)))
        dest_vis = 10 if dest_cond in ["Clear", "Cloudy"] else (4 if dest_cond == "Rain" else (1 if dest_cond in ["Fog", "Snow"] else 2))

        # Cancellation logic (~1.5% overall BTS average)
        is_severe_weather = (origin_cond in ["Thunderstorm", "Snow"] and origin_wind > 25) or (origin_vis <= 1)
        cancel_prob = 0.18 if is_severe_weather else 0.012
        is_cancelled = 1 if (random.random() < cancel_prob) else 0
        cancellation_code = None

        if is_cancelled:
            if is_severe_weather:
                cancellation_code = "B" # Weather
            elif random.random() < 0.5:
                cancellation_code = "A" # Carrier
            else:
                cancellation_code = "C" # NAS
            
            records.append({
                "flight_id": flight_id,
                "flight_date": flight_date.strftime("%Y-%m-%d"),
                "carrier_code": carrier_code,
                "flight_number": flight_num,
                "tail_number": tail_num,
                "origin_airport": origin_code,
                "dest_airport": dest_code,
                "crs_dep_time": crs_dep_time,
                "dep_time": None,
                "dep_delay": None,
                "taxi_out": None,
                "wheels_off": None,
                "wheels_on": None,
                "taxi_in": None,
                "crs_arr_time": crs_arr_time,
                "arr_time": None,
                "arr_delay": None,
                "cancelled": 1,
                "cancellation_code": cancellation_code,
                "diverted": 0,
                "crs_elapsed_time": crs_elapsed,
                "actual_elapsed_time": None,
                "air_time": None,
                "distance": dist,
                "carrier_delay": 0.0,
                "weather_delay": 0.0,
                "nas_delay": 0.0,
                "security_delay": 0.0,
                "late_aircraft_delay": 0.0,
                "origin_temp_f": origin_temp,
                "origin_wind_mph": origin_wind,
                "origin_visibility_miles": origin_vis,
                "origin_weather_condition": origin_cond,
                "dest_temp_f": dest_temp,
                "dest_wind_mph": dest_wind,
                "dest_visibility_miles": dest_vis,
                "dest_weather_condition": dest_cond,
            })
            continue

        # Non-cancelled flight delays
        # Baseline on-time probability based on carrier & time of day congestion
        time_congestion_factor = 1.0 + (0.35 if (16 <= dep_hour <= 20) else 0.0)
        weather_factor = 1.8 if (origin_cond in ["Rain", "Snow", "Fog", "Thunderstorm"]) else 1.0
        
        on_time_prob = carrier["on_time_baseline"] / (time_congestion_factor * (1.0 + 0.15 * (weather_factor - 1.0)))
        
        is_delayed = random.random() > on_time_prob

        if not is_delayed:
            # On-time or slightly early (-15 to +14 min)
            dep_delay = round(float(np.random.normal(-2, 4)), 1)
            arr_delay = round(dep_delay + float(np.random.normal(-1, 5)), 1)
            carrier_delay, weather_delay, nas_delay, sec_delay, late_ac_delay = 0.0, 0.0, 0.0, 0.0, 0.0
        else:
            # Delayed flight: exponential distribution of delay minutes
            dep_delay = round(float(np.random.exponential(35) + 15), 1)
            # En-route padding recovery
            recovery = np.random.normal(3, 4)
            arr_delay = max(0.0, round(dep_delay - recovery, 1))

            # Delay breakdown attribution (BTS rules: only populated if arr_delay >= 15)
            if arr_delay >= 15.0:
                rem = arr_delay
                if origin_cond in ["Snow", "Thunderstorm"]:
                    weather_delay = round(rem * random.uniform(0.4, 0.8), 1)
                    rem -= weather_delay
                else:
                    weather_delay = 0.0

                if dep_hour >= 17 and random.random() < 0.6:
                    late_ac_delay = round(rem * random.uniform(0.3, 0.7), 1)
                    rem -= late_ac_delay
                else:
                    late_ac_delay = 0.0

                if random.random() < 0.5:
                    nas_delay = round(rem * random.uniform(0.3, 0.6), 1)
                    rem -= nas_delay
                else:
                    nas_delay = 0.0

                carrier_delay = max(0.0, round(rem, 1))
                sec_delay = 0.0
            else:
                carrier_delay, weather_delay, nas_delay, sec_delay, late_ac_delay = 0.0, 0.0, 0.0, 0.0, 0.0

        # Diverted (~0.2% probability)
        is_diverted = 1 if (random.random() < 0.002 and is_delayed) else 0

        # Calculate actual operational timestamps
        act_dep_dt = sched_dep_dt + timedelta(minutes=dep_delay)
        dep_time = act_dep_dt.hour * 100 + act_dep_dt.minute

        taxi_out = max(8, int(nominal_taxi_out + np.random.normal(0, 3) + (5 if dep_delay > 30 else 0)))
        actual_air_time = max(20, int(nominal_air_time + np.random.normal(0, 5)))
        taxi_in = max(4, int(nominal_taxi_in + np.random.normal(0, 2)))
        
        actual_elapsed = taxi_out + actual_air_time + taxi_in
        
        wheels_off_dt = act_dep_dt + timedelta(minutes=taxi_out)
        wheels_off = wheels_off_dt.hour * 100 + wheels_off_dt.minute
        
        wheels_on_dt = wheels_off_dt + timedelta(minutes=actual_air_time)
        wheels_on = wheels_on_dt.hour * 100 + wheels_on_dt.minute

        act_arr_dt = act_dep_dt + timedelta(minutes=actual_elapsed)
        arr_time = None if is_diverted else (act_arr_dt.hour * 100 + act_arr_dt.minute)

        records.append({
            "flight_id": flight_id,
            "flight_date": flight_date.strftime("%Y-%m-%d"),
            "carrier_code": carrier_code,
            "flight_number": flight_num,
            "tail_number": tail_num,
            "origin_airport": origin_code,
            "dest_airport": dest_code,
            "crs_dep_time": crs_dep_time,
            "dep_time": dep_time,
            "dep_delay": dep_delay,
            "taxi_out": taxi_out,
            "wheels_off": wheels_off,
            "wheels_on": wheels_on,
            "taxi_in": taxi_in,
            "crs_arr_time": crs_arr_time,
            "arr_time": arr_time,
            "arr_delay": arr_delay if not is_diverted else None,
            "cancelled": 0,
            "cancellation_code": None,
            "diverted": is_diverted,
            "crs_elapsed_time": crs_elapsed,
            "actual_elapsed_time": actual_elapsed if not is_diverted else None,
            "air_time": actual_air_time if not is_diverted else None,
            "distance": dist,
            "carrier_delay": carrier_delay,
            "weather_delay": weather_delay,
            "nas_delay": nas_delay,
            "security_delay": sec_delay,
            "late_aircraft_delay": late_ac_delay,
            "origin_temp_f": origin_temp,
            "origin_wind_mph": origin_wind,
            "origin_visibility_miles": origin_vis,
            "origin_weather_condition": origin_cond,
            "dest_temp_f": dest_temp,
            "dest_wind_mph": dest_wind,
            "dest_visibility_miles": dest_vis,
            "dest_weather_condition": dest_cond,
        })

        # Generate companion baggage event sample for ~10% of flights
        if i % 10 == 0 and not is_cancelled:
            num_bags = random.randint(20, min(140, aircraft_info.get("seat_capacity", 150)))
            delayed_bags = random.randint(0, 3) if arr_delay > 30 else 0
            baggage_events.append({
                "event_id": f"BAG-{flight_id}",
                "flight_id": flight_id,
                "carrier_code": carrier_code,
                "origin_airport": origin_code,
                "dest_airport": dest_code,
                "total_checked_bags": num_bags,
                "loaded_bags": num_bags - delayed_bags,
                "delayed_bags": delayed_bags,
                "mishandled_bag_rate_pct": round((delayed_bags / num_bags) * 100, 2) if num_bags > 0 else 0.0,
                "avg_carousel_wait_min": round(max(8, 14 + (taxi_in * 0.5) + np.random.normal(0, 2)), 1),
                "timestamp": act_dep_dt.strftime("%Y-%m-%d %H:%M:%S")
            })

    # Convert to DataFrames
    flights_df = pd.DataFrame(records)
    baggage_df = pd.DataFrame(baggage_events)
    
    # Save reference files to data/sample and data/raw
    for out_dir in [SAMPLE_DIR, RAW_DIR]:
        os.makedirs(out_dir, exist_ok=True)
        airports_df.to_csv(os.path.join(out_dir, "airports.csv"), index=False)
        airports_df.to_json(os.path.join(out_dir, "airports.json"), orient="records", indent=2)
        airlines_df.to_csv(os.path.join(out_dir, "airlines.csv"), index=False)
        fleet_df.to_csv(os.path.join(out_dir, "aircraft.csv"), index=False)
        flights_df.to_csv(os.path.join(out_dir, "flights_sample.csv"), index=False)
        baggage_df.to_csv(os.path.join(out_dir, "baggage_events.csv"), index=False)

    print(f"Successfully generated {len(flights_df)} flights, {len(airports_df)} airports, {len(airlines_df)} airlines, {len(fleet_df)} aircraft, and {len(baggage_df)} baggage events.")
    print(f"Files saved to {SAMPLE_DIR} and {RAW_DIR}")
    return flights_df

if __name__ == "__main__":
    generate_flight_dataset(30000)
