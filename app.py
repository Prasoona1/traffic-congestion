import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import requests
import json

# Set page configuration
st.set_page_config(
    page_title="MobiSync India - Hyderabad Route Optimization",
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

# Google Maps API Configuration
# Note: In production, store this in environment variables or Streamlit secrets
GOOGLE_MAPS_API_KEY = st.secrets.get("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY_HERE")

# Custom CSS (keeping the original styling)
st.markdown("""
<style>
.title {
    font-size: 2rem;
    font-weight: bold;
    color: #FF6B35;
    text-align: center;
}
.route-card {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid #FF6B35;
}
.carpool-card {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    border: 2px solid #4CAF50;
    background-color: #E8F5E8;
}
.sustainability-card {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    background-color: #138808;
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
    background-color: #138808;
    border-radius: 0.5rem;
    margin: 1rem 0;
    color: white;
}
.metric-item {
    text-align: center;
}
.map-container {
    border-radius: 0.5rem;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
""", unsafe_allow_html=True)

# Google Maps Integration Functions
def get_google_maps_directions(origin, destination, api_key, mode='driving', alternatives=True):
    """
    Get directions from Google Maps Directions API
    """
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    
    params = {
        'origin': origin,
        'destination': destination,
        'key': api_key,
        'mode': mode,
        'alternatives': alternatives,
        'traffic_model': 'best_guess',
        'departure_time': 'now'
    }
    
    try:
        response = requests.get(base_url, params=params)
        return response.json()
    except Exception as e:
        st.error(f"Error fetching directions: {e}")
        return None

def get_google_maps_distance_matrix(origins, destinations, api_key, mode='driving'):
    """
    Get distance matrix from Google Maps Distance Matrix API
    """
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    
    params = {
        'origins': '|'.join(origins),
        'destinations': '|'.join(destinations),
        'key': api_key,
        'mode': mode,
        'traffic_model': 'best_guess',
        'departure_time': 'now'
    }
    
    try:
        response = requests.get(base_url, params=params)
        return response.json()
    except Exception as e:
        st.error(f"Error fetching distance matrix: {e}")
        return None

def create_google_maps_embed(origin, destination, api_key, mode='driving'):
    """
    Create Google Maps embed URL for displaying route
    """
    base_url = "https://www.google.com/maps/embed/v1/directions"
    
    params = {
        'key': api_key,
        'origin': origin,
        'destination': destination,
        'mode': mode,
        'avoid': 'tolls' if st.session_state.get('avoid_tolls', False) else '',
    }
    
    # Remove empty parameters
    params = {k: v for k, v in params.items() if v}
    
    # Build URL
    param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{param_string}"

def parse_google_directions(directions_data):
    """
    Parse Google Directions API response into readable format
    """
    if not directions_data or directions_data['status'] != 'OK':
        return []
    
    routes = []
    for route in directions_data['routes']:
        leg = route['legs'][0]  # Assuming single leg journey
        
        route_info = {
            'distance_km': leg['distance']['value'] / 1000,
            'duration_min': leg['duration']['value'] / 60,
            'duration_in_traffic_min': leg.get('duration_in_traffic', {}).get('value', 0) / 60,
            'start_address': leg['start_address'],
            'end_address': leg['end_address'],
            'summary': route['summary'],
            'steps': []
        }
        
        # Parse steps
        for step in leg['steps']:
            step_info = {
                'instruction': step['html_instructions'],
                'distance': step['distance']['text'],
                'duration': step['duration']['text'],
                'maneuver': step.get('maneuver', '')
            }
            route_info['steps'].append(step_info)
        
        routes.append(route_info)
    
    return routes

# Enhanced location data with more precise coordinates
HYDERABAD_LOCATIONS = {
    "HITEC City": {"coords": [17.4435, 78.3772], "address": "HITEC City, Cyberabad, Telangana, India"},
    "Rajiv Gandhi International Airport": {"coords": [17.2403, 78.4294], "address": "Rajiv Gandhi International Airport, Shamshabad, Telangana, India"},
    "Secunderabad": {"coords": [17.4399, 78.4983], "address": "Secunderabad, Telangana, India"},
    "Banjara Hills": {"coords": [17.4126, 78.4482], "address": "Banjara Hills, Hyderabad, Telangana, India"},
    "Jubilee Hills": {"coords": [17.4239, 78.4738], "address": "Jubilee Hills, Hyderabad, Telangana, India"},
    "Gachibowli": {"coords": [17.4399, 78.3482], "address": "Gachibowli, Hyderabad, Telangana, India"},
    "Kukatpally": {"coords": [17.4850, 78.4867], "address": "Kukatpally, Hyderabad, Telangana, India"},
    "Begumpet": {"coords": [17.4504, 78.4677], "address": "Begumpet, Hyderabad, Telangana, India"},
    "Charminar": {"coords": [17.3616, 78.4747], "address": "Charminar, Hyderabad, Telangana, India"},
    "Tank Bund": {"coords": [17.4126, 78.4747], "address": "Tank Bund, Hyderabad, Telangana, India"},
    "Kondapur": {"coords": [17.4617, 78.3617], "address": "Kondapur, Hyderabad, Telangana, India"},
    "Madhapur": {"coords": [17.4483, 78.3915], "address": "Madhapur, Hyderabad, Telangana, India"},
    "Ameerpet": {"coords": [17.4375, 78.4482], "address": "Ameerpet, Hyderabad, Telangana, India"},
    "Miyapur": {"coords": [17.5067, 78.3592], "address": "Miyapur, Hyderabad, Telangana, India"},
    "LB Nagar": {"coords": [17.3498, 78.5522], "address": "LB Nagar, Hyderabad, Telangana, India"}
}

# Title
st.markdown('<p class="title">🚦 MobiSync India - Hyderabad Route Optimization</p>', unsafe_allow_html=True)

# API Key Configuration
if GOOGLE_MAPS_API_KEY == "YOUR_API_KEY_HERE":
    st.warning("⚠ Google Maps API key not configured. Please add your API key to Streamlit secrets.")
    st.info("To use Google Maps integration, add your API key in Streamlit Cloud secrets or .streamlit/secrets.toml")

# Sidebar (keeping original sidebar code)
with st.sidebar:
    st.header("🌟 Your EcoProfile")
    
    # User stats
    st.markdown(f"""
    <div class="sustainability-card">
        <h4>🏆 EcoPoints: {st.session_state.user_points}</h4>
        <p>🚗 Trips Completed: {st.session_state.trips_completed}</p>
        <p>🌱 CO₂ Saved: {st.session_state.co2_saved} kg</p>
        <p>👥 Carpools Joined: {st.session_state.carpools_joined}</p>
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
    
    for badge in badges:
        st.markdown(f'<span class="reward-badge">{badge}</span>', unsafe_allow_html=True)
    
    # Google Maps Settings
    st.subheader("🗺 Map Settings")
    map_view = st.selectbox("Map View", ["roadmap", "satellite", "hybrid", "terrain"])
    show_traffic = st.checkbox("Show Traffic Layer", True)
    
    # Rewards store (keeping original)
    st.subheader("🎁 Rewards Store")
    rewards = [
        {"name": "Free Chai", "points": 100, "icon": "☕"},
        {"name": "Petrol Voucher ₹300", "points": 250, "icon": "⛽"},
        {"name": "Premium Features", "points": 500, "icon": "⭐"},
        {"name": "Plant a Tree", "points": 200, "icon": "🌳"},
        {"name": "Metro Card Top-up ₹200", "points": 180, "icon": "🚇"},
        {"name": "Swiggy Voucher ₹150", "points": 150, "icon": "🍽"}
    ]
    
    for reward in rewards:
        if st.button(f"{reward['icon']} {reward['name']} ({reward['points']} pts)"):
            if st.session_state.user_points >= reward['points']:
                st.session_state.user_points -= reward['points']
                st.success(f"Redeemed {reward['name']}! 🎉")
            else:
                st.error("Not enough points!")

# Helper functions (keeping existing ones and adding new)
def calculate_environmental_impact(distance_km, transport_mode, passengers=1):
    """Calculate CO2 emissions and savings"""
    emissions_per_km = {
        "solo_driving": 0.21,
        "carpool_2": 0.105,
        "carpool_3": 0.07,
        "carpool_4": 0.0525,
        "public_transport": 0.05,
        "metro": 0.03,
        "auto_rickshaw": 0.15,
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
        "trees_equivalent": max(0, co2_saved / 22)
    }

# Main App Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🗺 Route Planning", "🚗 Carpooling", "🌱 Sustainability Tracker", "📍 Live Maps"])

with tab1:
    st.header("Smart Route Optimization - Hyderabad")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("Starting Point")
        start_location = st.selectbox(
            "Select start location", 
            list(HYDERABAD_LOCATIONS.keys()),
            index=0
        )

    with col2:
        st.markdown("Destination")
        end_location = st.selectbox(
            "Select destination", 
            list(HYDERABAD_LOCATIONS.keys()),
            index=1
        )

    # Route preferences
    st.subheader("Route Preferences")
    col1, col2 = st.columns(2)
    with col1:
        avoid_tolls = st.checkbox("Avoid toll roads", False)
        st.session_state.avoid_tolls = avoid_tolls
        avoid_highways = st.checkbox("Avoid ORR (Outer Ring Road)", False)
        eco_mode = st.checkbox("🌱 Eco-friendly priority", False)

    with col2:
        optimize_for = st.radio(
            "Optimize for:",
            ["Time", "Distance", "Eco-Friendly", "Cost"],
            index=0
        )
        
        departure_time = st.selectbox(
            "Departure time:",
            ["Now", "In 30 minutes", "In 1 hour", "In 2 hours"],
            index=0
        )

    if st.button("Find Routes with Google Maps", type="primary"):
        if GOOGLE_MAPS_API_KEY != "YOUR_API_KEY_HERE":
            origin_address = HYDERABAD_LOCATIONS[start_location]["address"]
            destination_address = HYDERABAD_LOCATIONS[end_location]["address"]
            
            # Get real-time directions from Google Maps
            with st.spinner("Fetching real-time route data from Google Maps..."):
                directions_data = get_google_maps_directions(
                    origin_address, 
                    destination_address, 
                    GOOGLE_MAPS_API_KEY
                )
                
                if directions_data and directions_data['status'] == 'OK':
                    routes = parse_google_directions(directions_data)
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.subheader("🗺 Google Maps Routes")
                        
                        for i, route in enumerate(routes):
                            # Calculate environmental impact
                            impact = calculate_environmental_impact(route['distance_km'], "solo_driving")
                            
                            # Determine traffic delay
                            traffic_delay = route['duration_in_traffic_min'] - route['duration_min'] if route['duration_in_traffic_min'] > 0 else 0
                            
                            card_color = "#FF6B35" if i == 0 else "#2196F3"
                            recommended_text = "⚡ RECOMMENDED" if i == 0 else f"🛣 ROUTE {i+1}"
                            
                            st.markdown(f"""
                            <div class="route-card" style="background-color: {card_color}; color: white;">
                                <h4>{route['summary']} {recommended_text}</h4>
                                <p>
                                <strong>Distance:</strong> {route['distance_km']:.1f} km<br>
                                <strong>Duration:</strong> {route['duration_min']:.0f} minutes<br>
                                <strong>With Traffic:</strong> {route['duration_in_traffic_min']:.0f} minutes<br>
                                <strong>Traffic Delay:</strong> +{traffic_delay:.0f} minutes<br>
                                <strong>CO₂ Emissions:</strong> {impact['solo_emissions']:.2f} kg<br>
                                <strong>Fuel Cost:</strong> ₹{route['distance_km'] * 8:.0f}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader("🗺 Interactive Route Map")
                        
                        # Create Google Maps embed
                        maps_embed_url = create_google_maps_embed(
                            origin_address, 
                            destination_address, 
                            GOOGLE_MAPS_API_KEY
                        )
                        
                        # Display embedded map
                        st.markdown(f"""
                        <div class="map-container">
                            <iframe
                                width="100%"
                                height="400"
                                style="border:0"
                                loading="lazy"
                                allowfullscreen
                                referrerpolicy="no-referrer-when-downgrade"
                                src="{maps_embed_url}">
                            </iframe>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display turn-by-turn directions
                        st.subheader("🧭 Turn-by-Turn Directions")
                        
                        if routes:
                            selected_route = routes[0]  # Use first (recommended) route
                            
                            for i, step in enumerate(selected_route['steps'][:10]):  # Show first 10 steps
                                # Clean HTML tags from instructions
                                instruction = step['instruction'].replace('<b>', '').replace('</b>', '')
                                instruction = instruction.replace('<div style="font-size:0.9em">', ' (').replace('</div>', ')')
                                
                                st.write(f"{i+1}.** {instruction}")
                                st.write(f"   📏 {step['distance']} • ⏱ {step['duration']}")
                
                else:
                    st.error("Unable to fetch route data from Google Maps. Please check your API key and try again.")
        
        else:
            # Fallback to original route generation when API key is not available
            st.info("Using sample route data. Configure Google Maps API key for real-time data.")
            # ... (keep original route generation code as fallback)

with tab4:
    st.header("📍 Live Maps & Traffic")
    
    if GOOGLE_MAPS_API_KEY != "YOUR_API_KEY_HERE":
        st.subheader("🗺 Hyderabad Traffic Overview")
        
        # Traffic overview map centered on Hyderabad
        traffic_map_url = f"""
        https://www.google.com/maps/embed/v1/view?key={GOOGLE_MAPS_API_KEY}&center=17.3850,78.4867&zoom=11&maptype={map_view}
        """
        
        st.markdown(f"""
        <div class="map-container">
            <iframe
                width="100%"
                height="500"
                style="border:0"
                loading="lazy"
                allowfullscreen
                referrerpolicy="no-referrer-when-downgrade"
                src="{traffic_map_url}">
            </iframe>
        </div>
        """, unsafe_allow_html=True)
        
        # Live traffic data for major routes
        st.subheader("🚦 Live Traffic Status")
        
        major_routes = [
            ("HITEC City", "Gachibowli"),
            ("Secunderabad", "HITEC City"),
            ("Banjara Hills", "Rajiv Gandhi International Airport"),
            ("Kukatpally", "Ameerpet")
        ]
        
        if st.button("Refresh Traffic Data"):
            traffic_data = []
            
            for origin, destination in major_routes:
                origin_addr = HYDERABAD_LOCATIONS[origin]["address"]
                dest_addr = HYDERABAD_LOCATIONS[destination]["address"]
                
                # Get distance matrix data
                matrix_data = get_google_maps_distance_matrix(
                    [origin_addr], [dest_addr], GOOGLE_MAPS_API_KEY
                )
                
                if matrix_data and matrix_data['status'] == 'OK':
                    element = matrix_data['rows'][0]['elements'][0]
                    if element['status'] == 'OK':
                        duration = element['duration']['value'] / 60
                        duration_in_traffic = element.get('duration_in_traffic', {}).get('value', 0) / 60
                        distance = element['distance']['value'] / 1000
                        
                        traffic_delay = duration_in_traffic - duration if duration_in_traffic > 0 else 0
                        
                        # Determine traffic status
                        if traffic_delay < 5:
                            status = "🟢 Light"
                            status_color = "#4CAF50"
                        elif traffic_delay < 15:
                            status = "🟡 Moderate"
                            status_color = "#FF9800"
                        else:
                            status = "🔴 Heavy"
                            status_color = "#F44336"
                        
                        traffic_data.append({
                            'Route': f"{origin} → {destination}",
                            'Distance': f"{distance:.1f} km",
                            'Normal Time': f"{duration:.0f} min",
                            'Current Time': f"{duration_in_traffic:.0f} min",
                            'Delay': f"+{traffic_delay:.0f} min",
                            'Status': status
                        })
            
            if traffic_data:
                df = pd.DataFrame(traffic_data)
                st.dataframe(df, use_container_width=True)
        
        # Place search functionality
        st.subheader("🔍 Search Places in Hyderabad")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("Search for a place", placeholder="e.g., Inorbit Mall, Charminar, etc.")
        
        with col2:
            if st.button("Search"):
                if search_query:
                    # Create search map embed
                    search_map_url = f"""
                    https://www.google.com/maps/embed/v1/place?key={GOOGLE_MAPS_API_KEY}&q={search_query},Hyderabad,Telangana&zoom=15
                    """
                    
                    st.markdown(f"""
                    <div class="map-container">
                        <iframe
                            width="100%"
                            height="300"
                            style="border:0"
                            loading="lazy"
                            allowfullscreen
                            referrerpolicy="no-referrer-when-downgrade"
                            src="{search_map_url}">
                        </iframe>
                    </div>
                    """, unsafe_allow_html=True)
    
    else:
        st.warning("Google Maps API key required for live traffic data and interactive maps.")
        st.info("Please configure your API key to access this feature.")

# Keep the rest of the tabs (tab2 and tab3) exactly as they were in the original code
with tab2:
    st.header("🚗 Carpooling Hub - Hyderabad")
    
    st.markdown("""
    <div class="eco-metrics">
        <div class="metric-item">
            <h3>👥 12</h3>
            <p>Carpools Joined</p>
        </div>
        <div class="metric-item">
            <h3>💰 ₹2,400</h3>
            <p>Money Saved</p>
        </div>
        <div class="metric-item">
            <h3>🌱 25.3kg</h3>
            <p>CO₂ Reduced</p>
        </div>
        <div class="metric-item">
            <h3>⭐ 350</h3>
            <p>Eco Points Earned</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Carpool search
    col1, col2 = st.columns(2)
    with col1:
        carpool_start = st.selectbox("From", list(HYDERABAD_LOCATIONS.keys())[:4], key="carpool_from")
        carpool_date = st.date_input("Travel Date", datetime.now())
    
    with col2:
        carpool_end = st.selectbox("To", list(HYDERABAD_LOCATIONS.keys())[1:5], key="carpool_to")
        carpool_time = st.time_input("Departure Time", datetime.now().time())
    
    if st.button("Find Carpool Matches", type="primary"):
        # Generate sample carpool options
        names = ["Priya S.", "Rajesh K.", "Anita M.", "Vikram R.", "Sneha P.", "Arjun T.", "Kavya L."]
        cars = ["Maruti Swift", "Hyundai i20", "Honda City", "Toyota Innova", "Tata Nexon", "Mahindra XUV300", "Kia Seltos"]
        
        carpool_options = []
        for i in range(3):
            option = {
                "driver": random.choice(names),
                "car": random.choice(cars),
                "rating": round(random.uniform(4.5, 5.0), 1),
                "departure_time": f"{random.randint(7, 9)}:{random.choice(['00', '15', '30', '45'])} AM",
                "available_seats": random.randint(1, 3),
                "cost_per_person": round(random.uniform(50, 200), 0),
                "eco_points": random.randint(15, 30),
                "route_match": random.randint(85, 98)
            }
            carpool_options.append(option)
        
        st.subheader("Available Carpool Options")
        
        for i, option in enumerate(carpool_options):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="carpool-card">
                    <h4>🚗 {option['driver']} - {option['car']}</h4>
                    <p>
                    ⭐ Rating: {option['rating']}/5.0 | 
                    🕐 Departure: {option['departure_time']} | 
                    👥 {option['available_seats']} seats available<br>
                    💰 ₹{option['cost_per_person']:.0f}/person | 
                    🌱 +{option['eco_points']} EcoPoints | 
                    📍 {option['route_match']}% route match
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"Join Ride", key=f"join_{i}"):
                    st.session_state.user_points += option['eco_points']
                    st.session_state.carpools_joined += 1
                    st.session_state.co2_saved += 2.5
                    st.success(f"🎉 Carpool booked with {option['driver']}!")
                    st.balloons()

with tab3:
    st.header("🌱 Sustainability Dashboard")
    
    # Environmental impact overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🌍 Total CO₂ Saved",
            value=f"{st.session_state.co2_saved:.1f} kg",
            delta=f"+2.3 kg this week"
        )
    
    with col2:
        trees_saved = st.session_state.co2_saved / 22
        st.metric(
            label="🌳 Trees Equivalent",
            value=f"{trees_saved:.1f} trees",
            delta=f"+0.1 trees this week"
        )
    
    with col3:
        money_saved = st.session_state.co2_saved * 12
        st.metric(
            label="💰 Fuel Money Saved",
            value=f"₹{money_saved:.0f}",
            delta=f"+₹180 this week"
        )
    
    # Weekly challenge
    st.subheader("🏆 Weekly Eco Challenge")
    
    current_progress = (st.session_state.co2_saved % 10) / 10 * 100
    st.progress(current_progress / 100)
    st.write(f"Save 10kg CO₂ this week - Progress: {current_progress:.0f}%")
    
    if current_progress >= 100:
        st.success("🎉 Challenge completed! +100 bonus EcoPoints!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🌱 <strong>MobiSync India</strong> - Making Hyderabad transportation smarter and more sustainable</p>
    <p>Join the eco-friendly movement! Every trip counts towards a greener Hyderabad. 🇮🇳</p>
    <p style="font-size: 0.9em;">Powered by Google Maps • Supporting Telangana's Green Transportation Initiative</p>
</div>
""", unsafe_allow_html=True)

