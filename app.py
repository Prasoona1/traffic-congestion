import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="MobiSync - Smart Route Optimization",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for attractive styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .route-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .route-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    .savings-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1rem;
    }
    .reward-badge {
        background: linear-gradient(45deg, #FFA726, #FF7043);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        display: inline-block;
        margin: 0.2rem;
        font-weight: bold;
    }
    .eco-points {
        background: linear-gradient(45deg, #66BB6A, #43A047);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for user data
if 'eco_points' not in st.session_state:
    st.session_state.eco_points = 1250
if 'total_savings' not in st.session_state:
    st.session_state.total_savings = {
        'fuel': 45.2,
        'money': 180.50,
        'co2': 105.8,
        'time': 420
    }
if 'trips_completed' not in st.session_state:
    st.session_state.trips_completed = 73

# Header
st.markdown("""
<div class="main-header">
    <h1>🚗 MobiSync Route Optimizer</h1>
    <p>Save Fuel • Save Money • Save the Planet • Earn Rewards</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for user profile and achievements
with st.sidebar:
    st.markdown("### 👤 Your Profile")
    
    # User level and points
    st.markdown(f"""
    <div class="eco-points">
        🏆 Eco Warrior Level<br>
        {st.session_state.eco_points} Points
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎖️ Achievements")
    achievements = [
        {"name": "Fuel Saver", "icon": "⛽", "unlocked": True},
        {"name": "Eco Champion", "icon": "🌱", "unlocked": True},
        {"name": "Time Master", "icon": "⏰", "unlocked": True},
        {"name": "Green Warrior", "icon": "🏆", "unlocked": True},
        {"name": "Planet Protector", "icon": "🌍", "unlocked": st.session_state.eco_points >= 2000}
    ]
    
    for achievement in achievements:
        if achievement["unlocked"]:
            st.markdown(f"""
            <div class="reward-badge">
                {achievement['icon']} {achievement['name']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"🔒 {achievement['name']} (Need 2000+ points)")
    
    st.markdown("### 📊 Quick Stats")
    st.metric("Trips Completed", st.session_state.trips_completed)
    st.metric("Trees Saved", f"{int(st.session_state.total_savings['co2'] / 22)}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 🗺️ Plan Your Smart Route")
    
    # Route input form
    with st.form("route_form"):
        col_from, col_to = st.columns(2)
        with col_from:
            start_location = st.text_input("📍 From", value="Downtown Office", placeholder="Enter starting point")
        with col_to:
            end_location = st.text_input("📍 To", value="Shopping Mall", placeholder="Enter destination")
        
        col_time, col_pref = st.columns(2)
        with col_time:
            departure_time = st.selectbox("🕐 Departure", 
                ["Now", "In 15 minutes", "In 30 minutes", "In 1 hour"])
        with col_pref:
            route_preference = st.selectbox("🎯 Optimize for", 
                ["Best Savings", "Fastest Time", "Shortest Distance"])
        
        find_routes = st.form_submit_button("🔍 Find Smart Routes", type="primary")
    
    if find_routes:
        st.markdown("## 🛣️ Route Options")
        
        # Generate sample route data
        routes = [
            {
                "name": "💚 Smart Eco Route",
                "distance": "12.4 km",
                "time": "18 min",
                "fuel": "0.8L",
                "cost": "$3.20",
                "co2": "1.9 kg",
                "savings": {"fuel": 0.3, "money": 1.80, "co2": 0.7, "time": 8},
                "color": "#4CAF50",
                "recommended": True,
                "points": 50
            },
            {
                "name": "⚡ Fast Route",
                "distance": "13.8 km",
                "time": "16 min",
                "fuel": "0.9L",
                "cost": "$3.80",
                "co2": "2.1 kg",
                "savings": {"fuel": 0.2, "money": 1.20, "co2": 0.5, "time": 10},
                "color": "#2196F3",
                "recommended": False,
                "points": 30
            },
            {
                "name": "🛣️ Standard Route",
                "distance": "15.2 km",
                "time": "26 min",
                "fuel": "1.1L",
                "cost": "$5.00",
                "co2": "2.6 kg",
                "savings": {"fuel": 0, "money": 0, "co2": 0, "time": 0},
                "color": "#FF9800",
                "recommended": False,
                "points": 10
            }
        ]
        
        for i, route in enumerate(routes):
            recommended_text = "🌟 RECOMMENDED" if route["recommended"] else ""
            
            st.markdown(f"""
            <div class="route-card" style="border-left-color: {route['color']}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>{route['name']} {recommended_text}</h3>
                    <div style="color: {route['color']}; font-weight: bold;">+{route['points']} points</div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1rem 0;">
                    <div><strong>📏 Distance:</strong><br>{route['distance']}</div>
                    <div><strong>⏱️ Time:</strong><br>{route['time']}</div>
                    <div><strong>⛽ Fuel:</strong><br>{route['fuel']}</div>
                    <div><strong>💰 Cost:</strong><br>{route['cost']}</div>
                </div>
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <strong>💡 You'll Save:</strong> 
                    {route['savings']['fuel']}L fuel • 
                    ${route['savings']['money']} money • 
                    {route['savings']['co2']}kg CO₂ • 
                    {route['savings']['time']} minutes
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🚀 Choose {route['name']}", key=f"route_{i}"):
                # Update user savings and points
                st.session_state.eco_points += route['points']
                st.session_state.total_savings['fuel'] += route['savings']['fuel']
                st.session_state.total_savings['money'] += route['savings']['money']
                st.session_state.total_savings['co2'] += route['savings']['co2']
                st.session_state.total_savings['time'] += route['savings']['time']
                st.session_state.trips_completed += 1
                
                st.success(f"🎉 Route selected! You earned {route['points']} eco points!")
                st.rerun()

with col2:
    st.markdown("## 📈 Your Impact")
    
    # Total savings display
    savings_data = st.session_state.total_savings
    
    st.markdown(f"""
    <div class="savings-card">
        <h3>🌟 Total Savings</h3>
        <div style="font-size: 2rem; margin: 1rem 0;">{savings_data['fuel']:.1f}L</div>
        <div>Fuel Saved</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem; color: #4CAF50; font-weight: bold;">${savings_data['money']:.0f}</div>
            <div>Money Saved</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem; color: #2196F3; font-weight: bold;">{savings_data['co2']:.0f}kg</div>
            <div>CO₂ Reduced</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 1.5rem; color: #FF9800; font-weight: bold;">{savings_data['time']:.0f} min</div>
        <div>Time Saved</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Environmental impact visualization
    st.markdown("### 🌱 Environmental Impact")
    
    # Create a simple chart showing CO2 savings
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = savings_data['co2'],
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "CO₂ Saved (kg)"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 200]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 150], 'color': "lightgreen"},
                {'range': [150, 200], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# Weekly savings chart
st.markdown("## 📊 Weekly Savings Trend")

# Generate sample weekly data
dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
daily_fuel_savings = np.random.uniform(0.5, 2.5, len(dates))
daily_money_savings = daily_fuel_savings * 4.2  # Approximate conversion

df = pd.DataFrame({
    'Date': dates,
    'Fuel Saved (L)': daily_fuel_savings,
    'Money Saved ($)': daily_money_savings
})

fig = px.line(df, x='Date', y=['Fuel Saved (L)', 'Money Saved ($)'], 
              title="Daily Savings Trend",
              color_discrete_sequence=['#4CAF50', '#2196F3'])
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# Rewards section
st.markdown("## 🎁 Redeem Your Rewards")

col1, col2, col3 = st.columns(3)

rewards = [
    {"name": "Free Coffee", "points": 100, "icon": "☕", "available": st.session_state.eco_points >= 100},
    {"name": "Gas Voucher $10", "points": 500, "icon": "⛽", "available": st.session_state.eco_points >= 500},
    {"name": "Plant a Tree", "points": 250, "icon": "🌳", "available": st.session_state.eco_points >= 250},
    {"name": "Eco Car Wash", "points": 300, "icon": "🚗", "available": st.session_state.eco_points >= 300},
    {"name": "Restaurant Discount", "points": 400, "icon": "🍽️", "available": st.session_state.eco_points >= 400},
    {"name": "Movie Tickets", "points": 600, "icon": "🎬", "available": st.session_state.eco_points >= 600}
]

for i, reward in enumerate(rewards):
    if i % 3 == 0:
        col = col1
    elif i % 3 == 1:
        col = col2
    else:
        col = col3
    
    with col:
        if reward["available"]:
            if st.button(f"{reward['icon']} {reward['name']}\n{reward['points']} points", key=f"reward_{i}"):
                st.session_state.eco_points -= reward['points']
                st.success(f"🎉 Redeemed: {reward['name']}!")
                st.balloons()
                st.rerun()
        else:
            st.markdown(f"""
            <div style="opacity: 0.5; text-align: center; padding: 1rem; border: 1px solid #ddd; border-radius: 8px;">
                {reward['icon']}<br>
                {reward['name']}<br>
                <small>{reward['points']} points needed</small>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    🌍 Together we've saved over 10,000L of fuel and prevented 24 tons of CO₂ emissions!<br>
    Keep using smart routes to earn more rewards and help save the planet! 🌱
</div>
""", unsafe_allow_html=True)
