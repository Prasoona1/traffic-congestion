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
    background-color: yellow;
}
.sustainability-card {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    background-color: brown;
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
    background-color: #e8f5e8;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.metric-item {
    text-align: center;
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
    
    # Rewards store
    st.subheader("🎁 Rewards Store")
    rewards = [
        {"name": "Free Coffee", "points": 100, "icon": "☕"},
        {"name": "Gas Voucher $5", "points": 250, "icon": "⛽"},
        {"name": "Premium Features", "points": 500, "icon": "⭐"},
        {"name": "Plant a Tree", "points": 200, "icon": "🌳"}
    ]
    
    for reward in rewards:
        if st.button(f"{reward['icon']} {reward['name']} ({reward['points']} pts)"):
            if st.session_state.user_points >= reward['points']:
                st.session_state.user_points -= reward['points']
                st.success(f"Redeemed {reward['name']}! 🎉")
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
def create_route_map(start_loc, end_loc, routes, carpool_points=None):
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
    colors = ["blue", "purple", "orange"]
    
    for i, route in enumerate(routes):
        variation = 0.005 * (i + 1)
        route_coords = generate_route_coords(start_coords, end_coords, variation)
        
        # Add route line
        folium.PolyLine(
            route_coords,
            color=colors[i % len(colors)],
            weight=4,
            opacity=0.8,
            tooltip=f"{route['name']} - {route['time_min']:.1f} min"
        ).add_to(route_map)
    
    return route_map

# Function to generate carpool options
def generate_carpool_options():
    """Generate sample carpool options"""
    names = ["Sarah M.", "Mike R.", "Jessica L.", "David K.", "Amanda S."]
    cars = ["Toyota Camry", "Honda Accord", "Tesla Model 3", "BMW 3 Series", "Nissan Altima"]
    
    carpool_options = []
    for i in range(3):
        option = {
            "driver": random.choice(names),
            "car": random.choice(cars),
            "rating": round(random.uniform(4.5, 5.0), 1),
            "departure_time": f"{random.randint(7, 9)}:{random.choice(['00', '15', '30', '45'])} AM",
            "available_seats": random.randint(1, 3),
            "cost_per_person": round(random.uniform(5, 15), 2),
            "eco_points": random.randint(15, 30),
            "route_match": random.randint(85, 98)
        }
        carpool_options.append(option)
    
    return carpool_options

# Function to calculate environmental impact
def calculate_environmental_impact(distance_km, transport_mode, passengers=1):
    """Calculate CO2 emissions and savings"""
    # CO2 emissions per km (kg)
    emissions_per_km = {
        "solo_driving": 0.21,
        "carpool_2": 0.105,  # Split between 2 people
        "carpool_3": 0.07,   # Split between 3 people
        "carpool_4": 0.0525, # Split between 4 people
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
        "trees_equivalent": max(0, co2_saved / 22)  # 1 tree absorbs ~22kg CO2/year
    }

# Main App Tabs
tab1, tab2, tab3 = st.tabs(["🗺 Route Planning", "🚗 Carpooling", "🌱 Sustainability Tracker"])

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
    col1, col2 = st.columns(2)
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
        
        departure_time = st.selectbox(
            "Departure time:",
            ["Now", "In 30 minutes", "In 1 hour", "In 2 hours"],
            index=0
        )

    if st.button("Find Routes", type="primary"):
        base_distance = 15 + random.uniform(-3, 3)
        base_time = 25 + random.uniform(-5, 5)
        
        routes = [
            {
                'name': 'Fastest Route',
                'distance_km': base_distance + random.uniform(0, 2),
                'time_min': base_time * (1.2 if avoid_highways else 1.0),
                'congestion': random.uniform(0.6, 0.8),
                'tolls': not avoid_tolls,
                'highways': not avoid_highways,
                'eco_rating': random.randint(6, 8)
            },
            {
                'name': 'Eco-Friendly Route',
                'distance_km': base_distance * 0.95,
                'time_min': base_time * 1.15,
                'congestion': random.uniform(0.4, 0.6),
                'tolls': False,
                'highways': False,
                'eco_rating': random.randint(8, 10)
            },
            {
                'name': 'Balanced Route',
                'distance_km': base_distance * 1.05,
                'time_min': base_time * 1.1,
                'congestion': random.uniform(0.5, 0.7),
                'tolls': random.choice([True, False]),
                'highways': random.choice([True, False]),
                'eco_rating': random.randint(7, 9)
            }
        ]
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Route Options")
            
            for i, route in enumerate(routes):
                # Calculate environmental impact
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
                    card_color = "#ff5757"
                    text_color = "white"
                    recommended_text = ""
                
                st.markdown(f"""
                <div class="route-card" style="background-color: {card_color}; color: {text_color};">
                    <h4>{route['name']} {recommended_text}</h4>
                    <p>
                    <strong>Distance:</strong> {route['distance_km']:.1f} km<br>
                    <strong>Est. Time:</strong> {route['time_min']:.1f} minutes<br>
                    <strong>Eco Rating:</strong> {route['eco_rating']}/10 🌱<br>
                    <strong>CO₂ Emissions:</strong> {impact['solo_emissions']:.2f} kg<br>
                    <strong>Features:</strong> {"Uses toll roads" if route['tolls'] else "No tolls"}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("Route Map")
            route_map = create_route_map(start_location, end_location, routes)
            folium_static(route_map, width=700, height=500)

with tab2:
    st.header("🚗 Carpooling Hub")
    
    st.markdown("""
    <div class="eco-metrics">
        <div class="metric-item">
            <h3>👥 12</h3>
            <p>Carpools Joined</p>
        </div>
        <div class="metric-item">
            <h3>💰 $180</h3>
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
        carpool_start = st.selectbox("From", ["City Center", "Downtown", "Midtown", "Brooklyn"], key="carpool_from")
        carpool_date = st.date_input("Travel Date", datetime.now())
    
    with col2:
        carpool_end = st.selectbox("To", ["Airport", "Financial District", "Times Square", "Queens"], key="carpool_to")
        carpool_time = st.time_input("Departure Time", datetime.now().time())
    
    if st.button("Find Carpool Matches", type="primary"):
        carpool_options = generate_carpool_options()
        
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
                    💰 ${option['cost_per_person']}/person | 
                    🌱 +{option['eco_points']} EcoPoints | 
                    📍 {option['route_match']}% route match
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"Join Ride", key=f"join_{i}"):
                    st.session_state.user_points += option['eco_points']
                    st.session_state.carpools_joined += 1
                    st.session_state.co2_saved += 2.5  # Estimated CO2 savings
                    st.success(f"🎉 Carpool booked with {option['driver']}!")
                    st.balloons()
    
    # Option to offer a ride
    st.subheader("🚙 Offer a Ride")
    
    with st.expander("Become a Driver"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Your Car Model")
            st.number_input("Available Seats", min_value=1, max_value=4, value=2)
        
        with col2:
            st.number_input("Cost per Person ($)", min_value=0.0, value=8.0, step=0.5)
            st.text_area("Additional Notes (optional)")
        
        if st.button("Post Your Ride", type="secondary"):
            reward_points = random.randint(20, 40)
            st.session_state.user_points += reward_points
            st.success(f"🚗 Ride posted successfully! +{reward_points} EcoPoints earned!")

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
        money_saved = st.session_state.co2_saved * 0.5  # Rough estimate
        st.metric(
            label="💰 Gas Money Saved",
            value=f"${money_saved:.0f}",
            delta=f"+$12 this week"
        )
    
    # Weekly challenge
    st.subheader("🏆 Weekly Eco Challenge")
    
    current_progress = (st.session_state.co2_saved % 10) / 10 * 100
    st.progress(current_progress / 100)
    st.write(f"Save 10kg CO₂ this week - Progress: {current_progress:.0f}%")
    
    if current_progress >= 100:
        st.success("🎉 Challenge completed! +100 bonus EcoPoints!")
    
    # Sustainability tips
    st.subheader("💡 Eco-Friendly Tips")
    
    tips = [
        "🚗 Carpool 2+ times per week to reduce emissions by 50%",
        "🚴‍♂ Try bike routes for trips under 5km",
        "🚌 Use public transport during peak hours to avoid traffic",
        "⚡ Choose electric or hybrid vehicles for eco points bonus",
        "📱 Plan combined trips to reduce total distance traveled"
    ]
    
    for tip in random.sample(tips, 3):
        st.info(tip)
    
    # Carbon footprint tracker
    st.subheader("📊 Monthly Carbon Footprint")
    
    # Generate sample data for chart
    dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
    co2_data = [random.uniform(0.5, 3.0) for _ in dates]
    
    chart_data = pd.DataFrame({
        'Date': dates,
        'CO₂ Emissions (kg)': co2_data
    })
    
    st.line_chart(chart_data.set_index('Date'))
    
    # Leaderboard
    st.subheader("🏅 Community Leaderboard")
    
    leaderboard_data = {
        'Rank': [1, 2, 3, 4, 5],
        'User': ['EcoWarrior23', 'GreenDriver', 'You', 'CarpoolKing', 'NatureLover'],
        'EcoPoints': [1580, 1420, st.session_state.user_points, 1180, 1050],
        'CO₂ Saved (kg)': [72.3, 64.1, st.session_state.co2_saved, 53.2, 47.8]
    }
    
    leaderboard_df = pd.DataFrame(leaderboard_data)
    st.dataframe(leaderboard_df, use_container_width=True)
    
    # Rewards redemption history
    with st.expander("🎁 Rewards History"):
        st.write("Recent redemptions:")
        st.write("• ☕ Free Coffee - 100 points (2 days ago)")
        st.write("• 🌳 Plant a Tree - 200 points (1 week ago)")
        st.write("• ⛽ Gas Voucher - 250 points (2 weeks ago)")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🌱 <strong>MobiSync</strong> - Making transportation smarter and more sustainable</p>
    <p>Join the eco-friendly movement! Every trip counts towards a greener future.</p>
</div>
""", unsafe_allow_html=True)
