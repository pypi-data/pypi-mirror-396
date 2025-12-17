import time
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import importlib.resources as resources
from . import data


def get_locations(key):
    """Fetch all monitoring locations in the US from the OpenAQ API and save to CSV."""
    headers = {"X-API-Key": key}

    base_url = "https://api.openaq.org/v3/locations"
    all_locations = []
    page = 1

    while True:
        params = {
            'countries_id': 155,
            'limit': 1000,
            'page': page
        }
        response = requests.get(base_url, params=params, headers=headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            break

        data = response.json()

        if page == 1:
            print(f"Response keys: {data.keys()}")
            print(f"Meta info: {data.get('meta', {})}")

        results = data.get('results', [])

        if not results:
            break

        all_locations.extend(results)

        if len(results) < 1000:
            break

        page += 1

    print(f"\nTotal locations found: {len(all_locations)}")

    locations_df = pd.DataFrame([
        {
            'Location ID': loc['id'],
            'Name': loc['name'],
            'Latitude': loc.get('coordinates', {}).get('latitude'),
            'Longitude': loc.get('coordinates', {}).get('longitude')
        }
        for loc in all_locations
    ])

    geometry = [Point(xy) for xy in zip(locations_df['Longitude'], locations_df['Latitude'])]

    locations_gdf = gpd.GeoDataFrame(locations_df, geometry=geometry, crs="EPSG:4326")

    states = gpd.read_file(
        "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_20m.zip"
    )
    states = states.to_crs("EPSG:4326")

    result = gpd.sjoin(locations_gdf, states, how="left", predicate="within")

    locations_df['State'] = result['NAME'].values
    locations_df['Abbreviation'] = result['STUSPS'].values

    return locations_df


def get_sensorID(sampled_locations, key):
    """Fetch PM2.5 sensor IDs for each location from the OpenAQ API and save to CSV."""
    BASE_URL = "https://api.openaq.org/v3/locations"

    df = sampled_locations.copy()
    df["PM2.5 Sensor ID"] = None

    for i, loc_id in enumerate(df["Locations ID"]):
        if i % 60 == 0 and i > 0:
            print("Sleeping for 60 seconds to respect API rate limits...")
            time.sleep(60)
        url = f"{BASE_URL}/{loc_id}/sensors"
        params = {"parameter": "pm25", "limit": 100}
        headers = {"x-api-key": key}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data=response
            
            if data.get("results"):
                pm25_sensors = [
                    s["id"] for s in data["results"]
                    if s.get("parameter", {}).get("name") == "pm25"
                ]
                df.loc[i, "PM2.5 Sensor ID"] = ", ".join(map(str, pm25_sensors))if pm25_sensors else None
            else:
                df.loc[i, "PM2.5 Sensor ID"] = None
        except Exception as e:
            print(f"Error fetching sensors for location {loc_id}: {e}")
            df.loc[i, "PM2.5 Sensor ID"] = None

    return df
               
def sample_location(locations):
    """Sample up to 25 monitoring locations per state and save to CSV."""
    df  = locations.copy()

    sampled_df = (
        df.groupby("State", group_keys=False)
        .apply(lambda x: x.sample(n=25) if len(x) > 20 else x)
    )

    return sampled_df

	
states_info = pd.DataFrame()


def append_to_df(col, name):
    """Helper to append a column to the global states_info DataFrame."""
    global states_info
    states_info[name] = col

def state_info():
    """
    Extract state-level information from various Excel files
    bundled within the package and compile into a DataFrame.
    """
    files = {
        "edu": resources.files("usadata.data") / "MappingAmerica_Education.xlsx",
        "hdi": resources.files("usadata.data") / "MappingAmerica_HDI.xlsx",
        "housing": resources.files("usadata.data") / "MappingAmerica_Housing.xlsx",
        "env": resources.files("usadata.data") / "MappingAmerica_Environment.xlsx",
    }

    for key, path in files.items():
        df = pd.read_excel(path, sheet_name="State")
        df = df.drop(df.index[:15]).reset_index(drop=True)

        if key == "edu":
            append_to_df(df.iloc[:,42], "Not_Graduated")
            append_to_df(df.iloc[:,0], "States")

        elif key == "hdi":
            df = df.drop(df.index[:1]).reset_index(drop=True)
            append_to_df(df.iloc[:,2], "HDI")
            append_to_df(df.iloc[:,3], "Health_Index")
            append_to_df(df.iloc[:,4], "Education_Index")
            append_to_df(df.iloc[:,5], "Income_Index")

        elif key == "housing":
            df = df.drop(df.index[:1]).reset_index(drop=True)
            append_to_df(df.iloc[:,3], "Homeless_Ratio")
            append_to_df(df.iloc[:,4], "Unsheltered_Homeless")

        elif key == "env":
            df = df.drop(df.index[:1]).reset_index(drop=True)
            append_to_df(df.iloc[:,11], "Coal")
            append_to_df(df.iloc[:,14], "Natural_Gas")

    return states_info



def fetch_averages(sensor_ids, output_csv, key):
    """Fetch yearly average PM2.5 values for each sensor and save to CSV."""
    headers = {"x-api-key": key}

    df = sensor_ids.copy()
    df["PM25_Yearly_Avg"] = None

    # Helper to get summary average
    def get_summary_avg(sensor_id):
        url = f"https://api.openaq.org/v3/sensors/{sensor_id}"
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        js = r.json()["results"][0]
        return js["summary"]["avg"]

    # Main loop
    for i, sensor_id in enumerate(df["PM2.5 Sensor ID"]):
        if pd.isna(sensor_id):
            continue

        if i > 0 and i % 50 == 0:
            print("Sleeping 30 seconds to respect API limits…")
            time.sleep(30)

        print(f"Processing sensor {sensor_id} ({i+1}/{len(df)})...")

        try:
            yearly_avg = get_summary_avg(sensor_id)
            df.loc[i, "PM25_Yearly_Avg"] = yearly_avg
        except:
            df.loc[i, "PM25_Yearly_Avg"] = None

    # Save result
    df.to_csv(output_csv, index=False)
    print(f"\nSaved updated file {output_csv}")

    return output_csv


def merge_data(sensor_avg, state_info):
    """Merge sensor averages with state information and return the final DataFrame."""
    
    mean = sensor_avg.groupby("State")['PM25_Yearly_Avg'].mean()
    state_info['Avg_PM25'] = state_info["States"].map(mean)
    
    return state_info


def USdata():
    """Return the final clean dataset without running API functions."""
    sensor_path = resources.files(data) / "US_Locations_PM25_With_Averages.csv"
    states_path = resources.files(data) / "States_Data.csv"

    sensor_avgs = pd.read_csv(sensor_path)
    states_df = pd.read_csv(states_path)

    return merge_data(sensor_avgs, states_df)