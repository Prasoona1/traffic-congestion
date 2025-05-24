import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from folium.features import DivIcon
import random
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="MobiSync Route Optimization",
    page_icon="🚦",
    layout="wide"
)

# Initialize session state for user data
if 'user_points' not in st.session_state:
    st.session_state.user_points = 1250
if 'trips_completed' not in st.session_state:
    st.session_state.trips_completed = 27
if 'co2_saved' not in st.session_state:
    st.session_state.co2_saved = 48.5
if 'carpools_joined' not in st.session_state:
    st.session_state.carpools_joined = 12
if 'total_distance' not in st.session_state:
    st.session_state.total_distance = 425.7
if 'money_saved' not in st.session_state:
    st.session_state.money_saved = 180

# Custom CSS
st.markdown("""
<style>
.title {
    font-size: 2rem;
    font-weight: bold;
    color: #1E88E5;
    text-align: center;
}
.route-card {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid #1E88E5;
}
.carpool-card {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    border: 2px solid #4CAF50;
    background-color: #f0f8ff;
}
.sustainability-card {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    background-color: #2E7D32;
    color: white;
}
.reward-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    background-color: #FFD700;
    color: #333;
    font-weight: bold;
    margin: 0.2rem;
}
.eco-metrics {
    display: flex;
    justify-content: space-around;
    padding: 1rem;
    background-color: #2E7D32;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.metric-item {
    text-align: center;
    color: white;
}
.traffic-info {
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 4px solid #FF9800;
    background-color: #FFF3E0;
}
.incident-card {
    padding: 0.8rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    background-color: #FFEBEE;
    border-left: 4px solid #F44336;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="title">🚦 MobiSync Route Optimization</p>', unsafe_allow_html=True)

# Sidebar for user profile and rewards
with st.sidebar:
    st.header("🌟 Your EcoProfile")
    
    # User stats
    st.markdown(f"""
    <div class="sustainability-card">
        <h4>🏆 EcoPoints: {st.session_state.user_points}</h4>
        <p>🚗 Trips Completed: {st.session_state.trips_completed}</p>
        <p>🌱 CO₂ Saved: {st.session_state.co2_saved} kg</p>
        <p>👥 Carpools Joined: {st.session_state.carpools_joined}</p>
        <p>📏 Total Distance: {st.session_state.total_distance} km</p>
        <p>💰 Money Saved: ${st.session_state.money_saved}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Achievement badges
    st.subheader("🏅 Achievements")
    badges = []
    if st.session_state.co2_saved > 40:
        badges.append("🌍 Eco Warrior")
    if st.session_state.carpools_joined > 10:
        badges.append("🤝 Social Driver")
    if st.session_state.trips_completed > 25:
        badges.append("🚀 Route Master")
    if st.session_state.user_points > 1000:
        badges.append("⭐ Premium Member")
    if st.session_state.total_distance > 400:
        badges.append("🛣 Distance Champion")
    
    for badge in badges:
        st.markdown(f'<span class="reward-badge">{badge}</span>', unsafe_allow_html=True)
    
    # Rewards store
    st.subheader("🎁 Rewards Store")
    rewards = [
        {"name": "Free Coffee", "points": 100, "icon": "☕"},
        {"name": "Gas Voucher $5", "points": 250, "icon": "⛽"},
        {"name": "Premium Features", "points": 500, "icon": "⭐"},
        {"name": "Plant a Tree", "points": 200, "icon": "🌳"},
        {"name": "Parking Discount", "points": 150, "icon": "🅿"}
    ]
    
    for reward in rewards:
        if st.button(f"{reward['icon']} {reward['name']} ({reward['points']} pts)"):
            if st.session_state.user_points >= reward['points']:
                st.session_state.user_points -= reward['points']
                st.success(f"Redeemed {reward['name']}! 🎉")
                st.rerun()
            else:
                st.error("Not enough points!")

# Function to generate route coordinates between two points with some randomness
def generate_route_coords(start_coords, end_coords, variation=0.01):
    """Generate a list of coordinates forming a route between start and end"""
    dist_lat = end_coords[0] - start_coords[0]
    dist_lng = end_coords[1] - start_coords[1]
    dist = np.sqrt(dist_lat*2 + dist_lng*2)
    num_points = max(5, int(dist * 100))
    
    route = []
    for i in range(num_points + 1):
        t = i / num_points
        lat = start_coords[0] + t * dist_lat + random.uniform(-variation, variation)
        lng = start_coords[1] + t * dist_lng + random.uniform(-variation, variation)
        route.append([lat, lng])
    
    route[0] = start_coords
    route[-1] = end_coords
    
    return route

# Function to create a map with routes and carpool pickup points
def create_route_map(start_loc, end_loc, routes, carpool_points=None, show_traffic=False):
    """Create a map with multiple route options and carpool pickup points"""
    locations = {
        "City Center": [40.712, -74.006],
        "Airport": [40.640, -73.779],
        "Downtown": [40.702, -74.015],
        "Midtown": [40.754, -73.984],
        "Brooklyn": [40.678, -73.944],
        "Queens": [40.728, -73.794],
        "Bronx": [40.837, -73.846],
        "Central Park": [40.785, -73.968],
        "Times Square": [40.758, -73.985],
        "Financial District": [40.707, -74.011]
    }
    
    start_coords = locations.get(start_loc, locations["City Center"])
    end_coords = locations.get(end_loc, locations["Airport"])
    
    center_lat = (start_coords[0] + end_coords[0]) / 2
    center_lng = (start_coords[1] + end_coords[1]) / 2
    route_map = folium.Map(location=[center_lat, center_lng], zoom_start=12, tiles="CartoDB positron")
    
    # Add markers for start and end points
    folium.Marker(
        location=start_coords,
        popup=start_loc,
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
        tooltip=f"Start: {start_loc}"
    ).add_to(route_map)
    
    folium.Marker(
        location=end_coords,
        popup=end_loc,
        icon=folium.Icon(color="red", icon="stop", prefix="fa"),
        tooltip=f"End: {end_loc}"
    ).add_to(route_map)
    
    # Add carpool pickup points if provided
    if carpool_points:
        for point in carpool_points:
            folium.Marker(
                location=point['coords'],
                popup=f"Carpool Pickup: {point['name']}<br>Passengers: {point['passengers']}",
                icon=folium.Icon(color="blue", icon="users", prefix="fa"),
                tooltip=f"Carpool: {point['name']}"
            ).add_to(route_map)
    
    # Add routes
    colors = ["blue", "purple", "orange", "darkgreen"]
    dash_patterns = [None, "5,5", "3,3", "10,5"]
    
    for i, route in enumerate(routes):
        variation = 0.005 * (i + 1)
        route_coords = generate_route_coords(start_coords, end_coords, variation)
        
        # Add traffic incidents for some routes
        if show_traffic and random.random() < 0.6:
            incident_idx = random.randint(1, len(route_coords) - 2)
            incident_loc = route_coords[incident_idx]
            
            folium.CircleMarker(
                location=incident_loc,
                radius=8,
                color="red",
                fill=True,
                fill_opacity=0.8,
                popup=f"🚨 Traffic incident: Delay of {random.randint(5, 15)} minutes"
            ).add_to(route_map)
        
        # Add route line
        folium.PolyLine(
            route_coords,
            color=colors[i % len(colors)],
            weight=4,
            opacity=0.8,
            dash_array=dash_patterns[i % len(dash_patterns)],
            tooltip=f"{route['name']} - {route['time_min']:.1f} min - {route['distance_km']:.1f} km"
        ).add_to(route_map)
        
        # Add route label
        mid_point = route_coords[len(route_coords) // 2]
        folium.map.Marker(
            mid_point,
            icon=DivIcon(
                icon_size=(150, 36),
                icon_anchor=(75, 18),
                html=f'<div style="font-size: 10pt; color: {colors[i % len(colors)]}; font-weight: bold; background: white; padding: 2px; border-radius: 3px;">{route["name"]}</div>'
            )
        ).add_to(route_map)
        
        # Add traffic density indicators
        if show_traffic:
            for j in range(1, len(route_coords) - 1, max(1, len(route_coords) // 5)):
                if j >= len(route_coords):
                    continue
                    
                congestion = route.get("congestion", 0.5)
                color = "green" if congestion < 0.5 else "orange" if congestion < 0.8 else "red"
                
                folium.CircleMarker(
                    location=route_coords[j],
                    radius=3,
                    color=color,
                    fill=True,
                    fill_opacity=0.7,
                    tooltip=f"Traffic density: {int(congestion * 100)}%"
                ).add_to(route_map)
    
    return route_map

# Function to generate route options
def generate_routes(start, end, preferences):
    """Generate route options based on preferences"""
    avoid_tolls = preferences.get("avoid_tolls", False)
    avoid_highways = preferences.get("avoid_highways", False)
    eco_mode = preferences.get("eco_mode", False)
    
    base_distance = 15 + random.uniform(-3, 3)
    base_time = 25 + random.uniform(-5, 5)
    
    routes = [
        {
            'name': 'Fastest Route',
            'distance_km': base_distance + random.uniform(0, 2),
            'time_min': base_time * (1.3 if avoid_highways else 1.0),
            'congestion': random.uniform(0.6, 0.8),
            'tolls': not avoid_tolls,
            'highways': not avoid_highways,
            'eco_rating': random.randint(6, 8),
            'fuel_cost': round(random.uniform(3.5, 5.2), 2)
        },
        {
            'name': 'Eco-Friendly Route',
            'distance_km': base_distance * 0.95,
            'time_min': base_time * 1.15,
            'congestion': random.uniform(0.4, 0.6),
            'tolls': False,
            'highways': False,
            'eco_rating': random.randint(8, 10),
            'fuel_cost': round(random.uniform(2.8, 4.1), 2)
        },
        {
            'name': 'Balanced Route',
            'distance_km': base_distance * 1.05,
            'time_min': base_time * 1.1,
            'congestion': random.uniform(0.5, 0.7),
            'tolls': random.choice([True, False]),
            'highways': random.choice([True, False]),
            'eco_rating': random.randint(7, 9),
            'fuel_cost': round(random.uniform(3.2, 4.8), 2)
        },
        {
            'name': 'Shortest Route',
            'distance_km': base_distance * 0.85,
            'time_min': base_time * 1.25,
            'congestion': random.uniform(0.7, 0.9),
            'tolls': False,
            'highways': False,
            'eco_rating': random.randint(6, 8),
            'fuel_cost': round(random.uniform(3.0, 4.3), 2)
        }
    ]
    
    return routes

# Function to generate carpool options
def generate_carpool_options():
    """Generate sample carpool options"""
    names = ["Sarah M.", "Mike R.", "Jessica L.", "David K.", "Amanda S.", "Chris P.", "Lisa W."]
    cars = ["Toyota Camry", "Honda Accord", "Tesla Model 3", "BMW 3 Series", "Nissan Altima", "Ford Fusion", "Hyundai Elantra"]
    
    carpool_options = []
    for i in range(random.randint(3, 6)):
        option = {
            "driver": random.choice(names),
            "car": random.choice(cars),
            "rating": round(random.uniform(4.2, 5.0), 1),
            "departure_time": f"{random.randint(7, 9)}:{random.choice(['00', '15', '30', '45'])} AM",
            "available_seats": random.randint(1, 3),
            "cost_per_person": round(random.uniform(5, 15), 2),
            "eco_points": random.randint(15, 35),
            "route_match": random.randint(82, 98),
            "verified": random.choice([True, False])
        }
        carpool_options.append(option)
    
    return carpool_options

# Function to calculate environmental impact
def calculate_environmental_impact(distance_km, transport_mode, passengers=1):
    """Calculate CO2 emissions and savings"""
    emissions_per_km = {
        "solo_driving": 0.21,
        "carpool_2": 0.105,
        "carpool_3": 0.07,
        "carpool_4": 0.0525,
        "public_transport": 0.05,
        "bike": 0,
        "walk": 0
    }
    
    solo_emissions = distance_km * emissions_per_km["solo_driving"]
    mode_emissions = distance_km * emissions_per_km.get(transport_mode, emissions_per_km["solo_driving"])
    co2_saved = solo_emissions - mode_emissions
    
    return {
        "solo_emissions": solo_emissions,
        "mode_emissions": mode_emissions,
        "co2_saved": max(0, co2_saved),
        "trees_equivalent": max(0, co2_saved / 22),
        "money_saved": max(0, co2_saved * 0.15)  # Rough estimate
    }

# Function to generate traffic incidents
def generate_traffic_incidents():
    """Generate sample traffic incidents"""
    incident_types = ["Accident", "Construction", "Road Closure", "Heavy Traffic", "Weather"]
    locations = ["Broadway", "Main St", "5th Avenue", "Highway 101", "Bridge St", "Downtown", "Uptown"]
    
    incidents = []
    num_incidents = random.randint(0, 3)
    
    for _ in range(num_incidents):
        incident = {
            "type": random.choice(incident_types),
            "location": f"{random.choice(['Near', 'On', 'At'])} {random.choice(locations)}",
            "delay": f"{random.randint(3, 25)} minutes",
            "severity": random.choice(["Minor", "Moderate", "Major"]),
            "description": random.choice([
                "Lane closure due to roadwork",
                "Multi-vehicle collision",
                "Stalled vehicle blocking lane",
                "Emergency vehicle activity",
                "Traffic signal malfunction"
            ])
        }
        incidents.append(incident)
    
    return incidents

# Main App Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🗺 Route Planning", "🚗 Carpooling", "🌱 Sustainability Tracker", "📊 Analytics"])

with tab1:
    st.header("Smart Route Optimization")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("*Starting Point*")
        start_location = st.selectbox(
            "Select start location", 
            ["City Center", "Downtown", "Midtown", "Brooklyn", "Queens", "Central Park"],
            index=0
        )

    with col2:
        st.markdown("*Destination*")
        end_location = st.selectbox(
            "Select destination", 
            ["Airport", "Financial District", "Times Square", "Bronx", "Brooklyn", "Queens"],
            index=0
        )

    # Route preferences
    st.subheader("Route Preferences")
    col1, col2, col3 = st.columns(3)
    with col1:
        avoid_tolls = st.checkbox("Avoid toll roads", False)
        avoid_highways = st.checkbox("Avoid highways", False)
        eco_mode = st.checkbox("🌱 Eco-friendly priority", False)

    with col2:
        optimize_for = st.radio(
            "Optimize for:",
            ["Time", "Distance", "Eco-Friendly", "Cost"],
            index=0
        )
        
        show_traffic = st.checkbox("Show real-time traffic", True)

    with col3:
        departure_time = st.selectbox(
            "Departure time:",
            ["Now", "In 30 minutes", "In 1 hour", "In 2 hours", "Custom time"],
            index=0
        )
        
        if departure_time == "Custom time":
            custom_time = st.time_input("Select time:", datetime.now().time())

    if st.button("Find Routes", type="primary"):
        routes = generate_routes(
            start_location, 
            end_location, 
            {"avoid_tolls": avoid_tolls, "avoid_highways": avoid_highways, "eco_mode": eco_mode}
        )
        
        # Sort routes based on optimization preference
        if optimize_for == "Time":
            routes.sort(key=lambda x: x['time_min'])
        elif optimize_for == "Distance":
            routes.sort(key=lambda x: x['distance_km'])
        elif optimize_for == "Eco-Friendly":
            routes.sort(key=lambda x: x['eco_rating'], reverse=True)
        elif optimize_for == "Cost":
            routes.sort(key=lambda x: x['fuel_cost'])
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Route Options")
            
            for i, route in enumerate(routes):
                impact = calculate_environmental_impact(route['distance_km'], "solo_driving")
                
                if i == 0:
                    card_color = "#38b6ff"
                    text_color = "white"
                    recommended_text = "✅ RECOMMENDED"
                elif route['name'] == 'Eco-Friendly Route':
                    card_color = "#4CAF50"
                    text_color = "white"
                    recommended_text = "🌱 ECO CHOICE"
                else:
                    card_color = "#9C27B0" if i == 1 else "#FF9800"
                    text_color = "white"
                    recommended_text = ""
                
                st.markdown(f"""
                <div class="route-card" style="background-color: {card_color}; color: {text_color};">
                    <h4>{route['name']} {recommended_text}</h4>
                    <p>
                    <strong>Distance:</strong> {route['distance_km']:.1f} km<br>
                    <strong>Est. Time:</strong> {route['time_min']:.1f} minutes<br>
                    <strong>Eco Rating:</strong> {route['eco_rating']}/10 🌱<br>
                    <strong>Fuel Cost:</strong> ${route['fuel_cost']}<br>
                    <strong>CO₂ Emissions:</strong> {impact['solo_emissions']:.2f} kg<br>
                    <strong>Traffic:</strong> {int(route['congestion']*100)}% congested<br>
                    <strong>Features:</strong> {"Tolls" if route['tolls'] else "No tolls"}, {"Highways" if route['highways'] else "Local roads"}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Add a button to select this route
                if st.button(f"Select {route['name']}", key=f"select_route_{i}"):
                    # Update user stats when a route is selected
                    st.session_state.trips_completed += 1
                    st.session_state.total_distance += route['distance_km']
                    st.session_state.user_points += 10 + (route['eco_rating'] * 2)
                    if route['name'] == 'Eco-Friendly Route':
                        st.session_state.co2_saved += impact['co2_saved']
                        st.session_state.user_points += 15  # Bonus for eco choice
                    st.success(f"🎉 Route selected! +{10 + (route['eco_rating'] * 2)} EcoPoints earned!")
                    st.rerun()
        
        with col2:
            st.subheader("Route Map")
            route_map = create_route_map(start_location, end_location, routes, show_traffic=show_traffic)
            folium_static(route_map, width=700, height=500)
        
        # Traffic conditions
        st.subheader("🚦 Current Traffic Conditions")
        incidents = generate_traffic_incidents()
        
        if incidents:
            st.warning(f"⚠ {len(incidents)} traffic incident(s) detected on your route")
            for incident in incidents:
                severity_color = "#FF5722" if incident['severity'] == "Major" else "#FF9800" if incident['severity'] == "Moderate" else "#4CAF50"
                st.markdown(f"""
                <div class="incident-card" style="border-left-color: {severity_color};">
                    <strong>{incident['type']}</strong> {incident['location']}<br>
                    <em>{incident['description']}</em><br>
                    Expected delay: <strong>{incident['delay']}</strong> ({incident['severity']} severity)
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No major incidents reported on your route")
        
        # Alternative transportation suggestions
        st.subheader("🚌 Alternative Transportation")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("*Public Transit*\n🚇 Subway: 35 min\n💰 Cost: $2.75\n🌱 CO₂: 0.8 kg saved")
        
        with col2:
            st.info("*Bike Share*\n🚴‍♂ CitiBike: 45 min\n💰 Cost: $4.95\n🌱 CO₂: 3.2 kg saved")
        
        with col3:
            st.info("*Walking + Transit*\n🚶‍♂ Combined: 40 min\n💰 Cost: $2.75\n🌱 CO₂: 2.8 kg saved")

with tab2:
    st.header("🚗 Carpooling Hub")
    
    st.markdown("""
    <div class="eco-metrics">
        <div class="metric-item">
            <h3>👥 {}</h3>
            <p>Carpools Joined</p>
        </div>
        <div class="metric-item">
            <h3>💰 ${}</h3>
            <p>Money Saved</p>
        </div>
        <div class="metric-item">
            <h3>🌱 {}kg</h3>
            <p>CO₂ Reduced</p>
        </div>
        <div class="metric-item">
            <h3>⭐ {}</h3>
            <p>Eco Points Earned</p>
        </div>
    </div>
    """.format(
        st.session_state.carpools_joined,
        st.session_state.money_saved,
        round(st.session_state.co2_saved * 0.5, 1),  # Portion from carpooling
        st.session_state.user_points // 4  # Portion from carpooling
    ), unsafe_allow_html=True)
    
    # Carpool search
    col1, col2 = st.columns(2)
    with col1:
        carpool_start = st.selectbox("From", ["City Center", "Downtown", "Midtown", "Brooklyn"], key="carpool_from")
        carpool_date = st.date_input("Travel Date", datetime.now())
        max_detour = st.slider("Max detour (minutes)", 0, 15, 5)
    
    with col2:
        carpool_end = st.selectbox("To", ["Airport", "Financial District", "Times Square", "Queens"], key="carpool_to")
        carpool_time = st.time_input("Departure Time", datetime.now().time())
        price_range = st.select_slider("Price range", ["$0-5", "$5-10", "$10-15", "$15+"], value="$5-10")
    
    if st.button("Find Carpool Matches", type="primary"):
        carpool_options = generate_carpool_options()
        
        st.subheader("Available Carpool Options")
        
        for i, option in enumerate(carpool_options):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                verified_badge = "✅ Verified" if option['verified'] else ""
                st.markdown(f"""
                <div class="carpool-card">
                    <h4>🚗 {option['driver']} - {option['car']} {verified_badge}</h4>
                    <p>
                    ⭐ Rating: {option['rating']}/5.0 ({random.randint(15, 150)} rides) | 
                    🕐 Departure: {option['departure_time']} | 
                    👥 {option['available_seats']} seats available<br>
                    💰 ${option['cost_per_person']}/person | 
                    🌱 +{option['eco_points']} EcoPoints | 
                    📍 {option['route_match']}% route match<br>
                    🛡 {"Fully insured" if option['verified'] else "Standard coverage"} | 
                    💬 Instant messaging available
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"Join Ride", key=f"join_{i}"):
                    st.session_state.user_points += option['eco_points']
                    st.session_state.carpools_joined += 1
                    st.session_state.co2_saved += 2.5
                    st.session_state.money_saved += round(random.uniform(3, 8), 2)
                    st.success(f"🎉 Carpool booked with {option['driver']}!")
                    st.balloons()
                    st.rerun()
                
                if st.button(f"Message", key=f"msg_{i}"):
                    st.info(f"💬 Message sent to {option['driver']}")
    
    # Quick carpool actions
    st.subheader("🚙 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Find Instant Rides", use_container_width=True):
            st.info("Searching for rides departing in the next 30 minutes...")
    
    with col2:
        if st.button("📅 Schedule Weekly Commute", use_container_width=True):
            st.info("Set up recurring carpool for your daily commute")
    
    with col3:
        if st.button("👥 Create Carpool Group", use_container_width=True):
            st.info("Start a private group with friends or colleagues")
