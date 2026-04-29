import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(page_title="Pile Foundation Designer", layout="wide")

# --- Custom CSS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e7d32, #1b5e20); color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.title("🏗️ Pile Group Analysis Tool")
st.subheader("Geotechnical Engineering Design for Eccentric Loading")

with st.sidebar:
    st.header("1. Input Parameters")
    
    st.subheader("Loads (Working Load)")
    p_load = st.number_input("Vertical Load (P), kN", value=1200.0)
    mx_load = st.number_input("Moment Mx, kN-m", value=150.0)
    my_load = st.number_input("Moment My, kN-m", value=80.0)
    
    st.divider()
    
    st.subheader("Pile Configuration")
    pile_capacity = st.number_input("Pile Safe Capacity, kN", value=500.0)
    num_piles = st.number_input("Number of Piles", min_value=1, value=4)
    
    st.info("ระบุตำแหน่งเสาเข็ม (x, y) เทียบกับจุด Center ของตอม่อ")
    piles_data = []
    for i in range(num_piles):
        col1, col2 = st.columns(2)
        with col1:
            x = st.number_input(f"Pile {i+1} X (m)", value=float((i % 2) * 2 - 1), key=f"x{i}")
        with col2:
            y = st.number_input(f"Pile {i+1} Y (m)", value=float((i // 2) * 2 - 1), key=f"y{i}")
        piles_data.append([x, y])

# --- Calculation Logic ---
df = pd.DataFrame(piles_data, columns=['x', 'y'])

# 1. Centroid calculation
cx = df['x'].mean()
cy = df['y'].mean()

# 2. Coordinates relative to centroid
df['dx'] = df['x'] - cx
df['dy'] = df['y'] - cy

# 3. Moment of Inertia of pile group
sum_x2 = (df['dx']**2).sum()
sum_y2 = (df['dy']**2).sum()

# 4. Individual Pile Reaction
# Q = P/n + (Mx*y / sum_y2) + (My*x / sum_x2)
df['Reaction'] = (p_load / num_piles) + (mx_load * df['dy'] / sum_y2) + (my_load * df['dx'] / sum_x2)

# --- Visualizations ---
col_main, col_res = st.columns([2, 1])

with col_main:
    st.subheader("Pile Layout & Stress Heatmap")
    
    fig = go.Figure()
    
    # Add Piles
    fig.add_trace(go.Scatter(
        x=df['x'], y=df['y'],
        mode='markers+text',
        marker=dict(size=df['Reaction']/df['Reaction'].max()*40, 
                    color=df['Reaction'], 
                    colorscale='Viridis', 
                    showscale=True,
                    colorbar=dict(title="Reaction (kN)")),
        text=df.index + 1,
        textposition="top center",
        name="Piles"
    ))
    
    # Add Centroid
    fig.add_trace(go.Scatter(x=[cx], y=[cy], mode='markers', 
                             marker=dict(symbol='x', size=12, color='red'),
                             name="Centroid"))

    fig.update_layout(
        xaxis_title="X-axis (m)",
        yaxis_title="Y-axis (m)",
        height=600,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

with col_res:
    st.subheader("Summary Results")
    max_reac = df['Reaction'].max()
    min_reac = df['Reaction'].min()
    efficiency = (max_reac / pile_capacity) * 100

    st.metric("Max Pile Reaction", f"{max_reac:.2f} kN")
    st.metric("Min Pile Reaction", f"{min_reac:.2f} kN")
    
    status_color = "green" if max_reac <= pile_capacity else "red"
    st.markdown(f"### Utilization: <span style='color:{status_color}'>{efficiency:.2f}%</span>", unsafe_allow_html=True)
    
    if max_reac > pile_capacity:
        st.error("⚠️ Overloaded! เสาเข็มรับน้ำหนักเกินกำลัง")
    else:
        st.success("✅ Design Safe! กำลังเสาเข็มเพียงพอ")

# --- Table Details ---
st.divider()
st.subheader("Detailed Calculation Table")
st.dataframe(df.style.background_gradient(subset=['Reaction'], cmap='YlOrRd'), use_container_width=True)
