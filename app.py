# Environmental impact overview with meaningful calculations
   
    
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
    padding: 1.2rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border: none;
}
.carpool-card {
    padding: 1.2rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #00C851 0%, #00FF7F 100%);
    color: white;
    box-shadow: 0 6px 20px rgba(0,200,81,0.3);
    border: none;
}
.sustainability-card {
    padding: 1.2rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    color: white;
    box-shadow: 0 6px 20px rgba(255,107,53,0.3);
}
.reward-badge {
    display: inline-block;
    padding: 0.4rem 1rem;
    border-radius: 25px;
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
    color: #333;
    font-weight: bold;
    margin: 0.3rem;
    box-shadow: 0 3px 10px rgba(255,215,0,0.4);
}
.eco-metrics {
    display: flex;
    justify-content: space-around;
    padding: 1.5rem;
    background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
    border-radius: 15px;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(33,150,243,0.2);
}
.metric-item {
    text-align: center;
}
.metric-item h3 {
    color: #1976D2;
    font-size: 1.8rem;
    margin-bottom: 0.3rem;
}
.savings-highlight {
    padding: 1rem;
    border-radius: 10px;
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
    color: white;
    margin: 0.5rem 0;
    box-shadow: 0 4px 12px rgba(76,175,80,0.3);
}
.impact-card {
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    text-align: center;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}
.bright-blue { background: linear-gradient(135deg, #2196F3 0%, #03DAC6 100%); color: white; }
.bright-purple { background: linear-gradient(135deg, #9C27B0 0%, #E91E63 100%); color: white; }
.bright-orange { background: linear-gradient(135deg, #FF9800 0%, #FF5722 100%); color: white; }
.bright-green { background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%); color: white; }
.bright-red { background: linear-gradient(135deg, #F44336 0%, #E91E63 100%); color: white; }
.bright-teal { background: linear-gradient(135deg, #009688 0%, #00BCD4 100%); color: white; }
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
    dist = np.sqrt(dist_lat**2 + dist_lng**2)
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

# Function to calculate meaningful environmental impact and savings
def calculate_environmental_impact(distance_km, transport_mode, passengers=1):
    """Calculate realistic CO2 emissions, cost savings, and environmental impact"""
    # Real-world CO2 emissions per km (kg) - based on EPA data
    emissions_per_km = {
        "solo_driving": 0.251,      # Average car emissions
        "carpool_2": 0.1255,       # Split between 2 people
        "carpool_3": 0.0837,       # Split between 3 people
        "carpool_4": 0.0628,       # Split between 4 people
        "public_transport": 0.089,  # Bus/train average
        "eco_route": 0.201,        # 20% reduction through efficient driving
        "bike": 0,
        "walk": 0
    }
    
    # Cost calculations (realistic US averages)
    gas_price_per_liter = 1.20  # $1.20 per liter
    fuel_consumption_per_km = 0.08  # 8L/100km average
    cost_per_km = gas_price_per_liter * fuel_consumption_per_km
    
    # Wear and tear, insurance, etc.
    total_cost_per_km = cost_per_km * 1.5  # Total driving cost
    
    solo_emissions = distance_km * emissions_per_km["solo_driving"]
    solo_cost = distance_km * total_cost_per_km
    
    mode_emissions = distance_km * emissions_per_km.get(transport_mode, emissions_per_km["solo_driving"])
    
    if "carpool" in transport_mode:
        mode_cost = solo_cost / passengers  # Split costs
    elif transport_mode == "public_transport":
        mode_cost = distance_km * 0.15  # ~$0.15/km for public transport
    else:
        mode_cost = solo_cost
    
    co2_saved = max(0, solo_emissions - mode_emissions)
    money_saved = max(0, solo_cost - mode_cost)
    
    # More accurate environmental equivalents
    trees_equivalent = co2_saved / 21.77  # One tree absorbs 21.77kg CO2/year (US Forest Service)
    coal_avoided = co2_saved / 2.23       # 1kg coal = 2.23kg CO2
    miles_not_driven = co2_saved / 0.404  # 1 mile driving = 0.404kg CO2
    
    return {
        "solo_emissions": round(solo_emissions, 3),
        "mode_emissions": round(mode_emissions, 3),
        "co2_saved": round(co2_saved, 3),
        "money_saved": round(money_saved, 2),
        "trees_equivalent": round(trees_equivalent, 2),
        "coal_avoided_kg": round(coal_avoided, 2),
        "equivalent_miles_saved": round(miles_not_driven, 1),
        "gas_saved_liters": round((co2_saved / emissions_per_km["solo_driving"]) * fuel_consumption_per_km, 2)
    }

# Main App Tabs
tab1, tab2, tab3 = st.tabs(["🗺️ Route Planning", "🚗 Carpooling", "🌱 Sustainability Tracker"])

with tab1:
    st.header("Smart Route Optimization")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Starting Point**")
        start_location = st.selectbox(
            "Select start location", 
            ["City Center", "Downtown", "Midtown", "Brooklyn", "Queens", "Central Park"],
            index=0
        )

    with col2:
        st.markdown("**Destination**")
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
        # Generate sample routes using original logic
        routes = generate_routes(
            start_location, 
            end_location, 
            {"avoid_tolls": avoid_tolls, "avoid_highways": avoid_highways}
        )
        
        # Create two columns for routes and map
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Route Options")
            
            # Display each route with more details and bright colors
            for i, route in enumerate(routes):
                # Calculate meaningful environmental impact
                transport_mode = "eco_route" if route['name'] == 'Eco-Friendly Route' else "solo_driving"
                impact = calculate_environmental_impact(route['distance_km'], transport_mode)
                
                if i == 0:  # Highlight recommended route
                    card_class = "bright-blue"
                    recommended_text = "✅ RECOMMENDED"
                elif route['name'] == 'Eco-Friendly Route':
                    card_class = "bright-green"
                    recommended_text = "🌱 ECO CHOICE"
                else:
                    card_class = "bright-orange"
                    recommended_text = ""
                    
                # Route card with detailed savings
                st.markdown(f"""
                <div class="route-card {card_class}">
                    <h4>{route['name']} {recommended_text}</h4>
                    <p>
                    <strong>📍 Distance:</strong> {route['distance_km']:.1f} km<br>
                    <strong>⏱️ Est. Time:</strong> {route['time_min']:.1f} minutes<br>
                    <strong>🚦 Congestion:</strong> {int(route['congestion']*100)}%<br>
                    <strong>💨 CO₂ Emissions:</strong> {impact['solo_emissions']:.2f} kg<br>
                    <strong>💰 Estimated Cost:</strong> ${(route['distance_km'] * 0.144):.2f}<br>
                    <strong>Features:</strong> {"Uses toll roads" if route['tolls'] else "No tolls"}, 
                    {"Uses highways" if route['highways'] else "Avoids highways"}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show savings for eco-friendly route
                if route['name'] == 'Eco-Friendly Route':
                    st.markdown(f"""
                    <div class="savings-highlight">
                        <strong>🌱 Environmental Savings:</strong><br>
                        • {impact['co2_saved']:.2f} kg CO₂ saved<br>
                        • Equivalent to {impact['equivalent_miles_saved']:.1f} miles not driven<br>
                        • {impact['gas_saved_liters']:.1f} liters of fuel saved<br>
                        • Equal to {impact['trees_equivalent']:.2f} trees planted
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("Route Map")
            # Create and display the map using original function
            route_map = create_route_map(start_location, end_location, routes)
            folium_static(route_map, width=700, height=500)
        
        # Traffic conditions along the route (original logic)
        st.subheader("Current Traffic Conditions")
        
        # Generate sample traffic incidents
        incidents = []
        if random.random() < 0.7:
            incidents.append({
                "type": "Accident",
                "location": f"Near {random.choice(['Broadway', 'Main St', '5th Avenue'])}",
                "delay": f"{random.randint(5, 20)} minutes",
                "severity": "Moderate"
            })
        
        if random.random() < 0.5:
            incidents.append({
                "type": "Construction",
                "location": f"On {random.choice(['Highway 101', 'Bridge St', 'Downtown'])}",
                "delay": f"{random.randint(3, 15)} minutes",
                "severity": "Minor"
            })
        
        # Display incidents
        if incidents:
            st.warning("⚠️ Traffic incidents detected on your route")
            for incident in incidents:
                st.markdown(f"**{incident['type']}** at {incident['location']} - Expected delay: {incident['delay']} ({incident['severity']} severity)")
        else:
            st.success("✅ No major incidents reported on your route")
        
        # Additional information
        st.subheader("Additional Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Traffic Forecast**")
            st.markdown("🔹 Traffic expected to improve in the next hour")
            st.markdown("🔹 Rush hour congestion from 4:30 PM - 6:00 PM")
        
        with col2:
            st.markdown("**Travel Tips**")
            st.markdown("🔹 Consider departing after 6:30 PM to avoid traffic")
            st.markdown("🔹 Check for updates before departure")
    else:
        # Show placeholder image when no routes are selected
        st.image("https://via.placeholder.com/800x400.png?text=Route+Map+(Enter+locations+and+click+Find+Routes)", use_container_width=True)

with tab2:
    st.header("🚗 Carpooling Hub")
    
    st.markdown("""
    <div class="eco-metrics">
        <div class="metric-item">
            <h3>👥 {}</h3>
            <p><strong>Carpools Joined</strong></p>
        </div>
        <div class="metric-item">
            <h3>💰 ${}</h3>
            <p><strong>Money Saved</strong></p>
        </div>
        <div class="metric-item">
            <h3>🌱 {}kg</h3>
            <p><strong>CO₂ Reduced</strong></p>
        </div>
        <div class="metric-item">
            <h3>⛽ {}L</h3>
            <p><strong>Fuel Saved</strong></p>
        </div>
    </div>
    """.format(
        st.session_state.carpools_joined,
        int(st.session_state.co2_saved * 2.8),  # Realistic money savings: ~$2.80 per kg CO2
        st.session_state.co2_saved,
        round(st.session_state.co2_saved * 3.98, 1)  # 1kg CO2 = ~3.98L fuel
    ), unsafe_allow_html=True)
    
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
                # Calculate carpool savings
                avg_distance = 18  # Average carpool distance
                carpool_impact = calculate_environmental_impact(avg_distance, f"carpool_{option['available_seats']+1}")
                
                st.markdown(f"""
                <div class="carpool-card">
                    <h4>🚗 {option['driver']} - {option['car']}</h4>
                    <p>
                    ⭐ <strong>Rating:</strong> {option['rating']}/5.0 | 
                    🕐 <strong>Departure:</strong> {option['departure_time']} | 
                    👥 <strong>{option['available_seats']} seats</strong> available<br>
                    💰 <strong>${option['cost_per_person']}/person</strong> | 
                    🌱 <strong>+{option['eco_points']} EcoPoints</strong> | 
                    📍 <strong>{option['route_match']}%</strong> route match
                    </p>
                    <div class="savings-highlight" style="margin-top: 0.8rem; background: rgba(255,255,255,0.2);">
                        <strong>🌍 Your Environmental Impact:</strong><br>
                        • Save {carpool_impact['co2_saved']:.1f} kg CO₂<br>
                        • Save ${carpool_impact['money_saved']:.2f} in costs<br>
                        • Equivalent to {carpool_impact['equivalent_miles_saved']:.0f} miles not driven
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"Join Ride", key=f"join_{i}"):
                    # Calculate realistic rewards
                    co2_reduction = round(random.uniform(2.1, 4.8), 1)
                    money_saved = round(co2_reduction * 2.8, 2)
                    
                    st.session_state.user_points += option['eco_points']
                    st.session_state.carpools_joined += 1
                    st.session_state.co2_saved += co2_reduction
                    
                    st.success(f"🎉 Carpool booked with {option['driver']}!")
                    st.success(f"💰 You'll save ${money_saved} and {co2_reduction}kg CO₂!")
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
        "🚴‍♂️ Try bike routes for trips under 5km",
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
