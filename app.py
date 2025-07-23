import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Constants
F = 96485  # Faraday's constant, C/mol
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

# --- Setup axes ---
volume_values = np.linspace(volume_range[0], volume_range[1], 50)
resistance_values = np.linspace(resistance_range[0], resistance_range[1], 50)

Z = np.zeros((len(resistance_values), len(volume_values)))  # Time values

# --- Compute time grid ---
for i, R in enumerate(resistance_values):
    for j, floz in enumerate(volume_values):
        liters = floz * FLOZ_TO_LITERS
        grams = (target_ppm * liters) / 1000
        mols = grams / MOLAR_MASS_HOCL
        charge = (mols * ELECTRONS_PER_HOCL * F) / faradaic_eff
        current = voltage / R
        time = charge / current  # in seconds
        Z[i, j] = time

# --- Plot ---
fig, ax = plt.subplots(figsize=(8, 5))

# Mask for color bands
cmap = plt.cm.get_cmap('RdYlGn_r')  # Green = fast, Red = slow
bounds = [0, 2, 5, Z.max()]
norm = plt.matplotlib.colors.BoundaryNorm(bounds, cmap.N)

im = ax.imshow(Z, aspect='auto', cmap=cmap, norm=norm,
               extent=[volume_values[0], volume_values[-1], resistance_values[-1], resistance_values[0]])

cbar = fig.colorbar(im, ax=ax, orientation='vertical')
cbar.set_label("Time to Generate Target HOCl (s)")

ax.set_xlabel("Volume (fl. oz)")
ax.set_ylabel("Electrode Resistance (Ω)")
ax.set_title("HOCl Generation Time")

st.pyplot(fig)

