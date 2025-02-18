import pandas as pd
import geopandas as gpd
import folium
import json
from flask import Flask, render_template

app = Flask(__name__)

# Load GeoJSON
geojson_path = r"C:\Users\Rono\Desktop\Folium\kenya.geojson"
gdf = gpd.read_file(geojson_path)

# Load Rainfall Data
excel_path = r"E:\Agriculture project\rainfall_analysis.xlsx"
df_2024 = pd.read_excel(excel_path)

# Ensure consistent column names
df_2024 = df_2024.melt(id_vars=['Date'], var_name="County", value_name="Value")

# Standardize county names
df_2024["County"] = df_2024["County"].str.strip().str.upper()
gdf["COUNTY_NAM"] = gdf["COUNTY_NAM"].str.strip().str.upper()

# Fix county name mismatches
corrections = {
    "THARAKA-NITHI": "THARAKA - NITHI",
    "ELGEYO-MARAKWET": "ELEGEYO-MARAKWET",
    "TRANS NZOIA": "TRANS NZOIA",
}
df_2024["County"] = df_2024["County"].replace(corrections)

# Convert Date to datetime
df_2024["Date"] = pd.to_datetime(df_2024["Date"])

# Filter for 2024 data
df_2024_2024 = df_2024[df_2024["Date"].dt.year == 2024]

# Compute yearly average per county
df_2024_avg = df_2024_2024.groupby("County", as_index=False)["Value"].mean()

# Merge with GeoJSON
gdf = gdf.merge(df_2024_avg, left_on="COUNTY_NAM", right_on="County", how="left")

# Filter out counties with missing data
gdf = gdf.dropna(subset=["Value"])

# Convert filtered GeoJSON for Folium
filtered_geojson = json.loads(gdf.to_json())

@app.route("/")
def index():
    # Create Map
    m = folium.Map(location=[1.2921, 36.8219], zoom_start=6, tiles="OpenStreetMap")

    # Add Choropleth Layer
    folium.Choropleth(
        geo_data=filtered_geojson,
        name="choropleth",
        data=gdf,
        columns=["COUNTY_NAM", "Value"],
        key_on="feature.properties.COUNTY_NAM",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="PNR 2024 Average",
    ).add_to(m)

    # **Save Map to STATIC folder**
    map_path = "static/map.html"
    m.save(map_path)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
