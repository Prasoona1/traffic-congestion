import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

# Configure page
st.set_page_config(
    page_title="Smart Transportation App",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'routes_data' not in st.session_state:
    st.session_state.routes_data = []
if 'journey_active' not in st.session_state:
    st.session_state.journey_active = False
if 'sustainability_points' not in st.session_state:
    st.session_state.sustainability_points = 0

# Mock data for demonstrations
mock_routes = [
    {
        'mode': 'Driving', 'time': 25, 'cost': 8.50, 'co2': 4.2, 
        'icon': '🚗', 'description': 'Direct route via Highway 101'
    },
    {
        'mode': 'Carpool', 'time': 32, 'cost': 3.20, 'co2': 1.4, 
        'icon': '👥', 'description': 'Share with 2 others, pickup nearby'
    },
    {
        'mode': 'Public Transit', 'time': 45, 'cost': 4.00, 'co2': 0.8, 
        'icon': '🚌', 'description': 'Bus + Light Rail combination'
    },
    {
        'mode': 'Bike', 'time': 35, 'cost': 0.00, 'co2': 0.0, 
        'icon': '🚲', 'description': 'Bike lanes available, slight uphill'
    }
]

carpool_matches = [
    {'name': 'Sarah M.', 'rating': 4.8, 'trips': 127, 'time': '8:15 AM', 'car': 'Toyota Prius'},
    {'name': 'Mike R.', 'rating': 4.9, 'trips': 89, 'time': '8:20 AM', 'car': 'Honda Civic'},
    {'name': 'Lisa K.', 'rating': 4.7, 'trips': 203, 'time': '8:10 AM', 'car': 'Tesla Model 3'}
]

# Sidebar navigation
st.sidebar.title("🚗 Smart Transport")
st.sidebar.markdown("---")

step_names = [
    "1. 👤 User Onboarding",
    "2. 🗺️ Route Analysis", 
    "3. 🌅 Morning Planning",
    "4. 👥 Carpool Matching",
    "5. 🛣️ Journey Monitoring",
    "6. 💳 Payment Processing",
    "7. 🌱 Sustainability Tracking",
    "8. 🤖 AI Learning"
]

selected_step = st.sidebar.selectbox("Navigate to Step:", step_names, index=st.session_state.step-1)
st.session_state.step = step_names.index(selected_step) + 1

# Progress bar
progress = st.session_state.step / 8
st.sidebar.progress(progress)
st.sidebar.write(f"Progress: {progress:.0%}")

# Main content based on current step
st.title("Smart Transportation Assistant")

if st.session_state.step == 1:
    st.header("Step 1: User Onboarding and Profile Creation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Account Registration")
        email = st.text_input("Email Address", placeholder="your.email@example.com")
        phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
        
        if st.button("Send Verification"):
            st.success("✅ Verification code sent!")
            
        verification_code = st.text_input("Verification Code", placeholder="Enter 6-digit code")
    
    with col2:
        st.subheader("Personal Details")
        name = st.text_input("Full Name", placeholder="John Doe")
        age = st.slider("Age", 18, 80, 30)
        
        st.subheader("Transportation Preferences")
        cost_priority = st.slider("Cost Priority", 0, 100, 50)
        time_priority = st.slider("Time Priority", 0, 100, 30)
        env_priority = st.slider("Environmental Priority", 0, 100, 20)
    
    st.subheader("Primary Locations")
    home_address = st.text_input("🏠 Home Address", placeholder="123 Main St, City, State")
    work_address = st.text_input("🏢 Work Address", placeholder="456 Business Ave, City, State")
    
    st.subheader("Preferred Transport Modes")
    transport_modes = st.multiselect(
        "Select your preferred transportation methods:",
        ["Driving", "Carpool", "Public Transit", "Walking", "Biking", "Ride-share"]
    )
    
    if st.button("Complete Profile Setup", type="primary"):
        st.session_state.user_profile = {
            'name': name, 'email': email, 'phone': phone,
            'preferences': {'cost': cost_priority, 'time': time_priority, 'environment': env_priority},
            'locations': {'home': home_address, 'work': work_address},
            'transport_modes': transport_modes
        }
        st.success("🎉 Profile created successfully!")
        st.balloons()

elif st.session_state.step == 2:
    st.header("Step 2: Initial Route Analysis and Learning")
    
    if st.session_state.user_profile:
        st.info(f"Welcome back, {st.session_state.user_profile.get('name', 'User')}!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🗺️ Route Discovery")
            st.write("Analyzing transportation options...")
            
            # Simulate route analysis
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            if st.button("Start Route Analysis"):
                for i in range(101):
                    progress_bar.progress(i)
                    if i < 25:
                        status_text.text("🚗 Analyzing driving routes...")
                    elif i < 50:
                        status_text.text("🚌 Checking public transit...")
                    elif i < 75:
                        status_text.text("👥 Finding carpool options...")
                    else:
                        status_text.text("🚲 Mapping bike paths...")
                    time.sleep(0.02)
                status_text.text("✅ Analysis complete!")
                
                # Store route data
                st.session_state.routes_data = mock_routes
        
        with col2:
            st.subheader("📊 Discovered Routes")
            if st.session_state.routes_data:
                for route in st.session_state.routes_data:
                    with st.expander(f"{route['icon']} {route['mode']} - {route['time']} min"):
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Time", f"{route['time']} min")
                        with col_b:
                            st.metric("Cost", f"${route['cost']:.2f}")
                        with col_c:
                            st.metric("CO2", f"{route['co2']} kg")
                        st.write(route['description'])
    else:
        st.warning("Please complete Step 1: User Onboarding first")

elif st.session_state.step == 3:
    st.header("Step 3: Smart Morning Planning and Recommendations")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🌅 Today's Commute Recommendations")
        
        # Current conditions
        st.write("**Current Conditions:**")
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("Weather", "☀️ Sunny", "72°F")
        with col_b:
            st.metric("Traffic", "🟡 Moderate", "+5 min")
        with col_c:
            st.metric("Transit", "🟢 On Time", "Normal")
        with col_d:
            st.metric("Air Quality", "🟢 Good", "AQI 45")
        
        st.subheader("📱 Route Recommendations")
        
        # Create interactive route comparison
        if st.session_state.routes_data:
            df_routes = pd.DataFrame(st.session_state.routes_data)
            
            # Add recommended badge based on user preferences
            if st.session_state.user_profile:
                prefs = st.session_state.user_profile['preferences']
                # Simple scoring algorithm
                df_routes['score'] = (
                    (100 - df_routes['time']) * prefs['time']/100 +
                    (100 - df_routes['cost']*10) * prefs['cost']/100 +
                    (100 - df_routes['co2']*20) * prefs['environment']/100
                )
                df_routes = df_routes.sort_values('score', ascending=False)
            
            for idx, route in df_routes.iterrows():
                is_recommended = idx == df_routes.index[0] if st.session_state.user_profile else False
                
                with st.container():
                    if is_recommended:
                        st.success("⭐ RECOMMENDED")
                    
                    col_route1, col_route2, col_route3, col_route4, col_route5 = st.columns([1, 2, 1, 1, 1])
                    
                    with col_route1:
                        st.write(f"## {route['icon']}")
                    with col_route2:
                        st.write(f"**{route['mode']}**")
                        st.caption(route['description'])
                    with col_route3:
                        st.write(f"⏱️ {route['time']} min")
                    with col_route4:
                        st.write(f"💰 ${route['cost']:.2f}")
                    with col_route5:
                        st.write(f"🌱 {route['co2']} kg CO2")
                    
                    if st.button(f"Select {route['mode']}", key=f"select_{idx}"):
                        st.session_state.selected_route = route
                        st.success(f"✅ {route['mode']} selected!")
                
                st.divider()
    
    with col2:
        st.subheader("📅 Smart Departure")
        
        departure_time = st.time_input("Desired Arrival Time", value=datetime.strptime("09:00", "%H:%M").time())
        
        # Calculate suggested departure times
        st.write("**Suggested Departure Times:**")
        for route in mock_routes[:3]:
            arrival_time = datetime.combine(datetime.today(), departure_time)
            depart_time = arrival_time - timedelta(minutes=route['time'])
            st.write(f"{route['icon']} {depart_time.strftime('%H:%M')} - {route['mode']}")
        
        st.subheader("📱 Notifications")
        notify_traffic = st.checkbox("Traffic alerts", value=True)
        notify_weather = st.checkbox("Weather updates", value=True)
        notify_carpool = st.checkbox("Carpool matches", value=True)

elif st.session_state.step == 4:
    st.header("Step 4: Carpool Matching and Coordination")
    
    st.subheader("🔍 Finding Carpool Matches...")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Matching criteria
        st.write("**Matching Criteria:**")
        col_a, col_b = st.columns(2)
        with col_a:
            max_detour = st.slider("Max detour (minutes)", 0, 15, 5)
            time_flexibility = st.slider("Time flexibility (minutes)", 0, 30, 10)
        with col_b:
            gender_pref = st.selectbox("Gender preference", ["No preference", "Same gender", "Any"])
            smoking_pref = st.selectbox("Smoking preference", ["Non-smoking only", "No preference"])
        
        st.subheader("👥 Available Matches")
        
        for idx, match in enumerate(carpool_matches):
            with st.container():
                col_match1, col_match2, col_match3, col_match4 = st.columns([1, 3, 2, 1])
                
                with col_match1:
                    st.write("👤")
                
                with col_match2:
                    st.write(f"**{match['name']}**")
                    st.write(f"⭐ {match['rating']}/5.0 ({match['trips']} trips)")
                    st.write(f"🚗 {match['car']}")
                
                with col_match3:
                    st.write(f"🕐 Departure: {match['time']}")
                    st.write("📍 0.3 miles from you")
                    st.write("💰 $3.20 per trip")
                
                with col_match4:
                    if st.button("Connect", key=f"connect_{idx}"):
                        st.success(f"✅ Request sent to {match['name']}!")
                        st.info("💬 You can now chat with your carpool partner")
                
                st.divider()
    
    with col2:
        st.subheader("💬 Carpool Chat")
        
        if st.button("Demo Chat"):
            st.chat_message("user").write("Hi! I saw we're matched for tomorrow's commute.")
            st.chat_message("assistant").write("Great! I usually leave at 8:15 AM. Does that work for you?")
            st.chat_message("user").write("Perfect! Where should we meet?")
            st.chat_message("assistant").write("How about the Starbucks on Main St? It's easy to spot.")
        
        st.subheader("🛡️ Safety Features")
        st.write("✅ Background check verified")
        st.write("✅ Phone number verified")
        st.write("✅ Real-time GPS tracking")
        st.write("✅ Emergency contact system")
        st.write("✅ Rating system")

elif st.session_state.step == 5:
    st.header("Step 5: Real-Time Journey Monitoring and Adaptation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🛣️ Live Journey Tracking")
        
        # Journey status
        if not st.session_state.journey_active:
            if st.button("🚀 Start Journey", type="primary"):
                st.session_state.journey_active = True
                st.rerun()
        else:
            st.success("🚗 Journey in progress...")
            
            # Create a mock real-time map
            map_data = pd.DataFrame({
                'lat': [37.7749 + i*0.01 for i in range(10)],
                'lon': [-122.4194 + i*0.01 for i in range(10)]
            })
            
            st.map(map_data)
            
            # Journey metrics
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("Progress", "65%", "2 miles")
            with col_b:
                st.metric("ETA", "8:47 AM", "-3 min")
            with col_c:
                st.metric("Speed", "35 mph", "+5 mph")
            with col_d:
                st.metric("Fuel Saved", "$2.10", "+15%")
            
            # Real-time alerts
            st.subheader("⚠️ Live Updates")
            st.warning("🚧 Construction ahead - Alternate route suggested")
            st.info("🌧️ Light rain expected in 10 minutes")
            st.success("👥 Carpool partner picked up successfully")
            
            # Rerouting options
            st.subheader("🔄 Route Adjustments")
            col_route1, col_route2 = st.columns(2)
            with col_route1:
                st.write("**Current Route:** Highway 101")
                st.write("⏱️ 12 min remaining")
                st.write("🚧 Heavy traffic ahead")
            with col_route2:
                st.write("**Suggested Route:** Side streets")
                st.write("⏱️ 10 min remaining")
                st.write("✅ Clear traffic")
                if st.button("Accept New Route"):
                    st.success("🔄 Route updated!")
            
            if st.button("🏁 Complete Journey"):
                st.session_state.journey_active = False
                st.session_state.sustainability_points += 25
                st.success("🎉 Journey completed successfully!")
                st.balloons()
                st.rerun()
    
    with col2:
        st.subheader("📊 Journey Analytics")
        
        # Real-time charts
        time_data = pd.DataFrame({
            'Time': pd.date_range('8:00', periods=30, freq='1min'),
            'Speed': np.random.normal(30, 10, 30).clip(0, 60)
        })
        
        fig = px.line(time_data, x='Time', y='Speed', title='Speed Over Time')
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🎯 Trip Efficiency")
        st.metric("Time vs Predicted", "On time", "3 min early")
        st.metric("Cost vs Budget", "$3.20", "Under budget")
        st.metric("CO2 Saved", "2.8 kg", "vs driving alone")

elif st.session_state.step == 6:
    st.header("Step 6: Payment Processing and Cost Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💳 Payment Dashboard")
        
        # Payment methods
        st.write("**Payment Methods:**")
        payment_method = st.radio(
            "Select payment method:",
            ["💳 Credit Card ****1234", "📱 Digital Wallet", "🏦 Bank Account", "💰 Transport Credits"]
        )
        
        # Current trip cost
        st.subheader("🧾 Current Trip")
        trip_cost = 3.20
        st.write(f"**Carpool with Sarah M.**")
        col_cost1, col_cost2 = st.columns(2)
        with col_cost1:
            st.write("Base fare: $6.40")
            st.write("Split 2 ways: $3.20")
            st.write("Platform fee: $0.30")
        with col_cost2:
            st.write("Discount: -$0.50")
            st.write("**Total: $3.00**")
        
        if st.button("💰 Process Payment", type="primary"):
            st.success("✅ Payment processed successfully!")
            st.info("💸 $3.00 charged to your credit card")
            
        # Auto-pay settings
        st.subheader("⚙️ Auto-Pay Settings")
        auto_pay = st.checkbox("Enable automatic payments", value=True)
        spending_limit = st.slider("Daily spending limit", 0, 50, 20)
        
    with col2:
        st.subheader("📊 Spending Analytics")
        
        # Monthly spending chart
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        spending = [45, 52, 38, 41, 47]
        
        fig = go.Figure(data=go.Bar(x=months, y=spending))
        fig.update_layout(title="Monthly Transportation Spending", yaxis_title="Amount ($)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Cost breakdown
        st.subheader("💰 Cost Breakdown (This Month)")
        cost_data = pd.DataFrame({
            'Category': ['Carpool', 'Public Transit', 'Bike Share', 'Parking'],
            'Amount': [28, 12, 3, 4],
            'Trips': [8, 6, 2, 3]
        })
        
        col_breakdown1, col_breakdown2 = st.columns(2)
        with col_breakdown1:
            fig_pie = px.pie(cost_data, values='Amount', names='Category', title='Spending by Category')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_breakdown2:
            st.dataframe(cost_data, use_container_width=True)
        
        # Savings summary
        st.subheader("💡 Savings Summary")
        st.metric("vs. Driving Alone", "$127", "This month")
        st.metric("vs. Taxi/Rideshare", "$234", "This month")
        st.metric("Total Saved (2024)", "$1,456", "+$234 this month")

elif st.session_state.step == 7:
    st.header("Step 7: Sustainability Tracking and Rewards")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌱 Environmental Impact")
        
        # Sustainability metrics
        col_env1, col_env2, col_env3 = st.columns(3)
        with col_env1:
            st.metric("CO2 Saved", "45.2 kg", "This month")
        with col_env2:
            st.metric("Fuel Saved", "18.3 gal", "This month")
        with col_env3:
            st.metric("Trees Equivalent", "2.1 trees", "Planted")
        
        # Carbon footprint chart
        st.subheader("📈 Carbon Footprint Trend")
        dates = pd.date_range('2024-01-01', periods=12, freq='M')
        co2_saved = np.random.normal(40, 10, 12).clip(20, 60)
        
        fig = px.line(x=dates, y=co2_saved, title='Monthly CO2 Savings (kg)')
        fig.update_xaxis(title='Month')
        fig.update_yaxis(title='CO2 Saved (kg)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Transport mode comparison
        st.subheader("🚗 Transport Mode Impact")
        mode_data = pd.DataFrame({
            'Mode': ['Carpool', 'Public Transit', 'Biking', 'Walking'],
            'CO2 per Trip (kg)': [1.4, 0.8, 0.0, 0.0],
            'Trips This Month': [12, 8, 5, 3]
        })
        
        fig = px.bar(mode_data, x='Mode', y='CO2 per Trip (kg)', 
                     color='Trips This Month', title='CO2 Impact by Transport Mode')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Rewards & Achievements")
        
        # Points summary
        points = st.session_state.sustainability_points + 450
        st.metric("🎯 EcoPoints", f"{points:,}", "+25 today")
        
        # Achievement badges
        st.write("**🏅 Recent Achievements:**")
        achievements = [
            {"badge": "🌟", "title": "Eco Warrior", "desc": "Saved 50kg CO2 this month"},
            {"badge": "🚌", "title": "Transit Champion", "desc": "Used public transport 10 times"},
            {"badge": "👥", "title": "Carpool Hero", "desc": "Completed 15 carpools"},
            {"badge": "🚲", "title": "Bike Enthusiast", "desc": "Biked 50 miles total"}
        ]
        
        for achievement in achievements:
            with st.container():
                col_ach1, col_ach2 = st.columns([1, 4])
                with col_ach1:
                    st.write(f"## {achievement['badge']}")
                with col_ach2:
                    st.write(f"**{achievement['title']}**")
                    st.caption(achievement['desc'])
                st.divider()
        
        # Rewards redemption
        st.subheader("🎁 Redeem Rewards")
        rewards = [
            {"name": "Coffee Voucher", "points": 100, "desc": "Free coffee at local cafes"},
            {"name": "Transit Pass", "points": 250, "desc": "$10 public transit credit"},
            {"name": "Bike Tune-up", "points": 300, "desc": "Free bike maintenance"},
            {"name": "Car Wash", "points": 200, "desc": "Premium car wash service"}
        ]
        
        for reward in rewards:
            col_rew1, col_rew2, col_rew3 = st.columns([3, 1, 1])
            with col_rew1:
                st.write(f"**{reward['name']}**")
                st.caption(reward['desc'])
            with col_rew2:
                st.write(f"{reward['points']} pts")
            with col_rew3:
                can_redeem = points >= reward['points']
                if st.button("Redeem" if can_redeem else "Need more", 
                           key=f"redeem_{reward['name']}", 
                           disabled=not can_redeem):
                    st.success(f"🎉 {reward['name']} redeemed!")
                    st.session_state.sustainability_points -= reward['points']
        
        # Leaderboard
        st.subheader("🏆 Monthly Leaderboard")
        leaderboard = pd.DataFrame({
            'Rank': [1, 2, 3, 4, 5],
            'User': ['You', 'Alex K.', 'Maria S.', 'John D.', 'Lisa M.'],
            'Points': [points, 445, 387, 356, 334]
        })
        st.dataframe(leaderboard, use_container_width=True)

elif st.session_state.step == 8:
    st.header("Step 8: AI Learning and Continuous Improvement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🤖 AI Personal Assistant")
        
        st.write("**Learning from your behavior patterns:**")
        
        # User behavior analysis
        behavior_insights = [
            "🕐 You prefer leaving 10 minutes early for important meetings",
            "🌧️ You choose carpool over biking when rain probability > 30%",
            "💰 Cost becomes priority factor when monthly spending exceeds $40",
            "🚌 You're 85% likely to take public transit on Fridays",
            "👥 You prefer carpooling with users rated 4.5+ stars"
        ]
        
        for insight in behavior_insights:
            st.info(insight)
        
        # Predictive recommendations
        st.subheader("🔮 Predictive Insights")
        st.write("**Tomorrow's Recommendations:**")
        
        predictions = [
            {"condition": "Heavy rain expected", "recommendation": "Suggest carpool over biking", "confidence": "94%"},
            {"condition": "Traffic 15% heavier than usual", "recommendation": "Leave 8 minutes earlier", "confidence": "87%"},
            {"condition": "Sarah M. available for carpool", "recommendation": "Match with preferred partner", "confidence": "96%"},
            {"condition": "Friday afternoon pattern", "recommendation": "Public transit for return trip", "confidence": "85%"}
        ]
        
        for pred in predictions:
            with st.expander(f"📊 {pred['condition']} ({pred['confidence']} confidence)"):
                st.write(f"**Recommendation:** {pred['recommendation']}")
                st.progress(int(pred['confidence'][:-1])/100)
    
    with col2:
        st.subheader("📊 ML Model Performance")
        
        # Model accuracy metrics
        col_model1, col_model2 = st.columns(2)
        with col_model1:
            st.metric("Route Prediction", "92%", "+3%")
            st.metric("Time Estimation", "87%", "+1%")
        with col_model2:
            st.metric("Carpool Matching", "89%", "+5%")
            st.metric("Cost Optimization", "94%", "+2%")
        
        # Learning progress chart
        st.subheader("📈 AI Learning Progress")
        weeks = list(range(1, 13))
        accuracy = [75, 78, 82, 85, 87, 89, 90, 91, 92, 92, 93, 94]
        
        fig = px.line(x=weeks, y=accuracy, title='Model Accuracy Over Time (%)')
        fig.update_xaxis(title='Weeks')
        fig.update_yaxis(title='Accuracy (%)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Data collection summary
        st.subheader("📊 Data Collection Summary")
        data_stats = pd.DataFrame({
            'Data Type': ['Trip Routes', 'Time Preferences', 'Cost Patterns', 'Weather Correlations', 'Traffic Patterns'],
            'Data Points': [1247, 892, 756, 423, 1156],
            'Quality Score': [96, 94, 91, 89, 93]
        })
        
        st.dataframe(data_stats, use_container_width=True)
        
        # Privacy controls
        st.subheader("🔒 Privacy & Data Control")
        data_sharing = st.checkbox("Share anonymized data for city planning", value=True)
        location_tracking = st.selectbox("Location tracking",
