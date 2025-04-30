import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import folium
from streamlit_folium import folium_static
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# Set page configuration
st.set_page_config(
    page_title="MobiSync Prototype",
    page_icon="🚦",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.title {
    font-size: 2rem;
    font-weight: bold;
    color: #1E88E5;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="title">🚦 MobiSync Platform Prototype</p>', unsafe_allow_html=True)

# -----------------------------
# Data Generation Functions
# -----------------------------

def generate_traffic_data():
    """Generate sample traffic data for demonstration"""
    np.random.seed(42)
    
    # Current time and locations
    now = datetime.datetime.now()
    times = [now - datetime.timedelta(minutes=i*15) for i in range(24)]
    times.reverse()
    
    cities = ["New York", "Los Angeles", "Chicago"]
    roads = ["Main St", "Broadway", "Highway 101"]
    
    data = []
    for time in times:
        hour = time.hour
        # Rush hour factor (8-10am, 4-6pm)
        rush_factor = 2.0 if (8 <= hour <= 10 or 16 <= hour <= 18) else 1.0
        
        for city in cities:
            for road in roads:
                # Generate traffic metrics
                traffic_volume = int(np.random.normal(500, 100) * rush_factor)
                speed = max(5, int(np.random.normal(60, 15) / rush_factor))
                congestion = min(10, max(1, int(np.random.normal(5, 2) * rush_factor)))
                incident = np.random.random() < (0.05 * rush_factor)
                
                data.append({
                    'timestamp': time,
                    'city': city,
                    'road_segment': road,
                    'traffic_volume': traffic_volume,
                    'average_speed': speed,
                    'congestion_level': congestion,
                    'incident_reported': incident
                })
    
    return pd.DataFrame(data)

def generate_predictions(df, hours=2):
    """Generate future traffic predictions"""
    last_time = df['timestamp'].max()
    future_times = [last_time + datetime.timedelta(minutes=i*15) for i in range(1, hours*4+1)]
    
    future_data = []
    for time in future_times:
        hour = time.hour
        rush_factor = 2.0 if (8 <= hour <= 10 or 16 <= hour <= 18) else 1.0
        
        for city in df['city'].unique():
            for road in df['road_segment'].unique():
                # Get recent data for this city/road
                recent = df[(df['city'] == city) & (df['road_segment'] == road)].tail(5)
                
                if not recent.empty:
                    # Base future values on recent trends
                    base_congestion = recent['congestion_level'].mean()
                    congestion = min(10, max(1, base_congestion * rush_factor + np.random.normal(0, 0.5)))
                    
                    future_data.append({
                        'timestamp': time,
                        'city': city,
                        'road_segment': road,
                        'congestion_level': int(congestion),
                        'predicted': True
                    })
    
    return pd.DataFrame(future_data)

def optimize_route(start, end):
    """Generate sample route options"""
    routes = [
        {
            'name': 'Fastest Route',
            'distance_km': np.random.uniform(8, 12),
            'time_min': np.random.uniform(15, 25),
            'congestion': np.random.uniform(0.6, 0.9)
        },
        {
            'name': 'Shortest Route',
            'distance_km': np.random.uniform(5, 9),
            'time_min': np.random.uniform(20, 35),
            'congestion': np.random.uniform(0.7, 1.0)
        },
        {
            'name': 'Eco-Friendly Route',
            'distance_km': np.random.uniform(7, 11),
            'time_min': np.random.uniform(18, 28),
            'congestion': np.random.uniform(0.5, 0.8)
        }
    ]
    return routes

def create_traffic_map(data, city=None):
    """Create a simple traffic map with folium"""
    if city:
        city_data = data[data['city'] == city]
        center = [40.7128, -74.0060]  # Default NYC
    else:
        city_data = data
        center = [40.7128, -74.0060]
    
    # Create map
    m = folium.Map(location=center, zoom_start=12, tiles="CartoDB positron")
    
    # Use latest data
    latest = city_data[city_data['timestamp'] == city_data['timestamp'].max()]
    
    # Add markers
    for _, row in latest.iterrows():
        color = 'green' if row['congestion_level'] <= 3 else 'orange' if row['congestion_level'] <= 6 else 'red'
        
        popup = f"""
        <b>{row['road_segment']}</b><br>
        Congestion: {row['congestion_level']}/10<br>
        Speed: {row.get('average_speed', 'N/A')} mph<br>
        Time: {row['timestamp'].strftime('%H:%M')}
        """
        
        folium.CircleMarker(
            location=center,  # In a real app, use actual coordinates
            radius=10,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=popup
        ).add_to(m)
    
    return m

def train_basic_model(df):
    """Train a basic prediction model"""
    X = df[['traffic_volume', 'average_speed']].copy()
    X['hour'] = df['timestamp'].dt.hour
    X['day_of_week'] = df['timestamp'].dt.dayofweek
    
    y = df['congestion_level']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X_scaled, y)
    
    return model, scaler, X.columns

# -----------------------------
# Main App
# -----------------------------

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Dashboard", "Traffic Visualization", "Congestion Prediction", "Route Optimization"])

# Load data
traffic_data = generate_traffic_data()
predictions = generate_predictions(traffic_data)

# City filter in sidebar
cities = ["All Cities"] + sorted(traffic_data['city'].unique().tolist())
selected_city = st.sidebar.selectbox("Select City", cities)

# Filter data based on city selection
if selected_city != "All Cities":
    display_data = traffic_data[traffic_data['city'] == selected_city]
    display_predictions = predictions[predictions['city'] == selected_city]
else:
    display_data = traffic_data
    display_predictions = predictions

# -----------------------------
# Dashboard Page
# -----------------------------
if page == "Dashboard":
    st.header("Traffic Dashboard")
    
    # KPIs
    latest_data = display_data[display_data['timestamp'] == display_data['timestamp'].max()]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg. Congestion", f"{latest_data['congestion_level'].mean():.1f}/10")
    with col2:
        st.metric("Avg. Speed", f"{latest_data['average_speed'].mean():.1f} mph")
    with col3:
        st.metric("Traffic Volume", f"{int(latest_data['traffic_volume'].sum()):,}")
    with col4:
        st.metric("Incidents", f"{int(latest_data['incident_reported'].sum())}")
    
    # Traffic map
    st.subheader("Current Traffic Map")
    traffic_map = create_traffic_map(latest_data, selected_city if selected_city != "All Cities" else None)
    folium_static(traffic_map, width=700)
    
    # Simple trend chart
    st.subheader("Congestion Trend")
    hourly_data = display_data.groupby(pd.Grouper(key='timestamp', freq='1H')).agg({
        'congestion_level': 'mean'
    }).reset_index()
    
    fig = px.line(
        hourly_data, 
        x='timestamp', 
        y='congestion_level',
        title="Average Congestion Level Over Time",
        labels={'congestion_level': 'Congestion (1-10)', 'timestamp': 'Time'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Raw data
    with st.expander("View Raw Data"):
        st.dataframe(display_data.sort_values('timestamp', ascending=False))

# -----------------------------
# Traffic Visualization Page
# -----------------------------
elif page == "Traffic Visualization":
    st.header("Traffic Visualization")
    
    viz_type = st.radio("Select Visualization", ["Traffic Heatmap", "Congestion Patterns"])
    
    if viz_type == "Traffic Heatmap":
        st.subheader("Congestion Heatmap")
        
        # Create pivot table for heatmap
        pivot = display_data.pivot_table(
            index='road_segment',
            columns=pd.Grouper(key='timestamp', freq='1H'),
            values='congestion_level',
            aggfunc='mean'
        ).fillna(0)
        
        # Plot heatmap
        fig = px.imshow(
            pivot,
            labels=dict(x="Time", y="Road Segment", color="Congestion"),
            x=[col.strftime("%H:%M") for col in pivot.columns],
            y=pivot.index,
            color_continuous_scale="RdYlGn_r"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Congestion Patterns":
        st.subheader("Congestion by Hour")
        
        # Group by hour
        display_data['hour'] = display_data['timestamp'].dt.hour
        hourly = display_data.groupby(['hour', 'road_segment']).agg({
            'congestion_level': 'mean'
        }).reset_index()
        
        # Plot hourly patterns
        fig = px.line(
            hourly,
            x='hour',
            y='congestion_level',
            color='road_segment',
            title="Congestion Patterns by Hour",
            labels={'congestion_level': 'Congestion (1-10)', 'hour': 'Hour of Day'}
        )
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Congestion Prediction Page
# -----------------------------
elif page == "Congestion Prediction":
    st.header("AI-Based Congestion Prediction")
    
    # Train model
    model, scaler, feature_names = train_basic_model(traffic_data)
    
    # Interactive prediction tool
    st.subheader("Predict Congestion")
    
    col1, col2 = st.columns(2)
    with col1:
        volume = st.slider("Traffic Volume", 100, 1000, 500, 50)
        speed = st.slider("Speed (mph)", 5, 70, 35, 5)
    
    with col2:
        hour = st.slider("Hour of Day", 0, 23, 12)
        incident = st.checkbox("Incident Reported", False)
    
    # Prepare input for prediction
    day_of_week = datetime.datetime.now().weekday()
    input_data = pd.DataFrame({
        'traffic_volume': [volume],
        'average_speed': [speed],
        'hour': [hour],
        'day_of_week': [day_of_week]
    })
    
    # Make prediction
    input_scaled = scaler.transform(input_data)
    prediction = model.predict(input_scaled)[0]
    
    # Display prediction
    st.subheader("Predicted Congestion Level")
    st.markdown(f"""
    <div style="text-align:center; font-size:3rem; font-weight:bold; 
                color:{'green' if prediction <= 3 else 'orange' if prediction <= 6 else 'red'}">
        {prediction:.1f}/10
    </div>
    """, unsafe_allow_html=True)
    
    # Interpretation
    if prediction <= 3:
        st.success("Low congestion expected. Traffic flowing freely.")
    elif prediction <= 6:
        st.warning("Moderate congestion. Some slowdowns possible.")
    else:
        st.error("Heavy congestion expected. Significant delays likely.")
    
    # Future predictions chart
    st.subheader("Future Congestion Forecast")
    
    forecast_hours = st.slider("Forecast Hours", 1, 6, 2)
    future_preds = generate_predictions(traffic_data, forecast_hours)
    
    if selected_city != "All Cities":
        future_preds = future_preds[future_preds['city'] == selected_city]
    
    # Group by time
    future_agg = future_preds.groupby('timestamp').agg({
        'congestion_level': 'mean'
    }).reset_index()
    
    # Plot forecast
    fig = px.line(
        future_agg,
        x='timestamp',
        y='congestion_level',
        title="Predicted Average Congestion Level",
        labels={'congestion_level': 'Congestion (1-10)', 'timestamp': 'Time'}
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Route Optimization Page
# -----------------------------
elif page == "Route Optimization":
    st.header("Smart Route Optimization")
    
    st.subheader("Route Planner")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Starting Point**")
        start_location = st.text_input("Enter start location", "City Center")
    
    with col2:
        st.markdown("**Destination**")
        end_location = st.text_input("Enter destination", "Airport")
    
    # Route preferences
    avoid_tolls = st.checkbox("Avoid toll roads", False)
    avoid_highways = st.checkbox("Avoid highways", False)
    
    # Generate routes on button click
    if st.button("Find Routes"):
        st.subheader("Route Options")
        
        # Generate sample routes
        routes = optimize_route(start_location, end_location)
        
        # Display routes in table
        route_data = []
        for route in routes:
            route_data.append({
                "Route": route['name'],
                "Distance (km)": f"{route['distance_km']:.1f}",
                "Est. Time (min)": f"{route['time_min']:.1f}",
                "Congestion": f"{int(route['congestion']*100)}%"
            })
        
        route_df = pd.DataFrame(route_data)
        st.table(route_df)
        
        # Show recommended route
        st.subheader("Recommended Route")
        
        # Simple recommendation logic
        if avoid_highways and avoid_tolls:
            best_route = routes[1]  # Shortest
        else:
            best_route = routes[0]  # Fastest
        
        st.success(f"""
        **{best_route['name']}**
        * Distance: {best_route['distance_km']:.1f} km
        * Estimated Time: {best_route['time_min']:.1f} minutes
        * Congestion Level: {int(best_route['congestion']*100)}%
        """)
        
        # Future improvement notes
        st.info("In a production app, this would show an interactive map with the routes.")
