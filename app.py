import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

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

# --- Setup grid ---
volume_values = np.linspace(volume_range[0], volume_range[1], 40)
resistance_values = np.linspace(resistance_range[0], resistance_range[1], 40)

data = {
    "Volume (fl oz)": [],
    "Electrode Resistance (Ω)": [],
    "Time (s)": [],
    "Power (W)": [],
    "Time Category": [],
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

        # Categorize
        if time <= time_thresholds[0]:
            category = f"Fast (≤ {time_thresholds[0]:.1f}s)"
        elif time <= time_thresholds[1]:
            category = f"Moderate ({time_thresholds[0]:.1f}–{time_thresholds[1]:.1f}s)"
        else:
            category = f"Slow (> {time_thresholds[1]:.1f}s)"

        data["Volume (fl oz)"].append(floz)
        data["Electrode Resistance (Ω)"].append(R)
        data["Time (s)"].append(time)
        data["Power (W)"].append(power)
        data["Time Category"].append(category)

df = pd.DataFrame(data)

# --- Scatter Plot ---
fig = px.scatter(
    df,
    x="Volume (fl oz)",
    y="Electrode Resistance (Ω)",
    color="Time Category",
    hover_data={
        "Time Category": False,
        "Time (s)": ':.1f',
        "Power (W)": ':.1f',
        "Volume (fl oz)": ':.2f',
        "Electrode Resistance (Ω)": ':.2f',
    },
    size_max=10,
    title="HOCl Generation Time by Volume and Resistance",
    color_discrete_map={
        f"Fast (≤ {time_thresholds[0]:.1f}s)": "green",
        f"Moderate ({time_thresholds[0]:.1f}–{time_thresholds[1]:.1f}s)": "orange",
        f"Slow (> {time_thresholds[1]:.1f}s)": "red",
    },
)

fig.update_traces(marker=dict(size=8, line=dict(width=1, color="DarkSlateGrey")))
fig.update_traces(hoverlabel=dict(font=dict(size=20)))
fig.update_layout(height=600)

st.plotly_chart(fig, use_container_width=True)

