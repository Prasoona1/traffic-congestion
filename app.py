import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from folium.features import DivIcon
import random
from datetime import datetime, timedelta
import hashlib

# Set page configuration
st.set_page_config(
    page_title="MobiSync Route Optimization",
    page_icon="🚦",
    layout="wide"
)

# Initialize session state for user management and carpooling
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'carpool_offers' not in st.session_state:
    st.session_state.carpool_offers = []
if 'carpool_requests' not in st.session_state:
    st.session_state.carpool_requests = []

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
}
.user-card {
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
    background-color: #f9f9f9;
}
.carpool-card {
    padding: 1rem;
    border: 1px solid #2E8B57;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
    background-color: #f0fff0;
}
.success-message {
    padding: 0.5rem;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 0.25rem;
    color: #155724;
}
.error-message {
    padding: 0.5rem;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 0.25rem;
    color: #721c24;
}
</style>
""", unsafe_allow_html=True)

# User Authentication Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password, phone, car_info=None):
    if username in st.session_state.users:
        return False, "Username already exists"
    
    st.session_state.users[username] = {
        'email': email,
        'password': hash_password(password),
        'phone': phone,
        'car_info': car_info,
        'rating': 5.0,
        'trips_completed': 0,
        'registration_date': datetime.now()
    }
    return True, "Registration successful"

def login_user(username, password):
    if username in st.session_state.users:
        if st.session_state.users[username]['password'] == hash_password(password):
            st.session_state.current_user = username
            return True
    return False

def logout_user():
    st.session_state.current_user = None

# Carpooling Functions
def create_carpool_offer(driver, start_loc, end_loc, departure_time, seats_available, price_per_seat, notes=""):
    offer = {
        'id': len(st.session_state.carpool_offers) + 1,
        'driver': driver,
        'start_location': start_loc,
        'end_location': end_loc,
        'departure_time': departure_time,
        'seats_available': seats_available,
        'price_per_seat': price_per_seat,
        'notes': notes,
        'passengers': [],
        'created_at': datetime.now(),
        'status': 'active'
    }
    st.session_state.carpool_offers.append(offer)
    return offer['id']

def create_carpool_request(passenger, start_loc, end_loc, departure_time, max_price, notes=""):
    request = {
        'id': len(st.session_state.carpool_requests) + 1,
        'passenger': passenger,
        'start_location': start_loc,
        'end_location': end_loc,
        'departure_time': departure_time,
        'max_price': max_price,
        'notes': notes,
        'created_at': datetime.now(),
        'status': 'active'
    }
    st.session_state.carpool_requests.append(request)
    return request['id']

def join_carpool(offer_id, passenger):
    for offer in st.session_state.carpool_offers:
        if offer['id'] == offer_id and len(offer['passengers']) < offer['seats_available']:
            offer['passengers'].append(passenger)
            return True
    return False

# Route generation functions (keeping the original ones)
def generate_route_coords(start_coords, end_coords, variation=0.01):
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

def create_route_map(start_loc, end_loc, routes):
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
    
    colors = ["blue", "purple", "orange"]
    
    for i, route in enumerate(routes):
        variation = 0.005 * (i + 1)
        route_coords = generate_route_coords(start_coords, end_coords, variation)
        
        folium.PolyLine(
            route_coords,
            color=colors[i % len(colors)],
            weight=4,
            opacity=0.8,
            tooltip=f"{route['name']} - {route['time_min']:.1f} min"
        ).add_to(route_map)
    
    return route_map

def generate_routes(start, end, preferences):
    avoid_tolls = preferences.get("avoid_tolls", False)
    avoid_highways = preferences.get("avoid_highways", False)
    
    base_distance = 15 + random.uniform(-3, 3)
    base_time = 25 + random.uniform(-5, 5)
    
    routes = [
        {
            'name': 'Fastest Route',
            'distance_km': base_distance + random.uniform(0, 2),
            'time_min': base_time * (1.2 if avoid_highways else 1.0),
            'congestion': random.uniform(0.6, 0.8),
            'tolls': not avoid_tolls,
            'highways': not avoid_highways
        },
        {
            'name': 'Shortest Route',
            'distance_km': base_distance * 0.85,
            'time_min': base_time * 1.2,
            'congestion': random.uniform(0.7, 0.9),
            'tolls': False,
            'highways': False
        },
        {
            'name': 'Eco-Friendly Route',
            'distance_km': base_distance * 1.1,
            'time_min': base_time * 1.1,
            'congestion': random.uniform(0.5, 0.7),
            'tolls': random.choice([True, False]),
            'highways': random.choice([True, False])
        }
    ]
    
    return routes

# -----------------------------
# Main App
# -----------------------------

# Title
st.markdown('<p class="title">🚦 MobiSync Route Optimization & Carpooling</p>', unsafe_allow_html=True)

# Sidebar for user authentication
with st.sidebar:
    st.header("User Account")
    
    if st.session_state.current_user is None:
        # Login/Register tabs
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login")
            login_username = st.text_input("Username", key="login_user")
            login_password = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Login"):
                if login_user(login_username, login_password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with tab2:
            st.subheader("Register")
            reg_username = st.text_input("Username", key="reg_user")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_pass")
            reg_phone = st.text_input("Phone Number", key="reg_phone")
            
            st.write("**Car Information (Optional)**")
            car_make = st.text_input("Car Make/Model", key="car_make")
            car_year = st.number_input("Year", min_value=1990, max_value=2024, value=2020, key="car_year")
            car_seats = st.number_input("Available Seats", min_value=1, max_value=8, value=4, key="car_seats")
            
            if st.button("Register"):
                if reg_username and reg_email and reg_password and reg_phone:
                    car_info = None
                    if car_make:
                        car_info = {
                            'make_model': car_make,
                            'year': car_year,
                            'seats': car_seats
                        }
                    
                    success, message = register_user(reg_username, reg_email, reg_password, reg_phone, car_info)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all required fields")
    
    else:
        # User is logged in
        user_info = st.session_state.users[st.session_state.current_user]
        st.success(f"Welcome, {st.session_state.current_user}!")
        st.write(f"**Email:** {user_info['email']}")
        st.write(f"**Rating:** ⭐ {user_info['rating']:.1f}")
        st.write(f"**Trips Completed:** {user_info['trips_completed']}")
        
        if st.button("Logout"):
            logout_user()
            st.rerun()

# Main content
if st.session_state.current_user is None:
    st.warning("Please login or register to access all features")
    st.info("You can still use basic route planning without an account")

# Navigation
if st.session_state.current_user:
    nav_option = st.selectbox(
        "Select Feature:",
        ["Route Planning", "Offer Carpool", "Find Carpool", "My Carpools", "Browse Community"]
    )
else:
    nav_option = "Route Planning"

# Route Planning (available to all users)
if nav_option == "Route Planning":
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

    st.subheader("Route Preferences")
    col1, col2 = st.columns(2)
    with col1:
        avoid_tolls = st.checkbox("Avoid toll roads", False)
        avoid_highways = st.checkbox("Avoid highways", False)

    with col2:
        optimize_for = st.radio(
            "Optimize for:",
            ["Time", "Distance", "Eco-Friendly"],
            index=0
        )
        
        departure_time = st.selectbox(
            "Departure time:",
            ["Now", "In 30 minutes", "In 1 hour", "In 2 hours"],
            index=0
        )

    if st.button("Find Routes", type="primary"):
        routes = generate_routes(
            start_location, 
            end_location, 
            {"avoid_tolls": avoid_tolls, "avoid_highways": avoid_highways}
        )
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Route Options")
            
            for i, route in enumerate(routes):
                if i == 0:
                    card_color = "#38b6ff"
                    text_color = "white"
                    recommended_text = "✅ RECOMMENDED"
                elif i == 1:
                    card_color = "#ff5757"
                    text_color = "white"
                    recommended_text = ""
                else:
                    card_color = "#57e964"
                    text_color = "white"
                    recommended_text = ""
                    
                st.markdown(f"""
                <div class="route-card" style="background-color: {card_color}; color: {text_color};">
                    <h4>{route['name']} {recommended_text}</h4>
                    <p>
                    <strong>Distance:</strong> {route['distance_km']:.1f} km<br>
                    <strong>Est. Time:</strong> {route['time_min']:.1f} minutes<br>
                    <strong>Congestion:</strong> {int(route['congestion']*100)}%<br>
                    <strong>Features:</strong> {"Uses toll roads" if route['tolls'] else "No tolls"}, 
                    {"Uses highways" if route['highways'] else "Avoids highways"}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("Route Map")
            route_map = create_route_map(start_location, end_location, routes)
            folium_static(route_map, width=700, height=500)
        
        # Show carpooling suggestions if user is logged in
        if st.session_state.current_user:
            st.subheader("💡 Carpooling Suggestions")
            matching_offers = [offer for offer in st.session_state.carpool_offers 
                             if offer['start_location'] == start_location and offer['end_location'] == end_location
                             and offer['status'] == 'active' and len(offer['passengers']) < offer['seats_available']]
            
            if matching_offers:
                st.success(f"Found {len(matching_offers)} carpool option(s) for your route!")
                for offer in matching_offers[:3]:  # Show top 3
                    st.markdown(f"""
                    <div class="carpool-card">
                        <strong>Driver:</strong> {offer['driver']} ⭐ {st.session_state.users.get(offer['driver'], {}).get('rating', 5.0):.1f}<br>
                        <strong>Departure:</strong> {offer['departure_time']}<br>
                        <strong>Available Seats:</strong> {offer['seats_available'] - len(offer['passengers'])}<br>
                        <strong>Price per Seat:</strong> ${offer['price_per_seat']:.2f}<br>
                        <strong>Notes:</strong> {offer['notes'] or 'None'}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No carpooling options found for this route. Consider creating an offer!")

# Carpool Offering (registered users only)
elif nav_option == "Offer Carpool":
    st.header("🚗 Offer a Carpool Ride")
    
    user_info = st.session_state.users[st.session_state.current_user]
    if not user_info.get('car_info'):
        st.warning("Please update your profile with car information to offer rides")
        st.stop()
    
    col1, col2 = st.columns(2)
    with col1:
        offer_start = st.selectbox("Starting Point", 
            ["City Center", "Downtown", "Midtown", "Brooklyn", "Queens", "Central Park", "Times Square", "Financial District"])
        offer_date = st.date_input("Departure Date", datetime.now().date())
        offer_seats = st.number_input("Available Seats", min_value=1, max_value=user_info['car_info']['seats'], value=3)
    
    with col2:
        offer_end = st.selectbox("Destination", 
            ["Airport", "Financial District", "Times Square", "Bronx", "Brooklyn", "Queens", "City Center", "Downtown"])
        offer_time = st.time_input("Departure Time", datetime.now().time())
        offer_price = st.number_input("Price per Seat ($)", min_value=0.0, value=10.0, step=0.50)
    
    offer_notes = st.text_area("Additional Notes (optional)", placeholder="e.g., No smoking, music preferences, pickup points...")
    
    if st.button("Create Carpool Offer", type="primary"):
        departure_datetime = f"{offer_date} {offer_time}"
        offer_id = create_carpool_offer(
            st.session_state.current_user, offer_start, offer_end, 
            departure_datetime, offer_seats, offer_price, offer_notes
        )
        st.success(f"Carpool offer created successfully! Offer ID: {offer_id}")

# Find Carpool (registered users only)
elif nav_option == "Find Carpool":
    st.header("🔍 Find a Carpool Ride")
    
    col1, col2 = st.columns(2)
    with col1:
        search_start = st.selectbox("From", 
            ["City Center", "Downtown", "Midtown", "Brooklyn", "Queens", "Central Park", "Times Square", "Financial District"])
        search_date = st.date_input("Travel Date", datetime.now().date())
    
    with col2:
        search_end = st.selectbox("To", 
            ["Airport", "Financial District", "Times Square", "Bronx", "Brooklyn", "Queens", "City Center", "Downtown"])
        max_price = st.number_input("Maximum Price per Seat ($)", min_value=0.0, value=20.0, step=0.50)
    
    if st.button("Search Rides"):
        matching_offers = [offer for offer in st.session_state.carpool_offers 
                          if offer['start_location'] == search_start and offer['end_location'] == search_end
                          and offer['price_per_seat'] <= max_price and offer['status'] == 'active'
                          and len(offer['passengers']) < offer['seats_available']]
        
        if matching_offers:
            st.success(f"Found {len(matching_offers)} available ride(s)!")
            
            for offer in matching_offers:
                col1, col2 = st.columns([3, 1])
                with col1:
                    driver_rating = st.session_state.users.get(offer['driver'], {}).get('rating', 5.0)
                    driver_trips = st.session_state.users.get(offer['driver'], {}).get('trips_completed', 0)
                    
                    st.markdown(f"""
                    <div class="carpool-card">
                        <strong>Driver:</strong> {offer['driver']} ⭐ {driver_rating:.1f} ({driver_trips} trips)<br>
                        <strong>Route:</strong> {offer['start_location']} → {offer['end_location']}<br>
                        <strong>Departure:</strong> {offer['departure_time']}<br>
                        <strong>Available Seats:</strong> {offer['seats_available'] - len(offer['passengers'])}/{offer['seats_available']}<br>
                        <strong>Price:</strong> ${offer['price_per_seat']:.2f} per seat<br>
                        <strong>Notes:</strong> {offer['notes'] or 'None'}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"Join Ride", key=f"join_{offer['id']}"):
                        if join_carpool(offer['id'], st.session_state.current_user):
                            st.success("Successfully joined the carpool!")
                            st.rerun()
                        else:
                            st.error("Unable to join - ride may be full")
        else:
            st.info("No rides found matching your criteria. Consider creating a ride request!")
    
    # Create ride request section
    st.subheader("Or Create a Ride Request")
    req_notes = st.text_area("Request Notes", placeholder="Looking for a ride, flexible with time...")
    
    if st.button("Create Ride Request"):
        req_id = create_carpool_request(
            st.session_state.current_user, search_start, search_end,
            f"{search_date} flexible", max_price, req_notes
        )
        st.success(f"Ride request created! Request ID: {req_id}")

# My Carpools (registered users only)
elif nav_option == "My Carpools":
    st.header("🚙 My Carpool Activities")
    
    tab1, tab2, tab3 = st.tabs(["My Offers", "My Bookings", "My Requests"])
    
    with tab1:
        st.subheader("My Carpool Offers")
        user_offers = [offer for offer in st.session_state.carpool_offers if offer['driver'] == st.session_state.current_user]
        
        if user_offers:
            for offer in user_offers:
                status_color = "🟢" if offer['status'] == 'active' else "🔴"
                st.markdown(f"""
                <div class="carpool-card">
                    {status_color} <strong>Offer #{offer['id']}</strong><br>
                    <strong>Route:</strong> {offer['start_location']} → {offer['end_location']}<br>
                    <strong>Departure:</strong> {offer['departure_time']}<br>
                    <strong>Passengers:</strong> {len(offer['passengers'])}/{offer['seats_available']}<br>
                    <strong>Passengers:</strong> {', '.join(offer['passengers']) if offer['passengers'] else 'None yet'}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("You haven't created any carpool offers yet.")
    
    with tab2:
        st.subheader("My Carpool Bookings") 
        user_bookings = [offer for offer in st.session_state.carpool_offers if st.session_state.current_user in offer['passengers']]
        
        if user_bookings:
            for booking in user_bookings:
                driver_rating = st.session_state.users.get(booking['driver'], {}).get('rating', 5.0)
                st.markdown(f"""
                <div class="carpool-card">
                    <strong>Booking #{booking['id']}</strong><br>
                    <strong>Driver:</strong> {booking['driver']} ⭐ {driver_rating:.1f}<br>
                    <strong>Route:</strong> {booking['start_location']} → {booking['end_location']}<br>
                    <strong>Departure:</strong> {booking['departure_time']}<br>
                    <strong>Price:</strong> ${booking['price_per_seat']:.2f}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("You haven't booked any carpool rides yet.")
    
    with tab3:
        st.subheader("My Ride Requests")
        user_requests = [req for req in st.session_state.carpool_requests if req['passenger'] == st.session_state.current_user]
        
        if user_requests:
            for request in user_requests:
                status_color = "🟡" if request['status'] == 'active' else "🔴"
                st.markdown(f"""
                <div class="carpool-card">
                    {status_color} <strong>Request #{request['id']}</strong><br>
                    <strong>Route:</strong> {request['start_location']} → {request['end_location']}<br>
                    <strong>Departure:</strong> {request['departure_time']}<br>
                    <strong>Max Price:</strong> ${request['max_price']:.2f}<br>
                    <strong>Notes:</strong> {request['notes'] or 'None'}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("You haven't created any ride requests yet.")

# Browse Community (registered users only)
elif nav_option == "Browse Community":
    st.header("🌟 Community Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Users", len(st.session_state.users))
    with col2:
        st.metric("Active Offers", len([o for o in st.session_state.carpool_offers if o['status'] == 'active']))
    with col3:
        st.metric("Total Requests", len(st.session_state.carpool_requests))
    
    st.subheader("Recent Carpool Activity")
    
    # Show recent offers
    recent_offers = sorted(st.session_state.carpool_offers, key=lambda x: x['created_at'], reverse=True)[:5]
    
    if recent_offers:
        for offer in recent_offers:
            if offer['status'] == 'active' and len(offer['passengers']) < offer['seats_available']:
                driver_rating = st.session_state.users.get(offer['driver'], {}).get('rating', 5.0)
                st.markdown(f"""
                <div class="carpool-card">
                    <strong>{offer['driver']}</strong> ⭐ {driver_rating:.1f} is offering a ride<br>
                    <strong>Route:</strong> {offer['start_location']} → {offer['end_location']}<br>
                    <strong>When:</strong> {offer['departure_time']}<br>
                    <strong>Seats:</strong> {offer['seats_available'] - len(offer['passengers'])} available<br>
                    <strong>Price:</strong> ${offer['price_per_seat']:.2f}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No recent carpool activity to display.")
    
    st.subheader("Top Rated Drivers")
    if st.session_state.users:
        drivers_with_cars = [(username, data) for username, data in st.session_state.users.items() if data.get('car_info')]
        sorted_drivers = sorted(drivers_with_cars, key=lambda x: x[1]['rating'], reverse=True)[:5]
        
        for username, data in sorted_drivers:
            st.markdown(f"""
            <div class="user-card">
                <strong>{username}</strong> ⭐ {data['rating']:.1f}<br>
                <strong>Car:</strong> {data['car_info']['make_model']} ({data['car_info']['year']})<br>
                <strong>Trips:</strong> {data['trips_completed']} completed
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("**MobiSync** - Smart Transportation for Everyone 🚗🌱")
st.markdown("*Save money, reduce emissions, and meet new people through carpooling!*")
