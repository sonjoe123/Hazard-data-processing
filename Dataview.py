import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import MarkerCluster

# --- Load the files ---
hazards_df = pd.read_excel("Waze data type Hazards.xlsx")  # Excel file
with open("Waze.json", "r") as f:
    waze_data = json.load(f)

# --- Extract alerts from JSON ---
waze_alerts = waze_data.get("alerts", [])
waze_df = pd.json_normalize(waze_alerts)

# --- Frequency Plots ---
def plot_frequency(data, column, title, rotation=45):
    counts = data[column].value_counts()
    plt.figure(figsize=(12, 4))
    sns.barplot(x=counts.index, y=counts.values)
    plt.title(title)
    plt.xlabel(column)
    plt.ylabel("Count")
    plt.xticks(rotation=rotation)
    plt.tight_layout()
    plt.show()

# Plot hazard type frequency from Excel file
if 'type' in hazards_df.columns:
    plot_frequency(hazards_df, 'type', 'Hazard Types in Excel Data')

# Plot subtype frequency from Waze JSON
if 'subtype' in waze_df.columns:
    plot_frequency(waze_df, 'subtype', 'Waze Hazard Subtypes', rotation=90)

# --- Summary Statistics ---
print("\n--- Hazards Excel Summary ---")
print(hazards_df.describe(include='all'))

print("\n--- Waze JSON Summary ---")
print(waze_df[['type', 'subtype', 'confidence', 'reliability']].describe(include='all'))

# --- Interactive Map (optional) ---
def create_map(df, lat_col, lon_col, label_col='subtype', map_name="Hazard Map"):
    if lat_col not in df.columns or lon_col not in df.columns:
        print("Latitude/Longitude columns not found.")
        return
    fmap = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=8)
    cluster = MarkerCluster().add_to(fmap)
    for _, row in df.iterrows():
        popup_text = f"{label_col}: {row.get(label_col, '')}"
        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=popup_text
        ).add_to(cluster)
    fmap.save(f"{map_name}.html")
    print(f"{map_name}.html saved.")

# Make Waze hazard map
if 'location.y' in waze_df.columns and 'location.x' in waze_df.columns:
    create_map(waze_df, 'location.y', 'location.x', label_col='subtype', map_name="Waze_Hazard_Map")
