import streamlit as st
import math
import matplotlib.pyplot as plt
import requests
import folium
from streamlit_folium import st_folium

class Missile:
    def __init__(self, name, speed, angle, target_distance, target_lat, target_lon):
        self.name = name
        self.speed = speed
        self.angle = angle
        self.target_distance = target_distance
        self.target_lat = target_lat
        self.target_lon = target_lon
        self.x_log = []
        self.y_log = []

    def simulate_trajectory(self):
        angle_rad = math.radians(self.angle)
        vx = self.speed * math.cos(angle_rad)
        vy = self.speed * math.sin(angle_rad)
        g = 9.81

        # Calculate time of flight more robustly
        time_of_flight = (2 * vy) / g if vy > 0 else 0
        max_height = (vy ** 2) / (2 * g) if vy > 0 else 0
        calculated_range = (self.speed ** 2 * math.sin(2 * angle_rad)) / g if self.speed > 0 else 0

        st.write(f"**Calculated range:** {calculated_range:.2f} m")
        st.write(f"**Target distance:** {self.target_distance:.2f} m")
        st.write(f"**Max height:** {max_height:.2f} m")
        st.write(f"**Time of flight:** {time_of_flight:.2f} s")

        if self.target_distance > 0 and abs(calculated_range - self.target_distance) > self.target_distance * 0.1:
            st.warning("Missile may not hit target accurately!")

        # Trajectory simulation
        t = 0
        dt = 0.1
        self.x_log.clear()
        self.y_log.clear()
        while t <= time_of_flight:
            x = vx * t
            y = vy * t - 0.5 * g * t**2
            if y < 0:
                break
            self.x_log.append(x)
            self.y_log.append(y)
            t += dt

        # Plot trajectory
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(self.x_log, self.y_log, label="Trajectory")
        ax.axvline(x=self.target_distance, color='r', linestyle='--', label='Target')
        ax.plot(calculated_range, 0, 'go', markersize=10, label='Impact')
        ax.set_xlabel("Distance (m)")
        ax.set_ylabel("Altitude (m)")
        ax.set_title(f"{self.name} Trajectory Simulation")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        accuracy = 0
        if self.target_distance > 0:
            accuracy = abs(calculated_range - self.target_distance) / self.target_distance * 100
            st.success(f"Accuracy: {100 - accuracy:.1f}%")
        else:
            st.warning("Target distance is zero or invalid, cannot calculate accuracy.")

        return calculated_range

def get_coordinates():
    try:
        response = requests.get('https://ipinfo.io/')
        data = response.json()
        lat, lon = map(float, data['loc'].split(','))
        city = data.get('city', 'Unknown')
        region = data.get('region', 'Unknown')
        return lat, lon, city, region
    except Exception as e:
        st.warning(f"Could not get launch site coordinates: {e}")
        return None, None, "Unknown", "Unknown"

def show_map(lat, lon, city, region, target_lat, target_lon):
    map_obj = folium.Map(location=[lat, lon], zoom_start=5)
    folium.Marker([lat, lon], popup=f"Launch Site: {city}, {region}", icon=folium.Icon(color='blue')).add_to(map_obj)
    folium.Marker([target_lat, target_lon], popup="Target Location", icon=folium.Icon(color='red')).add_to(map_obj)
    folium.PolyLine([[lat, lon], [target_lat, target_lon]], color="green", weight=2.5).add_to(map_obj)
    st_folium(map_obj, width=700)

# Streamlit UI
st.title("🚀 Missile Launch Simulator")

with st.form("missile_form"):
    name = st.text_input("Missile Name", "Falcon")
    speed = st.number_input("Speed (m/s)", min_value=1.0, value=100.0)
    angle = st.slider("Launch Angle (degrees)", min_value=0, max_value=90, value=45)
    target_distance = st.number_input("Target Distance (m)", min_value=1.0, value=1000.0)
    target_lat = st.number_input("Target Latitude", value=40.7128)
    target_lon = st.number_input("Target Longitude", value=-74.0060)
    submit = st.form_submit_button("Launch Missile")

if submit:
    missile = Missile(name, speed, angle, target_distance, target_lat, target_lon)
    missile.simulate_trajectory()

    lat, lon, city, region = get_coordinates()
    if lat is not None and lon is not None:
        st.subheader("🌍 Launch Map")
        show_map(lat, lon, city, region, target_lat, target_lon)
