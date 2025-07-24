import streamlit as st
import numpy as np
import pandas as pd
import text
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Constants
F = 96485  # Faraday's constant (C/mol)
MOLAR_MASS_HOCL = 52.46  # g/mol
ELECTRONS_PER_HOCL = 2
FLOZ_TO_LITERS = 0.0295735

st.set_page_config(page_title="HOCl Time Visualizer", layout="centered")
st.title("⏱️ HOCl Generation Time Estimator")

st.markdown("Visualize electrolysis time across fluid volume and electrode resistance.")

# --- Inputs ---
target_ppm = st.slider("Target HOCl Concentration (ppm)", 10, 500, 100, 10, help="Default to 100ppm assumption")
faradaic_eff = st.slider("Faradaic Efficiency (%)", 10, 100, 50, 5, help="50% is a reasonable assumption based on using membrane electrodes, worst case is close to 20% and best case is close to 80%") / 100
voltage = st.slider("Load Voltage (V)", 3.0, 12.0, 7.2, 0.1, help="7.2V is doubling a nominal 1S 3.6V cell")

volume_range = st.slider("Volume (fl oz)", 0.1, 5.0, (0.1, 1.0), 0.1)
resistance_range = st.slider("Electrode Resistance (Ω)", 0.1, 10.0, (1.0, 4.0), 0.1)

time_thresholds = st.slider(
    "Time Category Thresholds (seconds)",
    0.1, 10.0, (2.0, 5.0), 0.1,
    help="Adjust the lower (fast-to-medium) and upper (medium-to-slow) time thresholds."
)

power_thresholds = st.slider(
    "Power Category Thresholds (W)",
    10.0, 100.0, (30.0, 50.0), 1.0,
    help="Adjust the lower (low-to-medium) and upper (medium-to-high) power thresholds."
)

# --- Setup grid ---
volume_values = np.linspace(volume_range[0], volume_range[1], 28)
resistance_values = np.linspace(resistance_range[0], resistance_range[1], 28)

data = {
    "Volume (fl oz)": [],
    "Electrode Resistance (Ω)": [],
    "Time (s)": [],
    "Power (W)": [],
    "Load Current (A)": [],
    "Battery Current (A)": [],
    "Time Category": [],
    "Power Category": [],
}

for R in resistance_values:
    for floz in volume_values:
        liters = floz * FLOZ_TO_LITERS
        grams = (target_ppm * liters) / 1000
        mols = grams / MOLAR_MASS_HOCL
        charge = (mols * ELECTRONS_PER_HOCL * F) / faradaic_eff
        current = voltage / R
        time = charge / current
        power = voltage * current
        battery_current = power / 3.6 / 0.9 # 3.6V battery, 90% efficiency

        # Categorize time
        if time <= time_thresholds[0]:
            time_category = f"Fast (≤ {time_thresholds[0]:.1f}s)"
        elif time <= time_thresholds[1]:
            time_category = f"Moderate ({time_thresholds[0]:.1f}–{time_thresholds[1]:.1f}s)"
        else:
            time_category = f"Slow (> {time_thresholds[1]:.1f}s)"

        # Categorize power
        if power <= power_thresholds[0]:
            power_category = f"Low (≤ {power_thresholds[0]:.1f}W)"
        elif power <= power_thresholds[1]:
            power_category = f"Medium ({power_thresholds[0]:.1f}–{power_thresholds[1]:.1f}W)"
        else:
            power_category = f"High (> {power_thresholds[1]:.1f}W)"

        data["Volume (fl oz)"].append(floz)
        data["Electrode Resistance (Ω)"].append(R)
        data["Time (s)"].append(time)
        data["Power (W)"].append(power)
        data["Load Current (A)"].append(current)
        data["Battery Current (A)"].append(battery_current)
        data["Time Category"].append(time_category)
        data["Power Category"].append(power_category)

df = pd.DataFrame(data)

# --- Create single combined plot ---
fig = go.Figure()

# Define marker shapes for power levels
power_shapes = {
    f"Low (≤ {power_thresholds[0]:.1f}W)": "star",
    f"Medium ({power_thresholds[0]:.1f}–{power_thresholds[1]:.1f}W)": "circle",
    f"High (> {power_thresholds[1]:.1f}W)": "triangle-up"
}

# Define colors for time categories
time_colors = {
    f"Fast (≤ {time_thresholds[0]:.1f}s)": "green",
    f"Moderate ({time_thresholds[0]:.1f}–{time_thresholds[1]:.1f}s)": "orange",
    f"Slow (> {time_thresholds[1]:.1f}s)": "red"
}

# Create traces for each power-time combination
for power_cat in power_shapes.keys():
    for time_cat in time_colors.keys():
        mask = (df["Power Category"] == power_cat) & (df["Time Category"] == time_cat)
        if mask.any():
            fig.add_trace(go.Scatter(
                x=df[mask]["Volume (fl oz)"],
                y=df[mask]["Electrode Resistance (Ω)"],
                mode='markers',
                marker=dict(
                    symbol=power_shapes[power_cat],
                    size=10,
                    color=time_colors[time_cat],
                    line=dict(width=1, color="DarkSlateGrey")
                ),
                name=f"{power_cat} + {time_cat}",
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>" +
                    "Volume: %{x:.2f} fl oz<br>" +
                    "Resistance: %{y:.2f} Ω<br>" +
                    "Time: %{customdata[0]:.1f} s<br>" +
                    "Power: %{customdata[1]:.1f} W<br>" +
                    "Load Current: %{customdata[2]:.2f} A<br>" +
                    "Battery Current: %{customdata[3]:.2f} A<br>" +
                    "<extra></extra>"
                ),
                customdata=np.column_stack((
                    df[mask]["Time (s)"],
                    df[mask]["Power (W)"],
                    df[mask]["Load Current (A)"],
                    df[mask]["Battery Current (A)"]
                )),
                hoverlabel=dict(font=dict(size=16))
            ))

fig.update_layout(
    title="HOCl Generation: Time (Color) and Power (Shape)",
    xaxis_title="Volume (fl oz)",
    yaxis_title="Electrode Resistance (Ω)",
    height=600,
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("View the math behind the calculator"):
    text.make_body()
