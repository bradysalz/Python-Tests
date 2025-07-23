import streamlit as st
import numpy as np
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
target_ppm = st.slider("Target HOCl Concentration (ppm)", 10, 500, 100, 10)
faradaic_eff = st.slider("Faradaic Efficiency (%)", 10, 100, 50, 5) / 100
voltage = st.slider("Load Voltage (V)", 3.0, 12.0, 7.2, 0.1)

volume_range = st.slider("Volume (fluid ounces)", 0.1, 10.0, (0.3, 1.0), 0.1)
resistance_range = st.slider("Electrode Resistance (Ω)", 0.1, 10.0, (1.5, 4.0), 0.1)

# --- Setup grid ---
volume_values = np.linspace(volume_range[0], volume_range[1], 50)
resistance_values = np.linspace(resistance_range[0], resistance_range[1], 50)

data = {
    "Volume (fl oz)": [],
    "Resistance (Ω)": [],
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
        power = voltage**2 / R

        # Categorize by thresholds
        if time <= 2:
            category = "Fast (≤ 2s)"
        elif time <= 5:
            category = "Moderate (2–5s)"
        else:
            category = "Slow (> 5s)"

        data["Volume (fl oz)"].append(floz)
        data["Resistance (Ω)"].append(R)
        data["Time (s)"].append(time)
        data["Power (W)"].append(power)
        data["Time Category"].append(category)

import pandas as pd
df = pd.DataFrame(data)

# --- Plotly chart ---
fig = px.density_heatmap(
    df,
    x="Volume (fl oz)",
    y="Resistance (Ω)",
    z="Time (s)",
    hover_data={"Time (s)": True, "Power (W)": True},
    color_continuous_scale=[
        (0.0, "green"),
        (0.4, "yellow"),
        (1.0, "red"),
    ],
    nbinsx=50,
    nbinsy=50,
    title="HOCl Generation Time Heatmap",
    labels={"z": "Time (s)"},
)

fig.update_layout(
    xaxis_title="Volume (fl oz)",
    yaxis_title="Electrode Resistance (Ω)",
    coloraxis_colorbar=dict(title="Time (s)"),
    height=600,
)

st.plotly_chart(fig, use_container_width=True)

